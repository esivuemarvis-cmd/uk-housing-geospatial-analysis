import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# -------------------------
# PAGE SETUP
# -------------------------
st.set_page_config(page_title="UK Housing Dashboard", layout="wide")

st.title("🏡 UK Housing Price Dashboard")
st.markdown("Interactive analysis of UK property prices by district")

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/price_paid.csv", header=None)

    df.columns = [
        "id", "price", "date", "postcode",
        "property_type", "new_build", "tenure",
        "paon", "saon", "street", "locality",
        "town", "district", "county", "category", "status"
    ]

    df = df[['price', 'district']].dropna()
    df['price'] = df['price'].astype(float)
    df = df[df['district'] != "GREATER LONDON"]

    avg_price = df.groupby('district')['price'].mean().reset_index()
    avg_price['district'] = avg_price['district'].str.upper().str.strip()

    return avg_price


@st.cache_data
def load_map():
    gdf = gpd.read_file("data/LAD_DEC_24_UK_BGC.shp")
    gdf['LAD24NM'] = gdf['LAD24NM'].str.upper().str.strip()
    return gdf


avg_price = load_data()
gdf = load_map()

# -------------------------
# MATCH DATA
# -------------------------
merged_list = []

for _, row in avg_price.iterrows():
    district = row['district']
    clean_name = district.replace("CITY OF ", "")

    match = gdf[gdf['LAD24NM'].str.contains(clean_name, na=False)]

    if not match.empty:
        match = match.copy()
        match['price'] = row['price']
        merged_list.append(match)

if merged_list:
    merged = pd.concat(merged_list)
else:
    merged = gpd.GeoDataFrame()

# -------------------------
# DASHBOARD METRICS
# -------------------------
if len(merged) > 0:
    col1, col2, col3 = st.columns(3)

    col1.metric("Average Price", f"£{int(merged['price'].mean()):,}")
    col2.metric("Highest Area", merged.loc[merged['price'].idxmax()]['LAD24NM'])
    col3.metric("Max Price", f"£{int(merged['price'].max()):,}")

# -------------------------
# FILTER
# -------------------------
districts = sorted(merged['LAD24NM'].unique())
selected = st.selectbox("Select District", districts)

filtered = merged[merged['LAD24NM'] == selected]

# -------------------------
# MAP DISPLAY
# -------------------------
st.subheader("📍 Selected District Map")

fig1, ax1 = plt.subplots(figsize=(6, 6))
filtered.plot(column='price', ax=ax1, legend=True)

ax1.set_title(f"{selected}")
ax1.axis('off')

st.pyplot(fig1)

# -------------------------
# FULL UK MAP
# -------------------------
st.subheader("🗺️ UK House Price Map")

fig2, ax2 = plt.subplots(figsize=(12, 8))
merged.plot(column='price', ax=ax2, legend=True)

ax2.set_title("UK House Prices by District")
ax2.axis('off')

st.pyplot(fig2)