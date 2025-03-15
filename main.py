import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List, Any, Dict, Literal, Annotated

# -------------------- LangChain, LangGraph, and Other Imports -------------------- #
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.runnables import RunnableLambda, RunnableWithFallbacks
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from typing_extensions import TypedDict

# Load environment variables (e.g., API keys)
load_dotenv()

app = FastAPI(title="Subway Outlets API")

# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Outlets Endpoints (using sqlite3) ---

DATABASE = "subway.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

@app.get("/", summary="API Home")
def home():
    return {"message": "Welcome to the UPDATED Subway Outlets API!"}

@app.get("/outlets", response_model=List[dict], summary="Get all outlets")
def get_all_outlets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address, work_day_start, work_day_end, start_time, end_time, latitude, longitude FROM outlets")
    outlets = cursor.fetchall()
    conn.close()
    if not outlets:
        raise HTTPException(status_code=404, detail="No outlets found.")
    return [dict(outlet) for outlet in outlets]

@app.get("/outlets/{outlet_id}", response_model=dict, summary="Get outlet by ID")
def get_outlet(outlet_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address, work_day_start, work_day_end, start_time, end_time, latitude, longitude FROM outlets WHERE id = ?", (outlet_id,))
    outlet = cursor.fetchone()
    conn.close()
    if outlet is None:
        raise HTTPException(status_code=404, detail="Outlet not found.")
    return dict(outlet)
# -------------------- Chatbot Workflow Setup -------------------- #

# Initialize SQLDatabase and Groq LLM model
db = SQLDatabase.from_uri(f"sqlite:///{DATABASE}")
llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

# Create fallback handler for tool errors
def handle_tool_error(state: Dict[str, Any]) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> RunnableWithFallbacks[Any, dict]:
    """
    Create a ToolNode with a fallback to handle errors and surface them to the agent.
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

# Setup the SQL Database Toolkit and extract specific tools
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()
list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")

# Define a custom SQL query tool
@tool
def db_query_tool(query: str) -> str:
    """
    Execute a SQL query against the database and get back the result.
    If the query is not correct, an error message will be returned.
    """
    result = db.run_no_throw(query)
    if not result:
        return "Error: Query failed. Please rewrite your query and try again."
    try:
        rows = eval(result)
        formatted = "\n".join([f"- {name}: {time}" for name, time in rows])
        return f"Query Results:\n{formatted}"
    except Exception:
        return result

# Define prompt and tool for query check before execution
query_check_system = """You are a SQL expert with a strong attention to detail.
Double check the SQLite query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

You will call the appropriate tool to execute the query after running this check."""
query_check_prompt = ChatPromptTemplate.from_messages(
    [("system", query_check_system), ("placeholder", "{messages}")]
)
query_check = query_check_prompt | llm.bind_tools(
    [db_query_tool], tool_choice="required"
)

# Define the state for the agent
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# Create the workflow state graph
workflow = StateGraph(State)

# Node: First tool call to list tables
def first_tool_call(state: State) -> dict[str, List[AIMessage]]:
    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"name": "sql_db_list_tables", "args": {}, "id": "tool_abcd123"}],
            )
        ]
    }

# Node: Model check to validate the query before execution
def model_check_query(state: State) -> dict[str, List[AIMessage]]:
    return {"messages": [query_check.invoke({"messages": [state["messages"][-1]]})]}

workflow.add_node("first_tool_call", first_tool_call)
workflow.add_node("list_tables_tool", create_tool_node_with_fallback([list_tables_tool]))
workflow.add_node("get_schema_tool", create_tool_node_with_fallback([get_schema_tool]))

# Node: Get schema using the model and schema tool
model_get_schema = llm.bind_tools([get_schema_tool])
workflow.add_node(
    "model_get_schema",
    lambda state: {"messages": [model_get_schema.invoke(state["messages"])]},
)

# Define the final answer submission tool structure
class SubmitFinalAnswer(BaseModel):
    final_answer: str = Field(..., description="The final answer to the user")

# Node: Generate query and final answer based on the question and schema
query_gen_system = """You are a SQL expert with a strong attention to detail.

Given an input question, output a syntactically correct SQLite query to run, then look at the results of the query and return the answer.

DO NOT call any tool besides SubmitFinalAnswer to submit the final answer.

When generating the query:

Output the SQL query that answers the input question without a tool call.

Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.

If you get an error while executing a query, rewrite the query and try again.

If you get an empty result set, you should try to rewrite the query to get a non-empty result set. 
NEVER make stuff up if you don't have enough information to answer the query... just say you don't have enough information.

If you have enough information to answer the input question, simply invoke the appropriate tool to submit the final answer to the user.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
When you have the query results, analyze them and present the answer in a clear, natural language format. For example:
'The outlets that close the latest are: Outlet A at 11:00 PM, Outlet B at 11:30 PM.'

Always use this format for final answers."""
query_gen_prompt = ChatPromptTemplate.from_messages(
    [("system", query_gen_system), ("placeholder", "{messages}")]
)
query_gen = query_gen_prompt | llm.bind_tools([SubmitFinalAnswer])

def query_gen_node(state: State):
    message = query_gen.invoke(state)
    tool_messages = []
    if message.tool_calls:
        for tc in message.tool_calls:
            if tc["name"] != "SubmitFinalAnswer":
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: The wrong tool was called: {tc['name']}. Please fix your mistakes. Remember to only call SubmitFinalAnswer to submit the final answer. Generated queries should be outputted WITHOUT a tool call.",
                        tool_call_id=tc["id"],
                    )
                )
    return {"messages": [message] + tool_messages}

workflow.add_node("query_gen", query_gen_node)
workflow.add_node("correct_query", model_check_query)
workflow.add_node("execute_query", create_tool_node_with_fallback([db_query_tool]))

def should_continue(state: State) -> Literal[END, "correct_query", "query_gen"]: # type: ignore
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return END
    if last_message.content.startswith("Error:"):
        return "query_gen"
    else:
        return "correct_query"

workflow.add_edge(START, "first_tool_call")
workflow.add_edge("first_tool_call", "list_tables_tool")
workflow.add_edge("list_tables_tool", "model_get_schema")
workflow.add_edge("model_get_schema", "get_schema_tool")
workflow.add_edge("get_schema_tool", "query_gen")
workflow.add_conditional_edges("query_gen", should_continue)
workflow.add_edge("correct_query", "execute_query")
workflow.add_edge("execute_query", "query_gen")

# Compile the workflow into a runnable.
workflow_app = workflow.compile()

# ---------------------------- FastAPI Endpoint ---------------------------- #

class QueryRequest(BaseModel):
    query: str

@app.post("/query", response_model=str, summary="Execute a SQL query via LangGraph workflow")
def run_query(request: QueryRequest):
    """
    API endpoint to execute a SQL query via LangGraph workflow.
    The workflow will process the input question, generate and validate the query,
    execute it, and return the final answer.
    """
    try:
        state = {"messages": [("user", request.query)]}
        result_state = workflow_app.invoke(state)
        # Directly extract the final answer string from the tool call.
        final_answer = result_state["messages"][-1].tool_calls[0]["args"]["final_answer"]
        if not final_answer:
            raise ValueError("Final answer missing in the tool call.")
        return final_answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))