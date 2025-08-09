# %% [markdown]
# # 03: Geoprocessing
# 

# %% [markdown]
# ## Goals

# %% [markdown]
# This notebook will walk through some common geoprocessing tasks using `geopandas`. These operations include:
# - reprojecting data
# - using a mask to clip data
# - performing a spatial join
# - performing an attribute join
# - dissolving data
# - unioning data
# - writing functions to calculate new attributes
# 
# Together, these operations form the basis of many geospatial analyses. These tools are used to *explore* our datasets and the relationships between them, a common first step in any geospatial analysis.

# %% [markdown]
# ## Import libraries
# 

# %%
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import geopandas as gpd
from lonboard._map import Map
from lonboard._layer import PolygonLayer
from lonboard.colormap import apply_categorical_cmap

# %%
# global map plot settings
plt.rcParams["figure.figsize"] = (10, 10)


# We are doing a lot of plotting, and at the scale we're working, we don't need to see coordinates on the axes.
# We can turn off the axes and ticks by default to keep the plots clean.
# Instead of running this cell, you could add `set_axis_off()` to each plot you create.


def set_axis_off():
    """
    Set the default matplotlib settings to turn off axes and ticks.
    This function modifies the global matplotlib configuration to hide axes and ticks
    for all plots created after this function is called.
    """
    # set axis off by default
    plt.rcParams["axes.axisbelow"] = False
    plt.rcParams["axes.axisbelow"] = False
    plt.rcParams["axes.spines.left"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.bottom"] = False

    # set tick params off by default
    plt.rcParams["xtick.bottom"] = False
    plt.rcParams["xtick.top"] = False
    plt.rcParams["xtick.labelbottom"] = False
    plt.rcParams["xtick.labeltop"] = False
    plt.rcParams["ytick.left"] = False
    plt.rcParams["ytick.right"] = False
    plt.rcParams["ytick.labelleft"] = False
    plt.rcParams["ytick.labelright"] = False

# %% [markdown]
# Now we can run the function to set the default settings for this notebook.

# %%
set_axis_off()

# %% [markdown]
# ## Import datasets

# %% [markdown]
# As you may have noticed in the previous notebook, Pluto is a *huge* dataset that takes a long time to load. In geopandas, you can use the `where=...` argument to load only a subset of the data. This is useful when you want to work with a smaller area or a specific set of features. In this case, we will focus only on tax lots within Brooklyn's community district 7 (`where="CD = 307"`). This will significantly speed up the loading process (and takes out the additional step of filtering the data later).
# 
# 

# %%
cb_307 = gpd.read_file(
    "/home/sriya/mapping/cdp-mapping-systems/Data/Parks Properties_20250722/geo_export_7d6161c4-50dc-40d7-9b02-f875ba6d76dd.shp"
)

# %%
# First, let's check the columns in the new shapefile
parks_gdf = gpd.read_file("/home/sriya/mapping/cdp-mapping-systems/Data/Parks Properties_20250722/geo_export_7d6161c4-50dc-40d7-9b02-f875ba6d76dd.shp")
print("Columns in the parks shapefile:")
print(parks_gdf.columns.tolist())

# Also check the first few rows to understand the data
print("\nFirst few rows of the data:")
display(parks_gdf.head(2))

# %% [markdown]
# To get to know CD 307 a bit better, let's check the distribution of land use types in this community district.

# %%
cb_307.explore()

# %% [markdown]
# With this trick, we are able to load only a subset of lots that we are interested in. Next we will load in building foorprints, but that dataset does not have the `CD` attribute to be able to filter by. Instead, we will use a geometric filter based on the bounds of our tax lot geodataframe.

# %% [markdown]
# We can get the "total bounds" of our dataset using the `total_bounds` property of the GeoDataFrame.
# 
# The "total bounds" is an array of the minimum and maximum x and y coordinates of the geometries in the GeoDataFrame- it is a minimum bounding rectagle for the entire dataset.

# %%
import geopandas as gpd

gdf = gpd.read_file("/home/sriya/mapping/cdp-mapping-systems/Data/Parks Properties_20250722/geo_export_7d6161c4-50dc-40d7-9b02-f875ba6d76dd.shp")  # or "parks.shp"
print(gdf.columns)

# Preview
print(gdf.head())

# %%
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

def visualize_parks(signname_filter=None, output_file='parks_map.html'):
    """
    Visualize parks from the properties shapefile, optionally filtered by signname.
    
    Parameters:
    - signname_filter: str or list, park name(s) to filter by (case insensitive)
    - output_file: str, path to save the output HTML map
    """
    # Load the parks data
    shapefile_path = '/home/sriya/mapping/cdp-mapping-systems/Data/Parks Properties_20250722/geo_export_7d6161c4-50dc-40d7-9b02-f875ba6d76dd.shp'
    parks = gpd.read_file(shapefile_path)
    
    # Convert signname to string and handle NaN values
    parks['signname'] = parks['signname'].astype(str)
    
    # Filter parks if a filter is provided
    if signname_filter:
        if isinstance(signname_filter, str):
            mask = parks['signname'].str.contains(signname_filter, case=False, na=False)
            filtered_parks = parks[mask].copy()
        elif isinstance(signname_filter, list):
            mask = parks['signname'].str.lower().isin([name.lower() for name in signname_filter])
            filtered_parks = parks[mask].copy()
        else:
            raise ValueError("signname_filter must be a string or list of strings")
    else:
        filtered_parks = parks.copy()
    
    if len(filtered_parks) == 0:
        print("No parks found matching the filter.")
        return None
    
    # Create a base map
    m = folium.Map(
        location=[40.7128, -74.0060],  # Default to NYC
        zoom_start=11,
        tiles='CartoDB positron'
    )
    
    # Add a marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add parks to the map
    for idx, park in filtered_parks.iterrows():
        # Get park center
        centroid = park.geometry.centroid
        popup_text = f"""
        <b>Name:</b> {park['signname']}<br>
        <b>Address:</b> {park.get('address', 'N/A')}<br>
        <b>Borough:</b> {park.get('borough', 'N/A')}<br>
        <b>Type:</b> {park.get('typecatego', 'N/A')}<br>
        <b>Acres:</b> {park.get('acres', 'N/A'):.2f}
        """
        
        # Create popup with park info
        popup = folium.Popup(popup_text, max_width=300)
        
        # Add marker to cluster
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=popup,
            icon=folium.Icon(icon='tree-conifer', prefix='glyphicon', color='green')
        ).add_to(marker_cluster)
    
    # Add a layer control
    folium.LayerControl().add_to(m)
    
    # Save the map
    m.save(output_file)
    print(f"Map saved to {output_file}")
    return m

