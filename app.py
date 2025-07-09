
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.title("Transport Cost Map by Postcode")

# Load your data
df = pd.read_csv("Transport Cost Comparison.csv")

# Clean up and average cost by postcode
df["Transport / 1000"] = pd.to_numeric(df["Transport / 1000"], errors="coerce")
df_grouped = df.groupby("Postcode", as_index=False)["Transport / 1000"].mean()

# Geocode postcodes
geolocator = Nominatim(user_agent="streamlit_postcode_mapper")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
df_grouped["location"] = df_grouped["Postcode"].apply(geocode)
df_grouped["lat"] = df_grouped["location"].apply(lambda loc: loc.latitude if loc else None)
df_grouped["lon"] = df_grouped["location"].apply(lambda loc: loc.longitude if loc else None)
df_grouped.dropna(subset=["lat", "lon"], inplace=True)

# Display folium map
st.success(f"Loaded {len(df_grouped)} unique postcodes.")

m = folium.Map(location=[54.5, -3], zoom_start=6)
for _, row in df_grouped.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=5,
        popup=f"{row['Postcode']}: £{row['Transport / 1000']:.2f}",
        color="blue",
        fill=True,
        fill_color="blue"
    ).add_to(m)

st_folium(m, width=700, height=500)
