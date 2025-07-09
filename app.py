
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.title("Transport Cost Map by Postcode")

# Load your data
df = pd.read_csv("Transport Cost Comparison.csv")

# Clean and convert numeric fields
df["Transport / 1000"] = pd.to_numeric(df["Transport / 1000"], errors="coerce")
df["SP/1000"] = pd.to_numeric(df["SP/1000"], errors="coerce")
df["Annual Volume"] = pd.to_numeric(df["Annual Volume"], errors="coerce")

# Average by postcode
group_cols = ["Postcode"]
agg_dict = {
    "Transport / 1000": "mean",
    "SP/1000": "mean",
    "Annual Volume": "sum",
}
df_grouped = df.groupby(group_cols, as_index=False).agg(agg_dict)

# Preserve a sample product and code
df_details = df.groupby("Postcode").first().reset_index()
df_grouped = df_grouped.merge(df_details[["Postcode", "Code", "Product"]], on="Postcode", how="left")

# Geocode
geolocator = Nominatim(user_agent="streamlit_postcode_mapper")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
df_grouped["location"] = df_grouped["Postcode"].apply(geocode)
df_grouped["lat"] = df_grouped["location"].apply(lambda loc: loc.latitude if loc else None)
df_grouped["lon"] = df_grouped["location"].apply(lambda loc: loc.longitude if loc else None)
df_grouped.dropna(subset=["lat", "lon"], inplace=True)

st.success(f"Mapped {len(df_grouped)} postcodes successfully.")

# Create map
m = folium.Map(location=[54.5, -3], zoom_start=6)
for _, row in df_grouped.iterrows():
    tooltip = f"{row['Postcode']} | £{row['Transport / 1000']:.2f} | {row['Product']}"
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=6,
        tooltip=tooltip,
        color="blue",
        fill=True,
        fill_color="blue"
    ).add_to(m)

st_folium(m, width=700, height=500)

# Optional: Show the full data table
with st.expander("📋 View Full Data Table"):
    st.dataframe(df_grouped)
