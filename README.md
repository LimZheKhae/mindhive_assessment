# Subway Outlets Assessment

This project scrapes data from Subway Malaysia to gather information on Kuala Lumpur (KL) outlets, enriches the data with geocoding via the Google Maps API, and provides a FastAPI backend integrated with a LangChain/Groq-powered natural language query system. A Streamlit-based front-end displays the outlets on a map and offers a chatbot interface for querying.

## Prerequisites

- [Anaconda](https://www.anaconda.com/download) (recommended)
- [Git](https://git-scm.com/downloads)
- Python 3.11 (or later)
- Google Chrome (for web scraping functionality)

## Setup and Installation

### 1. Create and Activate Conda Environment
```bash
conda create -n mindhive_assessment python=3.11
conda activate mindhive_assessment 
```

### 2. Clone Repository & Install Dependencies
```bash
git clone https://github.com/yourusername/subway-outlets.git
cd subway-outlets
pip install -r requirements.txt ```

### 3. Configure API Keys
Create a .env file in the project root directory with the following content:
```env
GOOGLE_MAP_API=your_google_maps_api_key_here
GROQ_API_KEY=your_groq_api_key_here ```

### 4. Configure API Keys
```
├── scrape.ipynb
├── main.py
├── app.py
├── subway.db
├── requirements.txt
└── .env
```



