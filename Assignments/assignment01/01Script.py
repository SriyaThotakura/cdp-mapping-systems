# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# %%
import geopandas as gpd
from shapely.geometry import Point

# %%
from lonboard._map import Map
from lonboard._layer import ScatterplotLayer
from lonboard.colormap import apply_categorical_cmap, apply_continuous_cmap
from palettable.colorbrewer.qualitative import Set3_12
from palettable.colorbrewer.sequential import YlOrRd_9
from matplotlib.colors import LogNorm

# %%
import pygwalker as pyg

# %%
import pandas as pd

trees = pd.read_csv("/home/sriya/mapping/cdp-mapping-systems/Data/bprd_trees.csv")

# %%
trees.head()

# %%
trees.columns

# %%
trees.dtypes

# %%
trees.shape

# %%
trees.spp_com.value_counts().head(15)

# %%
plt.figure(figsize=(12, 8))
top_species = trees.spp_com.value_counts().head(15)
ax = top_species.plot(kind='barh', color='forestgreen', edgecolor='black')
plt.title('Top 15 Tree Species in Boston Urban Forest', fontsize=16, fontweight='bold')
plt.xlabel('Number of Trees', fontsize=12)
plt.ylabel('Species', fontsize=12)
plt.grid(axis='x', alpha=0.3)


# %%
for i, v in enumerate(top_species.values):
    ax.text(v + 50, i, f'{v:,}', va='center', fontweight='bold')

plt.tight_layout()

# %%
trees['location_type'] = trees['park'].apply(
    lambda x: 'Park Tree' if pd.notna(x) and str(x).strip() != '' else 'Street Tree'
)


# %%
trees.location_type.value_counts()

# %% [markdown]
# Park vs Street trees gives us the idea of microclimate referenced shade and greenery in the city

# %%
plt.figure(figsize=(10, 6))
location_counts = trees['location_type'].value_counts()
colors = ['#228B22', '#90EE90']
plt.pie(location_counts.values, labels=location_counts.index, autopct='%1.1f%%', 
        colors=colors, startangle=90)
plt.title('Distribution of Park vs Street Trees', fontsize=16, fontweight='bold')
plt.axis('equal')


# %%
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

park_species = trees[trees['location_type'] == 'Park Tree']['spp_com'].value_counts().head(10)
park_species.plot(kind='bar', ax=ax1, color='darkgreen', title='Top 10 Park Tree Species')
ax1.set_xlabel('Species')
ax1.set_ylabel('Count')
ax1.tick_params(axis='x', rotation=45)

street_species = trees[trees['location_type'] == 'Street Tree']['spp_com'].value_counts().head(10)
street_species.plot(kind='bar', ax=ax2, color='lightgreen', title='Top 10 Street Tree Species')
ax2.set_xlabel('Species')
ax2.set_ylabel('Count')
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()


# %%
trees['dbh'] = pd.to_numeric(trees['dbh'], errors='coerce')
mean_diameter = trees['dbh'].mean()
std_diameter = trees['dbh'].std()
trees_clean = trees[(trees['dbh'] >= mean_diameter - 3*std_diameter) & 
                   (trees['dbh'] <= mean_diameter + 3*std_diameter)]

# %%
trees_clean['dbh'].describe()

# %% [markdown]
# Spread - Diameter coverage

# %%
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Histogram of tree diameters
ax1.hist(trees_clean['dbh'].dropna(), bins=30, edgecolor='black', alpha=0.7, color='brown')
ax1.set_title('Distribution of Tree Diameters')
ax1.set_xlabel('Diameter (inches)')
ax1.set_ylabel('Frequency')
ax1.grid(axis='y', alpha=0.3)

# Box plot of diameter by location type
location_data = [trees_clean[trees_clean['location_type'] == 'Park Tree']['dbh'].dropna(),
                 trees_clean[trees_clean['location_type'] == 'Street Tree']['dbh'].dropna()]
ax2.boxplot(location_data, labels=['Park Trees', 'Street Trees'])
ax2.set_title('Tree Diameter by Location Type')
ax2.set_ylabel('Diameter (inches)')
ax2.grid(axis='y', alpha=0.3)

# Scatter plot of diameter vs species (top 5)
top_5_species = trees_clean['spp_com'].value_counts().head(5).index
for i, species in enumerate(top_5_species):
    species_data = trees_clean[trees_clean['spp_com'] == species]
    ax3.scatter(species_data['dbh'], [i] * len(species_data), alpha=0.6, label=species)
