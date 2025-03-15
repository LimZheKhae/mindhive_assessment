# Subway Outlets API & Web Scraper

This project is designed to scrape Subway outlet data for Kuala Lumpur branches, store and process the data in a SQLite database, and expose the information via a FastAPI backend. A Streamlit-based web interface displays an interactive map and provides a chatbot functionality powered by LangChain/LangGraph for querying the data.

---

## Prerequisites

- **Anaconda Installation:**  
  Ensure you have [Anaconda](https://www.anaconda.com/products/individual) installed.

- **Conda Environment:**  
  Create and activate a new conda environment named `mindhive_assessment`:
  ```bash
  conda create --name mindhive_assessment python=3.9
  conda activate mindhive_assessment
  ```

## Installation

### Clone the Repository:
```bash
git clone <repository_url>
cd <repository_directory>
```

### Install Dependencies:
Install the required Python packages using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### Setup API Keys & Selenium:

#### Selenium:
The project uses Selenium along with `webdriver-manager` which automatically manages the Chrome driver.

#### Google Maps API:
Create a `.env` file in the project root and add your Google Maps API key:
```ini
GOOGLE_MAP_API=your_google_maps_api_key
```

#### Groq API:
Also include your Groq API key in the `.env` file:
```ini
GROQ_API_KEY=your_groq_api_key
```

## Requirements File

Below is an example of a `requirements.txt` file for the project. Adjust or pin versions as needed:
```nginx
fastapi
uvicorn
pydantic
python-dotenv
langchain-groq
langchain_community
langchain_core
langgraph
selenium
webdriver-manager
googlemaps
pandas
streamlit
folium
streamlit-folium
requests
```
Install the dependencies with:
```bash
pip install -r requirements.txt
```

## Project Structure & File-Level Specification

### 1. `scrape.ipynb`
**Purpose:**
- Performs web scraping and geocoding.
- Extracts Subway store details (name, address, working hours) from Subway Malaysia for Kuala Lumpur branches.
- Normalizes day names and time formats, and saves the processed data into a SQLite database (`subway.db`).
- Updates missing geocodes using the Google Maps API.

**Key Components:**
- **Day & Time Normalization:** Functions to convert short day names to full names and normalize time formats.
- **Web Scraping:** Uses Selenium to extract store data.
- **Data Storage:** Saves data to SQLite using Pandas.
- **Geocoding:** Updates missing geographical coordinates via Google Maps API.

### 2. `main.py`
**Purpose:**
- Implements the FastAPI backend.
- Exposes endpoints to retrieve all Subway outlets and individual outlet details.
- Integrates a chatbot workflow using LangChain and LangGraph for dynamic SQL query processing.

**How to Run:**
Start the FastAPI server with:
```bash
uvicorn main:app --reload
```

**Key Components:**
- **API Endpoints:**
  - Root endpoint: Welcome message.
  - `/outlets`: Retrieves all outlet records.
  - `/outlets/{outlet_id}`: Retrieves a specific outlet by its ID.
- **Chatbot Workflow:**
  - Uses LangChain/LangGraph to process and validate SQL queries.
  - Ensures safe query execution with fallback error handling.

### 3. `app.py`
**Purpose:**
- Provides a user-friendly front end using Streamlit.
- Displays an interactive Folium map with markers for each Subway outlet.
- Offers a chatbot interface for querying the outlets database.

**Important:**
Execute `main.py` (the FastAPI server) before running `app.py` to ensure the API endpoints are available.

**How to Run:**
Start the Streamlit app with:
```bash
streamlit run app.py
```

**Key Components:**
- **Map Visualization:**
  - Uses Folium to create a map centered on Kuala Lumpur.
  - Adds markers and popups with outlet details.
- **Chatbot Interface:**
  - Provides an input box for user queries.
  - Sends queries to the FastAPI endpoint and displays responses.

## Execution Flow

### Web Scraping & Data Preparation (`scrape.ipynb`):
1. Scrape outlet data and process working hours.
2. Geocode addresses with the Google Maps API.
3. Save the structured data to a SQLite database (`subway.db`).

### API Server (`main.py`):
1. Launch the FastAPI server using:
   ```bash
   uvicorn main:app --reload
   ```
2. Access endpoints to retrieve or query outlet data.
3. Utilize the LangChain/LangGraph-powered chatbot for dynamic SQL queries.

### Web Interface (`app.py`):
1. Run the Streamlit application using:
   ```bash
   streamlit run app.py
   ```
2. Visualize Subway outlets on an interactive map.
3. Use the chatbot interface to query the API.

**Note:** Always start `main.py` before running `app.py` to ensure proper API functionality.

## Summary

This project integrates web scraping, API development, and a web-based interactive map to provide comprehensive data on Subway outlets in Kuala Lumpur. With Selenium handling data extraction, FastAPI and LangChain powering the backend, and Streamlit delivering a responsive front end, this project is a robust example of full-stack Python development.