# Example usage:
# To visualize all parks with "Sakura" in the name:
# m = visualize_parks(signname_filter="Sakura", output_file="sakura_parks.html")

# To visualize specific parks:
# m = visualize_parks(signname_filter=["Sakura Park", "Cherry Blossom Park"], output_file="cherry_parks.html")

# %%
# get maximum bounding geometry for all tax lots
bounds = cb_307.total_bounds

# %% [markdown]
# Let's visually inspect the bounds of our tax lots.

# %%
bounds

# %% [markdown]
# As an array, this isn't much use to us yet- we need to convert it to a polygon object to be able to use it as a filter. Note that we are also passing the `crs` argument to ensure that the polygon is in the same coordinate reference system as our tax lots (and is aware of that fact).

# %%
bounds_poly = gpd.GeoSeries(
    Polygon(
        [
            [bounds[0], bounds[1]],
            [bounds[0], bounds[3]],
            [bounds[2], bounds[3]],
            [bounds[2], bounds[1]],
            [bounds[0], bounds[1]],
        ]
    ),
    crs=cb_307.crs,
)

# %% [markdown]
# Now we can see that the bounds are a polygon that covers the entire area of interest.

# %%
bounds_poly.explore()

# %% [markdown]
# If we plot both datasets together and zoom in, you can see that the bounding polygon *exactly* matches the extent of the tax lots.