ax3.set_xlabel('Diameter (inches)')
ax3.set_ylabel('Species')
ax3.set_title('Diameter Distribution by Top 5 Species')
ax3.set_yticks(range(len(top_5_species)))
ax3.set_yticklabels([s[:20] + '...' for s in top_5_species])
ax3.grid(True, alpha=0.3)

# Average diameter by top species
avg_diameter_by_species = trees_clean.groupby('spp_com')['dbh'].mean().sort_values(ascending=False).head(10)
ax4.bar(range(len(avg_diameter_by_species)), avg_diameter_by_species.values, color='sienna')
ax4.set_title('Average Tree Diameter by Species (Top 10)')
ax4.set_xlabel('Species')
ax4.set_ylabel('Average Diameter (inches)')
ax4.set_xticks(range(len(avg_diameter_by_species)))
ax4.set_xticklabels([s[:15] + '...' for s in avg_diameter_by_species.index], rotation=45)
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()

# %% [markdown]
# Density

# %%
trees['y_latitude'] = pd.to_numeric(trees['y_latitude'], errors='coerce')
trees['x_longitude'] = pd.to_numeric(trees['x_longitude'], errors='coerce')

# %%
trees_geo = trees.dropna(subset=['y_latitude', 'x_longitude'])

# %%
geometry = [Point(xy) for xy in zip(trees_geo['x_longitude'], trees_geo['y_latitude'])]
trees_gdf = gpd.GeoDataFrame(trees_geo, geometry=geometry, crs='EPSG:4326')

# %%
fig, ax = plt.subplots(figsize=(12, 10))
trees_gdf.plot(ax=ax, markersize=0.5, alpha=0.6, color='green')
ax.set_title('Boston BPRD Trees Distribution', fontsize=16, fontweight='bold')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.grid(True, alpha=0.3)
ax.set_axis_off()

# %% [markdown]
# Variety

# %%
top_species_for_map = trees_gdf['spp_com'].value_counts().head(8).index
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
species_color_map = dict(zip(top_species_for_map, colors))

# %%
op_species_for_map = trees_gdf['spp_com'].value_counts().head(8).index
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
species_color_map = dict(zip(top_species_for_map, colors))


# %%
trees_gdf['species_mapped'] = trees_gdf['spp_com'].apply(
    lambda x: x if x in top_species_for_map else 'Other'
)
species_color_map['Other'] = '#CCCCCC'

# %%
fig, ax = plt.subplots(figsize=(15, 12))

# Plot each species with different colors
for species in top_species_for_map:
    species_data = trees_gdf[trees_gdf['species_mapped'] == species]
    species_data.plot(ax=ax, markersize=1.5, alpha=0.7, 
                     color=species_color_map[species], label=species)

# Plot 'Other' species
other_data = trees_gdf[trees_gdf['species_mapped'] == 'Other']
other_data.plot(ax=ax, markersize=0.5, alpha=0.5, 
               color=species_color_map['Other'], label='Other')

ax.set_title('Boston Trees by Species Distribution', fontsize=16, fontweight='bold')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_axis_off()

plt.tight_layout()

# %%
sample_size = 10000
trees_sample = trees_gdf.sample(n=min(sample_size, len(trees_gdf)), random_state=42)

# %%
species_categories = trees_sample['species_mapped'].astype('category')

# %%
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Convert your species_color_map to use RGB tuples
species_color_map_rgb = {k: hex_to_rgb(v) for k, v in species_color_map.items()}

# %%
layer = ScatterplotLayer.from_geopandas(
    trees_sample[['species_mapped', 'geometry']],
    get_fill_color=apply_categorical_cmap(species_categories, cmap=species_color_map_rgb),
    get_radius=20,
    radius_scale=1,
    opacity=0.8
)
m = Map(layer)
m

# %%
trees_size_sample = trees_sample.dropna(subset=['dbh'])


# %%
print(trees_size_sample['dbh'].min(), trees_size_sample['dbh'].max())
print(trees_size_sample['dbh'].isna().sum())
print((trees_size_sample['dbh'] <= 0).sum())

# %%
trees_size_sample = trees_size_sample[trees_size_sample['dbh'] > 0].copy()
trees_size_sample = trees_size_sample.dropna(subset=['dbh'])

# %%
from matplotlib.colors import LogNorm

normalizer = LogNorm(vmin=trees_size_sample['dbh'].min(), 
                    vmax=trees_size_sample['dbh'].max(), 
                    clip=True)
normalized_diameter = normalizer(trees_size_sample['dbh'])

# %%
normalizer = LogNorm(vmin=trees_size_sample['dbh'].min(), 
                    vmax=trees_size_sample['dbh'].max(), 
                    clip=True)
