import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("data/price_paid.csv", header=None)

df.columns = [
    "id", "price", "date", "postcode",
    "property_type", "new_build", "tenure",
    "paon", "saon", "street", "locality",
    "town", "district", "county", "category", "status"
]

# -------------------------
# CLEAN DATA
# -------------------------
df = df[['price', 'district']].dropna()
df['price'] = df['price'].astype(float)

# Remove bad entries
df = df[df['district'] != "GREATER LONDON"]

# -------------------------
# GROUP DATA
# -------------------------
avg_price = df.groupby('district')['price'].mean().reset_index()

# Clean names
avg_price['district'] = avg_price['district'].str.upper().str.strip()

# -------------------------
# LOAD SHAPEFILE
# -------------------------
gdf = gpd.read_file("data/LAD_DEC_24_UK_BGC.shp")
gdf['LAD24NM'] = gdf['LAD24NM'].str.upper().str.strip()

# -------------------------
# SMART MATCH (THIS IS THE FIX)
# -------------------------
merged_list = []

for _, row in avg_price.iterrows():
    district = row['district']

    # Remove "CITY OF" during matching
    clean_name = district.replace("CITY OF ", "")

    match = gdf[gdf['LAD24NM'].str.contains(clean_name, na=False)]

    if not match.empty:
        match = match.copy()
        match['price'] = row['price']
        merged_list.append(match)

# Combine results
if merged_list:
    merged = pd.concat(merged_list)
else:
    merged = gpd.GeoDataFrame()

print("Final merged rows:", len(merged))

# -------------------------
# PLOT
# -------------------------
if len(merged) > 0:
    merged.plot(column='price', legend=True, figsize=(12, 8))
    plt.title("UK House Prices Map")
    plt.axis('off')
    plt.show()
else:
    print("❌ Still no match")