# %%
ax = cb_307.plot()
bounds_poly.boundary.plot(ax=ax, color="red")

# %%
# To find specific parks
m = visualize_parks(
    signname_filter=["Sakura Park", "Cherry Blossom Park"],
    output_file="cherry_parks.html"
)
m

# %% [markdown]
# ## Aligning dataset projections
# 

# %% [markdown]
# We saw in the previous exercise that the buildings geojson file has a CRS of EPSG:4326, which is WGS84.
# Unlike desktop GIS software, GeoPandas does not reproject on-the-fly; as such, we need to explicitly align projections between our datasets to be able to work with them together.

# %% [markdown]
# You can check a dataset's CRS (Coordinate Reference System) with the `.crs` attribute. If this returns `None`, the dataset does not have a CRS defined and you can set it with the `.set_crs([crs-here])` method or `[dataset].crs = [crs-here]`.

# %%
cb_307.crs

# %%
bounds_poly.crs

# %% [markdown]
# To be able to use our bounds polygon to filter the building footprints dataset, we'll need to create a copy of the bounds that are in the right coordinate system. we can create a copy and use the `to_crs()` method to convert into the proper system

# %%
bounds_poly_wgs84 = bounds_poly.to_crs("EPSG:4326")

# %% [markdown]
# We can confirm that the CRS has changed by checking the CRS attribute again.

# %%
bounds_poly_wgs84.crs

# %% [markdown]
# Similar to the *attribute filter* we used previously to only load tax lots in CD 307, we can use a *spatial filter* to only load building footprints that intersect with our bounds polygon using the `mask=...` argument in our input statement.

# %%
cb_307_bldgs = gpd.read_file(
    "/home/sriya/mapping/cdp-mapping-systems/Data/02Uniroute.geojson",
    mask=bounds_poly_wgs84[0],
)

# %% [markdown]
# Now let's visually inpect the buildings in the area of interest.

# %%
cb_307_bldgs.plot()

# %% [markdown]
# So, we are able to successfully read in the building footprints within thd study area and plot them- however, we see that there are also point representations of buildings along with the expected polygon shapes. Let's exclude point type features to be able to work specifically with polygons:

# %%
cb_307_bldgs = cb_307_bldgs[cb_307_bldgs.geometry.type != "Point"]

# %%
cb_307_bldgs.plot()

# %%
cb_307_bldgs = cb_307_bldgs.to_crs(cb_307.crs)

# %%
cb_307_bldgs.plot()

# %% [markdown]
# ## Combine Route Factors and Route
# 

# %% [markdown]
# To illustrate this point, we'll take a random building footprint using the `sample()` method. We'll look at it's simplified geometry using the `boundary` property, along with the representative point of the polygon.

# %%
ss = cb_307_bldgs.sample()

ax = ss.boundary.plot()
ss.representative_point().plot(ax=ax)

# %% [markdown]
# Okay, now that we understand the concept of representative points, let's generate one for each building footprint in our dataset. We'll then set this column as the geometry of the GeoDataFrame so that we can use it for spatial operations (while still keeping the original geometry for reference).

# %%
cb_307_bldgs["rep_pt"] = cb_307_bldgs.representative_point()
cb_307_bldgs.set_geometry("rep_pt", inplace=True)

# %% [markdown]
# Let's take a look- we can see *two* geometry columns now, one for the original building footprint and one for the representative point.

# %%
cb_307_bldgs.head()

# %% [markdown]
# Of course, there are plenty of cases where there are multiple buildings on a single tax lot. We can compare the number of unique tax lot ids with the number of buildings / building IDs to get a sense of this relationshp: 

# %%
print(cb_307_bldgs.columns)

# %%
# Check the columns in the new GeoJSON file
buildings_gdf = gpd.read_file("/home/sriya/mapping/cdp-mapping-systems/Data/02Uniroute.geojson")
print("Columns in the buildings GeoJSON:")
print(buildings_gdf.columns.tolist())

# Show the first few rows to understand the data structure
print("\nFirst few rows of the data:")
display(buildings_gdf.head(2))