normalized_diameter = normalizer(trees_size_sample['dbh'])


# %%
size_layer = ScatterplotLayer.from_geopandas(
    trees_size_sample[['dbh', 'geometry']],
    get_fill_color=apply_continuous_cmap(normalized_diameter, cmap=YlOrRd_9),
    get_radius=trees_size_sample['dbh'] * 2,
    radius_scale=1,
    opacity=0.7
)
m_size = Map(size_layer)
m_size


# %% [markdown]
# Tree Vs Species

# %%
species_diversity = trees_gdf.groupby('location_type')['spp_com'].agg(['count', 'nunique']).reset_index()
species_diversity.columns = ['Location Type', 'Total Trees', 'Unique Species']
species_diversity['Diversity Ratio'] = species_diversity['Unique Species'] / species_diversity['Total Trees']


# %%
species_diversity

# %%
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Total trees by location
ax1.bar(species_diversity['Location Type'], species_diversity['Total Trees'], 
        color=['darkgreen', 'lightgreen'])
ax1.set_title('Total Trees by Location Type')
ax1.set_ylabel('Number of Trees')

# Species diversity by location
ax2.bar(species_diversity['Location Type'], species_diversity['Unique Species'], 
        color=['darkblue', 'lightblue'])
ax2.set_title('Species Diversity by Location Type')
ax2.set_ylabel('Number of Unique Species')

plt.tight_layout()


# %%
print(trees_gdf['date_plant'].head())

# %%
# Convert 'date_plant' to datetime and extract year
trees_gdf['date_plant'] = pd.to_datetime(trees_gdf['date_plant'], errors='coerce')
trees_gdf['year'] = trees_gdf['date_plant'].dt.year

# Calculate age
trees_gdf['age'] = 2024 - trees_gdf['year']

# %%
print("Total rows in original:", len(trees_gdf))
print("Rows with valid year:", trees_gdf['year'].notnull().sum())
print("Rows with valid dbh:", trees_gdf['dbh'].notnull().sum())
print("Rows with valid age:", (2024 - trees_gdf['year']).notnull().sum())
print("Rows with valid age and dbh:", ((2024 - trees_gdf['year'] > 0) & (trees_gdf['dbh'] > 0)).sum())

# %% [markdown]
# Volume of species diversity

# %%
# Prepare data for pygwalker (remove geometry column if it exists)
trees_for_exploration = trees.drop(columns=['geometry'], errors='ignore')

# Create interactive visualization
pyg.walk(trees_for_exploration)


# %%
trees.to_csv('boston_trees_processed.csv', index=False) 

# %%
trees.to_parquet('boston_trees_processed.parquet', index=False)

# %%
trees_gdf.to_file('boston_trees_geo.geojson', driver='GeoJSON')


# %%
import plotly.express as px

fig = px.scatter_3d(
    trees_gdf,
    x='x_longitude',        # or 'POINT_X'
    y='y_latitude',         # or 'POINT_Y'
    z='dbh',                # or 'diameter', or 'age'
    color='spp_com',        # species, or any other categorical variable
    size='dbh',             # size by diameter
    hover_data=['address', 'park', 'neighborhood']
)
fig.update_layout(title='3D View of Boston Trees')
fig.show()

# %% [markdown]
# Interactive map

# %%
import pydeck as pdk

layer = pdk.Layer(
    "ScatterplotLayer",
    data=trees_gdf,
    get_position='[x_longitude, y_latitude]',
    get_radius='dbh * 2',
    get_fill_color='[200, 30, 0, 160]',
    pickable=True,
    elevation_scale=10,
    extruded=True,
)

view_state = pdk.ViewState(
    longitude=trees_gdf['x_longitude'].mean(),
    latitude=trees_gdf['y_latitude'].mean(),
    zoom=12,
    pitch=45,
)

r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{spp_com}\nDiameter: {dbh}"})
r.show()

# %%
print("Most common species:")
print(trees['spp_com'].value_counts().head(3))

# %%
print("DBH stats:")
print(trees['dbh'].describe())

# %%
print("Earliest and latest planting years:")
print(trees_gdf['year'].min(), trees_gdf['year'].max())

# %%
print("Neighborhood with most trees:")
print(trees['neighborhood'].value_counts().head(1))

# %%
species_diversity = trees.groupby('neighborhood')['spp_com'].nunique().sort_values(ascending=False)
print("Neighborhoods with highest and lowest species diversity:")
print("Highest:", species_diversity.head(1))
print("Lowest:", species_diversity.tail(1))

# %%
pip install streamlit pandas geopandas matplotlib seaborn folium streamlit-folium


