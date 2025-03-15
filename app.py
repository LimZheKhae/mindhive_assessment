import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Rename the page title
st.set_page_config(page_title="KL Subway Outlets with Chatbot")

st.title("Subway Outlets Map")

# Fetch outlet data from FastAPI
try:
    response = requests.get("http://127.0.0.1:8000/outlets")
    outlets = response.json()
except Exception as e:
    st.error(f"Error fetching outlets: {e}")
    outlets = []

# Center map at Kuala Lumpur
m = folium.Map(location=[3.1390, 101.6869], zoom_start=12)

for outlet in outlets:
    lat = outlet.get("latitude")
    lon = outlet.get("longitude")
    name = outlet.get("name")
    address = outlet.get("address")
    start_time = outlet.get("start_time", "N/A")
    end_time = outlet.get("end_time", "N/A")
    work_days = outlet.get("work_day_start", "") + " to " + outlet.get("work_day_end", "")
    
    if lat and lon:
        # Create HTML content for the popup
        popup_html = f"""
        <div style="width: 250px; padding: 10px;">
            <h3 style="margin: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                <i class="fa fa-store" style="margin-right: 8px;"></i>{name}
            </h3>
            
            <div style="margin-top: 10px;">
                <p style="margin: 5px 0;">
                    <i class="fa fa-map-marker-alt" style="margin-right: 8px; color: #e74c3c;"></i>
                    {address}
                </p>
                
                <p style="margin: 5px 0;">
                    <i class="fa fa-clock" style="margin-right: 8px; color: #2ecc71;"></i>
                    Hours: {work_days} {start_time} - {end_time}
                </p>
                
                <p style="margin: 5px 0;">
                    <i class="fa fa-info-circle" style="margin-right: 8px; color: #f1c40f;"></i>
                    ID: {outlet.get("id", "N/A")}
                </p>
            </div>
            
            <a href="https://www.google.com/maps/dir/?api=1&destination={lat},{lon}" 
               target="_blank" 
               style="display: block; 
                      margin-top: 10px; 
                      padding: 8px; 
                      background-color: #3498db; 
                      color: white; 
                      text-align: center; 
                      text-decoration: none; 
                      border-radius: 4px;">
                <i class="fa fa-directions" style="margin-right: 5px;"></i>Get Directions
            </a>
        </div>
        """
        
        # Create the marker with styled popup
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Click for {name} details",
            icon=folium.Icon(icon='info-sign', color='red', prefix='fa')
        ).add_to(m)

        # Add circle overlay
        folium.Circle(
            location=[lat, lon],
            radius=5000,
            color='blue',
            fill=True,
            fill_opacity=0.03
        ).add_to(m)

st_data = st_folium(m, width=700)

# Chatbot functionality
st.subheader("Ask a Query")

# Initialize session state for query response if not already present
if "query_response" not in st.session_state:
    st.session_state.query_response = None

query = st.text_input("Enter your query", "")

if st.button("Submit"):
    if query:
        with st.spinner("Processing your query..."):
            try:
                res = requests.post("http://127.0.0.1:8000/query", json={"query": query})
                # The API returns a JSON with a single key "result"
                st.session_state.query_response = res.json()
                st.write(st.session_state.query_response)
            except Exception as e:
                st.error(f"Error processing query: {e}")
    else:
        st.warning("Please enter a query.")