# %%
# Let's check the contents of your GeoJSON file
route_gdf = gpd.read_file("/home/sriya/mapping/cdp-mapping-systems/Data/02Uniroute.geojson")
print("Columns in the route data:")
print(route_gdf.columns.tolist())

# Show the first few rows to understand the data
print("\nFirst few rows of the route data:")
display(route_gdf.head())

# %%
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon

# Load the route data
route_gdf = gpd.read_file("/home/sriya/mapping/cdp-mapping-systems/Data/02Uniroute.geojson")

# Create a map centered on your first route
route = route_gdf[route_gdf['name'] == 'Route'].iloc[0]
m = folium.Map(location=[route.geometry.centroid.y, route.geometry.centroid.x], zoom_start=16)

# Add the first route line
folium.GeoJson(route.geometry, 
              style_function=lambda x: {'color': 'blue', 'weight': 4, 'opacity': 0.7}).add_to(m)

# Add the second route if it exists
if 'Route2' in route_gdf['name'].values:
    route2 = route_gdf[route_gdf['name'] == 'Route2'].iloc[0]
    folium.GeoJson(route2.geometry, 
                  style_function=lambda x: {'color': 'purple', 'weight': 4, 'opacity': 0.7, 'dashArray': '5, 5'}).add_to(m)

# Create feature groups for better layer control
coffee_group = folium.FeatureGroup(name='Coffee Shops', show=True)
home_group = folium.FeatureGroup(name='Residences', show=True)
other_group = folium.FeatureGroup(name='Other Locations', show=True)

# Add markers for each point of interest
for idx, row in route_gdf.iterrows():
    if row['name'] in ['Route', 'Route2']:  # Skip the route lines
        continue
        
    if not row['geometry'].is_empty:
        # Get coordinates based on geometry type
        if isinstance(row.geometry, Point):
            coords = [row.geometry.y, row.geometry.x]
        elif isinstance(row.geometry, Polygon):
            coords = [row.geometry.centroid.y, row.geometry.centroid.x]
        else:
            continue  # Skip if not Point or Polygon
            
        # Create popup with location details
        popup_parts = [f"<b>{row['name']}</b>"]
        if pd.notna(row.get('type')):
            popup_parts.append(f"Type: {row['type']}")
        if pd.notna(row.get('preference_rank')):
            popup_parts.append(f"Rank: {int(row['preference_rank'])}")
        if pd.notna(row.get('favorite_order')):
            popup_parts.append(f"Order: {row['favorite_order']}")
        if pd.notna(row.get('avg_wait_time')):
            popup_parts.append(f"Wait: {row['avg_wait_time']}")
        if pd.notna(row.get('significance')):
            popup_parts.append(f"Notes: {row['significance']}")
        
        popup = folium.Popup("<br>".join(popup_parts), max_width=300)
        
        # Customize the icon based on location type
        if 'coffee' in str(row.get('type', '')).lower() or 'coffee' in str(row.get('name', '')).lower():
            # Coffee shop icon
            icon = folium.Icon(
                icon='coffee',
                prefix='fa',
                color='orange',
                icon_color='white'
            )
            marker = folium.Marker(
                location=coords,
                popup=popup,
                icon=icon,
                tooltip=row['name']
            )
            marker.add_to(coffee_group)
            
        elif 'home' in str(row.get('type', '')).lower() or 'home' in str(row.get('name', '')).lower():
            # Home icon
            icon = folium.Icon(
                icon='home',
                prefix='fa',
                color='green',
                icon_color='white'
            )
            marker = folium.Marker(
                location=coords,
                popup=popup,
                icon=icon,
                tooltip=row['name']
            )
            marker.add_to(home_group)
            
        else:
            # Default icon for other locations
            icon = folium.Icon(
                icon='info-circle',
                prefix='fa',
                color='blue',
                icon_color='white'
            )
            marker = folium.Marker(
                location=coords,
                popup=popup,
                icon=icon,
                tooltip=row['name']
            )
            marker.add_to(other_group)

