
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load and clean data
df = pd.read_csv("Transport Cost Comparison.csv")
df.columns = df.columns.str.strip()  # Ensure no whitespace issues

# Debug: Show available columns
# st.write("Columns:", df.columns.tolist())

# Create color gradient from green (low) to red (high)
cmap = plt.get_cmap("RdYlGn_r")

min_cost = df["Transport / 1000"].min()
max_cost = df["Transport / 1000"].max()

def cost_to_color(value):
    norm = (value - min_cost) / (max_cost - min_cost)
    rgb = cmap(norm)[:3]
    return f"rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})"

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Transport Cost by Postcode")

st.markdown("""
**Map Legend:**
- Green = Low transport cost
- Red = High transport cost
""")

# Initialize map
center_lat = df["lat"].mean()
center_lon = df["lon"].mean()
map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=6)

# Marker clustering
marker_cluster = MarkerCluster().add_to(map_obj)

# Add data points
for _, row in df.iterrows():
    color = cost_to_color(row["Transport / 1000"])
    popup = folium.Popup(f"""
        <b>Customer:</b> {row['Customer']}<br>
        <b>Postcode:</b> {row['Postcode']}<br>
        <b>Product:</b> {row['Product']}<br>
        <b>Transport / 1000:</b> £{row['Transport / 1000']:.2f}<br>
        <b>Annual Volume:</b> {row['Annual Volume']:.0f}
    """, max_width=300)
    folium.CircleMarker(
        location=(row["lat"], row["lon"]),
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        popup=popup
    ).add_to(marker_cluster)

# Display map
folium_static(map_obj)
