
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import branca.colormap as cm

st.set_page_config(layout="wide")
st.title("🚚 Transport Cost Map by Postcode")

# Load and clean data
df = pd.read_csv("Transport Cost Comparison.csv")
df["Transport / 1000"] = pd.to_numeric(df["Transport / 1000"], errors="coerce")
df["SP/1000"] = pd.to_numeric(df["SP/1000"], errors="coerce")
df["Annual Volume"] = pd.to_numeric(df["Annual Volume"], errors="coerce")

# Group and merge product details
df_grouped = df.groupby("Postcode", as_index=False).agg({
    "Transport / 1000": "mean",
    "SP/1000": "mean",
    "Annual Volume": "sum"
})
df_first = df.groupby("Postcode").first().reset_index()
df_grouped = df_grouped.merge(df_first[["Postcode", "Code", "Product"]], on="Postcode", how="left")

# Geocode
geolocator = Nominatim(user_agent="streamlit_postcode_mapper")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
df_grouped["location"] = df_grouped["Postcode"].apply(geocode)
df_grouped["lat"] = df_grouped["location"].apply(lambda loc: loc.latitude if loc else None)
df_grouped["lon"] = df_grouped["location"].apply(lambda loc: loc.longitude if loc else None)
df_grouped.dropna(subset=["lat", "lon"], inplace=True)

st.success(f"Mapped {len(df_grouped)} valid postcodes.")

# Color scale
min_cost = df_grouped["Transport / 1000"].min()
max_cost = df_grouped["Transport / 1000"].max()
colormap = cm.linear.YlOrRd_09.scale(min_cost, max_cost)
colormap.caption = "Transport Cost (£ / 1000)"

# Select view type
view_type = st.radio("Select View Type", ["Markers with Color", "Clustered Markers", "Heatmap"], horizontal=True)

# Create map
m = folium.Map(location=[54.5, -3], zoom_start=6)

if view_type == "Markers with Color":
    for _, row in df_grouped.iterrows():
        tooltip = f"{row['Postcode']} | £{row['Transport / 1000']:.2f} | {row['Product']}"
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6,
            tooltip=tooltip,
            color=colormap(row["Transport / 1000"]),
            fill=True,
            fill_color=colormap(row["Transport / 1000"])
        ).add_to(m)
    colormap.add_to(m)

elif view_type == "Clustered Markers":
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in df_grouped.iterrows():
        tooltip = f"{row['Postcode']} | £{row['Transport / 1000']:.2f} | {row['Product']}"
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6,
            tooltip=tooltip,
            color=colormap(row["Transport / 1000"]),
            fill=True,
            fill_color=colormap(row["Transport / 1000"])
        ).add_to(marker_cluster)
    colormap.add_to(m)

elif view_type == "Heatmap":
    heat_data = df_grouped[["lat", "lon", "Transport / 1000"]].values.tolist()
    HeatMap(heat_data, radius=15, blur=10).add_to(m)

# Display map
st_folium(m, width=1100, height=600)

# Optional: Show full data
with st.expander("📋 View Full Data Table"):
    st.dataframe(df_grouped)