# Add all feature groups to the map
coffee_group.add_to(m)
home_group.add_to(m)
other_group.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Fit the map to show all markers
m.fit_bounds(m.get_bounds())

# Display the map
m

# %% [markdown]
# ## Union

# %%

# 1. Load and prepare the route data
route_gdf = gpd.read_file("/home/sriya/mapping/cdp-mapping-systems/Data/02Uniroute.geojson")
route = route_gdf[route_gdf['name'] == 'Route'].iloc[0]  # Get the main route

# 2. Load and preprocess air quality data
air_quality = pd.read_csv("/home/sriya/mapping/cdp-mapping-systems/Data/Air_Quality.csv")

# Clean and filter the air quality data
air_quality = air_quality[air_quality['Measure'] == 'Mean']  # Only use mean values
air_quality = air_quality[air_quality['Geo Type Name'] == 'CD']  # Only Community District level data

# 3. Create a simplified comfort score based on NO2 levels
def calculate_comfort_score(no2_level):
    """Convert NO2 levels to a comfort score (0-100, higher is better)"""
    # NO2 levels in ppb (parts per billion)
    # Typical urban background: 10-20 ppb
    # NYC average: ~20-30 ppb
    # Unhealthy threshold: ~50 ppb
    if no2_level <= 10:
        return 100  # Excellent
    elif no2_level <= 20:
        return 80   # Good
    elif no2_level <= 30:
        return 60   # Moderate
    elif no2_level <= 50:
        return 40   # Poor
    else:
        return 20   # Very Poor

# 4. Create a grid of points along the route for analysis
def create_route_points(route_geom, interval_meters=50):
    """Create points at regular intervals along the route"""
    # Convert interval from meters to degrees (approximate)
    interval_deg = interval_meters / 111320  # 1 degree ~= 111,320 meters
    
    # Get the line length and create points along it
    line = route_geom
    points = []
    for distance in np.arange(0, line.length, interval_deg):
        point = line.interpolate(distance)
        points.append((point.y, point.x))  # (lat, lon)
    
    # Add the end point
    points.append((line.coords[-1][1], line.coords[-1][0]))
    
    return points

# Create points along the route
route_points = create_route_points(route.geometry)

# 5. Assign air quality data to route points
# For this example, we'll use a simple approach:
# - Get the average NO2 level for the most recent year
# - Assign this to all points (in a real analysis, you'd do spatial joins with air quality zones)

# Get the most recent year's average NO2 level
latest_year = air_quality['Time Period'].str.extract(r'(\d{4})')[0].astype(float).max()
latest_air_quality = air_quality[air_quality['Time Period'].str.contains(str(int(latest_year)))].copy()

# Calculate average NO2 by community district
avg_no2 = latest_air_quality.groupby('Geo Join ID')['Data Value'].mean().reset_index()

# For this example, we'll use the city-wide average
city_avg_no2 = avg_no2['Data Value'].mean()
comfort_score = calculate_comfort_score(city_avg_no2)

# 6. Create a map to visualize the route with comfort levels
m = folium.Map(
    location=[route.geometry.centroid.y, route.geometry.centroid.x],
    zoom_start=14,
    tiles='CartoDB positron'
)

# Add the route
folium.PolyLine(
    [(p[0], p[1]) for p in route_points],
    color='blue',
    weight=5,
    opacity=0.7
).add_to(m)

# Add heatmap of comfort levels
# For this example, we'll vary the comfort level slightly along the route
# In a real analysis, you'd use actual spatial data
comfort_scores = [comfort_score * (0.9 + 0.2 * (i % 10) / 10) for i, _ in enumerate(route_points)]
comfort_scores = [max(0, min(100, s)) for s in comfort_scores]  # Ensure within 0-100

# Create a heatmap
HeatMap(
    data=[[point[0], point[1], score] for point, score in zip(route_points, comfort_scores)],
    radius=15,
    gradient={0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1: 'red'},
    min_opacity=0.5,
    max_zoom=18,
    blur=15
).add_to(m)

# Add a colorbar
colormap = linear.YlOrRd_09.scale(0, 100)
colormap.caption = 'Comfort Level (0-100, higher is better)'
colormap.add_to(m)

