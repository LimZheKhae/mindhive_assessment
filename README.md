# Subway Outlets API & Web Scraper

This project scrapes Subway outlet data for Kuala Lumpur branches, stores it in a SQLite database, and exposes the data via a FastAPI backend. A Streamlit-based web interface provides an interactive map and chatbot functionality using LangChain/LangGraph.

---

## Prerequisites

### Install Anaconda
Ensure [Anaconda](https://www.anaconda.com/products/individual) is installed on your system.

### Create and Activate a Conda Environment
Run the following commands:
```
conda create --name mindhive_assessment python=3.9
conda activate mindhive_assessment
```

To deactivate the environment when finished:
```
conda deactivate
```

---

## Installation

### Clone the Repository:
```
git clone <repository_url>
cd <repository_directory>
```

### Install Dependencies:
Install the required packages using:
```
pip install -r requirements.txt
```

---

## Setup API Keys & Services

### Selenium Setup
This project uses Selenium for web scraping. Follow these steps:

1. Install `webdriver-manager` (already included in `requirements.txt`).
2. Ensure you have Google Chrome installed.
3. The `webdriver-manager` package will automatically manage the ChromeDriver.

For more information, visit: [WebDriver Manager GitHub](https://github.com/SergeyPirogov/webdriver_manager)

### Google Maps API Setup
To enable Google Maps API, follow these steps:

1. Visit [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services > Enable APIs and Services**.
4. Enable **Geocoding API**, **Maps JavaScript API**, and **Places API**.
5. Generate an API key from **Credentials**.
6. Create a `.env` file in your project root and add:
```
GOOGLE_MAP_API=your_google_maps_api_key
```

### Groq API Setup
To obtain a Groq API key:

1. Visit [Groq API](https://console.groq.com/).
2. Sign up or log in.
3. Navigate to **API Keys** and generate a new key.
4. Add the key to the `.env` file:
```
GROQ_API_KEY=your_groq_api_key
```

---

## Project Structure

### 1. `scrape.ipynb`
**Purpose:**
- Scrapes Subway store details (name, address, working hours) from Subway Malaysia for Kuala Lumpur branches.
- Normalizes working hours format.
- Saves data into a SQLite database (`subway.db`).
- Updates missing geocodes using Google Maps API.

### 2. `main.py` (FastAPI Backend)
**Purpose:**
- Provides API endpoints to retrieve Subway outlet data.
- Implements a chatbot workflow using LangChain/LangGraph for dynamic SQL query processing.

#### How to Run:
```
uvicorn main:app --reload
```

#### API Endpoints:

- **Root Endpoint (`/`)**: Displays a welcome message.
- **Get All Outlets (`/outlets`)**: Retrieves all Subway outlet records.
- **Get a Specific Outlet (`/outlets/{outlet_id}`)**: Retrieves outlet details by ID.
- **Execute a Query (`/query`)**: AI agents process natural language queries to retrieve relevant outlet information.

### 3. `app.py` (Streamlit Frontend)
**Purpose:**
- Displays an interactive map with Subway outlets.
- Provides a chatbot interface for querying the database.

#### How to Run:
```
streamlit run app.py
```

**Features:**
- **Map Visualization:** Uses Folium to create an interactive map of Kuala Lumpur with outlet markers.
- **Chatbot Interface:** Users can query outlet data through a chatbot.

---

## Execution Flow

### 1. Web Scraping & Data Preparation (`scrape.ipynb`)
- Scrape outlet data and format working hours.
- Geocode addresses using Google Maps API.
- Save data to `subway.db`.

### 2. API Server (`main.py`)
- Start the FastAPI server:
```
uvicorn main:app --reload
```
- Access API endpoints or use the chatbot.

### 3. Web Interface (`app.py`)
- Start the Streamlit application:
```
streamlit run app.py
```
- Visualize Subway outlets on an interactive map.
- Use the chatbot interface to query the API.

**Note:** Start `main.py` before `app.py` to ensure API functionality.

---

## Demo Images

Refer to the following images for a visual demonstration of the project:

- **Demo Chatbot Query:** `demo2.png` `demo1.png`
![alt text](https://https://github.com/LimZheKhae/mindhive_assessment/blob/main/demo1.png)

---

## Summary

This project integrates web scraping, API development, and an interactive web application to provide comprehensive Subway outlet data for Kuala Lumpur. Selenium handles data extraction, FastAPI and LangChain power the backend, and Streamlit delivers a user-friendly interface.