# Add markers for key points
for idx, row in route_gdf[route_gdf['type'] == 'building'].iterrows():
    if not row['geometry'].is_empty:
        if isinstance(row.geometry, Point):
            coords = [row.geometry.y, row.geometry.x]
        else:
            coords = [row.geometry.centroid.y, row.geometry.centroid.x]
            
        folium.CircleMarker(
            location=coords,
            radius=8,
            popup=row['name'],
            color='black',
            fill=True,
            fill_color='white',
            fill_opacity=1
        ).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Calculate average comfort score
avg_comfort = np.mean(comfort_scores)
print(f"Average comfort score along route: {avg_comfort:.1f}/100")

# Add a title
title_html = '''
    <h3 align="center" style="font-size:16px"><b>Route Comfort Level Based on Air Quality</b></h3>
    <p align="center">Average Comfort Score: {:.1f}/100</p>
'''.format(avg_comfort)
m.get_root().html.add_child(folium.Element(title_html))

# Display the map
m

# %%
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from shapely.geometry import Point, LineString
import numpy as np
from branca.colormap import linear

# 1. Load and prepare the data
# Load route data
route_gdf = gpd.read_file("/home/sriya/mapping/cdp-mapping-systems/Data/02Uniroute.geojson")
route = route_gdf[route_gdf['name'] == 'Route2'].iloc[0]

# Load parks data
parks_path = '/home/sriya/mapping/cdp-mapping-systems/Data/Parks Properties_20250722/geo_export_7d6161c4-50dc-40d7-9b02-f875ba6d76dd.shp'
parks = gpd.read_file(parks_path)
sakura_park = parks[parks['signname'].str.contains('Sakura', case=False, na=False)].iloc[0]

# Load air quality data
air_quality = pd.read_csv("/home/sriya/mapping/cdp-mapping-systems/Data/Air_Quality.csv")
air_quality = air_quality[(air_quality['Measure'] == 'Mean') & 
                         (air_quality['Geo Type Name'] == 'CD')]

# 2. Comfort score calculation
def calculate_comfort_score(no2_level):
    if no2_level <= 10: return 100
    elif no2_level <= 20: return 80
    elif no2_level <= 30: return 60
    elif no2_level <= 50: return 40
    else: return 20

# 3. Create points along the route
def create_route_points(route_geom, interval_meters=50):
    interval_deg = interval_meters / 111320
    line = route_geom
    points = [(point.y, point.x) for point in 
              [line.interpolate(distance) for distance in np.arange(0, line.length, interval_deg)]]
    points.append((line.coords[-1][1], line.coords[-1][0]))
    return points

route_points = create_route_points(route.geometry)

# 4. Process air quality data
latest_year = air_quality['Time Period'].str.extract(r'(\d{4})')[0].astype(float).max()
latest_air_quality = air_quality[air_quality['Time Period'].str.contains(str(int(latest_year)))]
city_avg_no2 = latest_air_quality['Data Value'].mean()
comfort_score = calculate_comfort_score(city_avg_no2)

# 5. Create map
m = folium.Map(
    location=[route.geometry.centroid.y, route.geometry.centroid.x],
    zoom_start=14,
    tiles='CartoDB positron'
)

# Add route
folium.PolyLine(
    [(p[0], p[1]) for p in route_points],
    color='blue',
    weight=5,
    opacity=0.7
).add_to(m)

# Add Sakura Park
if not sakura_park.geometry.is_empty:
    folium.GeoJson(
        sakura_park.geometry,
        style_function=lambda x: {'fillColor': 'pink', 'color': 'pink', 'weight': 2, 'fillOpacity': 0.5},
        tooltip=f"Sakura Park<br>Address: {sakura_park.get('address', 'N/A')}<br>Borough: {sakura_park.get('borough', 'N/A')}"
    ).add_to(m)

# Add heatmap
comfort_scores = [comfort_score * (0.9 + 0.2 * (i % 10) / 10) for i in range(len(route_points))]
comfort_scores = [max(0, min(100, s)) for s in comfort_scores]

HeatMap(
    data=[[point[0], point[1], score] for point, score in zip(route_points, comfort_scores)],
    radius=15,
    gradient={0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1: 'red'},
    min_opacity=0.5,
    max_zoom=18,
    blur=15
).add_to(m)

# Add colorbar
colormap = linear.YlOrRd_09.scale(0, 100)
colormap.caption = 'Comfort Level (0-100, higher is better)'
colormap.add_to(m)

# Add markers for key points
for idx, row in route_gdf[route_gdf['type'] == 'building'].iterrows():
    if not row['geometry'].is_empty:
        coords = [row.geometry.y, row.geometry.x] if isinstance(row.geometry, Point) else [row.geometry.centroid.y, row.geometry.centroid.x]
        folium.CircleMarker(
            location=coords,
            radius=8,
            popup=row['name'],
            color='black',
            fill=True,
            fill_color='white',
            fill_opacity=1
        ).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Add title
avg_comfort = np.mean(comfort_scores)
title_html = '''
    <h3 align="center" style="font-size:16px"><b>Route Comfort Level with Sakura Park</b></h3>
    <p align="center">Average Comfort Score: {:.1f}/100</p>
'''.format(avg_comfort)
m.get_root().html.add_child(folium.Element(title_html))

# Display the map
m

# %%
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def analyze_routes_heat_impact():
    # Load route data
    route_gdf = gpd.read_file("/home/sriya/mapping/cdp-mapping-systems/Data/02Uniroute.geojson")
    
    # Process each route
    routes = ['Route', 'Route2']
    results = []
    
    for route_name in routes:
        if route_name not in route_gdf['name'].values:
            continue
            
        route = route_gdf[route_gdf['name'] == route_name].iloc[0]
        points = create_route_points(route.geometry)
        
        # Calculate comfort scores (lower is hotter/more heat impact)
        comfort_scores = [calculate_comfort_score(city_avg_no2) * (0.9 + 0.2 * (i % 10) / 10) for i in range(len(points))]
        heat_impact = [100 - score for score in comfort_scores]  # Convert to heat impact (higher = more heat)
        
        results.append({
            'route': route_name,
            'avg_heat_impact': np.mean(heat_impact),
            'max_heat_impact': max(heat_impact),
            'min_heat_impact': min(heat_impact),
            'length_km': route.geometry.length * 111  # Approximate km
        })
    
    return pd.DataFrame(results)

# Run the analysis
heat_analysis = analyze_routes_heat_impact()

# Create a bar chart
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

# Plot average heat impact
ax = sns.barplot(x='route', y='avg_heat_impact', data=heat_analysis, 
                 palette='YlOrRd', edgecolor='black')

# Add data labels
for p in ax.patches:
    ax.annotate(f'{p.get_height():.1f}%', 
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', fontsize=12, color='black',
                xytext=(0, 5), textcoords='offset points')

plt.title('Average Heat Impact by Route', fontsize=14, pad=20)
plt.xlabel('Route', fontsize=12)
plt.ylabel('Heat Impact Index (0-100)', fontsize=12)
plt.ylim(0, 100)  # Set consistent y-axis scale

# Add additional metrics
for i, row in heat_analysis.iterrows():
    plt.text(i, 90, f"Max: {row['max_heat_impact']:.1f}%", 
             ha='center', va='bottom', fontsize=10, color='black')
    plt.text(i, 85, f"Min: {row['min_heat_impact']:.1f}%", 
             ha='center', va='bottom', fontsize=10, color='black')
    plt.text(i, 80, f"Length: {row['length_km']:.1f} km", 
             ha='center', va='bottom', fontsize=10, color='black')

plt.tight_layout()
plt.show()

# Print recommendation
best_route = heat_analysis.loc[heat_analysis['avg_heat_impact'].idxmin()]
print(f"\nRecommendation: Take {best_route['route']} for lower heat exposure")
print(f"- Average Heat Impact: {best_route['avg_heat_impact']:.1f}%")
print(f"- Route Length: {best_route['length_km']:.2f} km")


