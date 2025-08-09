# %% [markdown]
# # Green Space Accessibility Analysis
# 
# This notebook provides a clean implementation of green space accessibility analysis in urban areas.

# %%
# Import essential libraries
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, Polygon
import warnings
warnings.filterwarnings('ignore')

print("All required libraries imported successfully!")

# %% [markdown]
# ## 1. Define Study Area and Get Data

# %%
def get_data(place_name="Manhattan, New York, USA"):
    """Fetch boundary, parks, and street network data."""
    print(f"Fetching data for {place_name}...")
    
    # Get boundary
    boundary = ox.geocode_to_gdf(place_name)
    
    # Get parks data
    tags = {'leisure': 'park'}
    parks = ox.features_from_place(place_name, tags)
    parks['area_sqm'] = parks.geometry.area
    
    # Get street network
    G = ox.graph_from_place(place_name, network_type='walk')
    
    return boundary, parks, G

# Example usage
boundary, parks, G = get_data("Manhattan, New York, USA")
print("Data fetched successfully!")

# %% [markdown]
# ## 2. Create Interactive Map

# %%
def create_map(boundary, parks, G):
    """Create an interactive map with parks and street network."""
    # Create base map
    center = [boundary.centroid.y.mean(), boundary.centroid.x.mean()]
    m = folium.Map(location=center, zoom_start=13, tiles='cartodbpositron')
    
    # Add boundary
    folium.GeoJson(
        boundary,
        style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
    ).add_to(m)
    
    # Add parks
    for _, park in parks.iterrows():
        folium.GeoJson(
            park.geometry,
            style_function=lambda x: {
                'fillColor': 'green',
                'color': 'darkgreen',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=f"Park: {park.get('name', 'Unnamed')}"
        ).add_to(m)
    
    # Save map to HTML
    m.save('green_space_map.html')
    return m

# Create and display the map
map_obj = create_map(boundary, parks, G)
map_obj

# %% [markdown]
# ## Next Steps:
# 1. The interactive map has been saved as 'green_space_map.html' in your current directory.
# 2. You can open this file in any web browser to view the map.
# 3. To analyze a different area, simply change the place name in the `get_data()` function call.

# %% [markdown]
# ## 3. Advanced Analysis

# %%
print("Type of boundary:", type(boundary))
print("Type of G:", type(G))

# %%
def get_data(place_name="Manhattan, New York, USA"):
    """Fetch boundary, parks, and street network data."""
    print(f"Fetching data for {place_name}...")
    
    try:
        # Get boundary
        boundary = ox.geocode_to_gdf(place_name)
        if not isinstance(boundary, gpd.GeoDataFrame):
            raise ValueError("Failed to get boundary data")
            
        # Get parks data
        tags = {'leisure': 'park'}
        try:
            parks = ox.features_from_place(place_name, tags)
            if len(parks) == 0:
                print("Warning: No parks found with the specified tags")
            parks['area_sqm'] = parks.geometry.area
        except Exception as e:
            print(f"Error fetching parks data: {e}")
            # Create empty GeoDataFrame with the same CRS as boundary
            parks = gpd.GeoDataFrame(geometry=[], crs=boundary.crs)
    
        # Get street network
        try:
            G = ox.graph_from_place(place_name, network_type='walk')
            if not isinstance(G, nx.MultiDiGraph):
                raise ValueError("Failed to create street network")
        except Exception as e:
            print(f"Error creating street network: {e}")
            G = None
            
        return boundary, parks, G
        
    except Exception as e:
        print(f"Error in get_data: {e}")
        # Return empty objects with the right types
        empty_gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        return empty_gdf.copy(), empty_gdf.copy(), None

# %%
# Get data with error handling
boundary, parks, G = get_data("Manhattan, New York, USA")

# Check if we got valid data
if G is None:
    print("Error: Could not create street network. Please check your internet connection and try again.")
else:
    print("Data fetched successfully!")
    print(f"Number of parks: {len(parks)}")
    print(f"Number of nodes in street network: {len(G.nodes())}")
    print(f"Number of edges in street network: {len(G.edges())}")

# %%
print(f"Type of boundary: {type(boundary)}")
print(f"Type of G: {type(G)}")
print(f"Boundary CRS: {boundary.crs if hasattr(boundary, 'crs') else 'No CRS'}")
print(f"Boundary geometry type: {type(boundary.geometry.iloc[0]) if len(boundary) > 0 else 'Empty boundary'}")

# %%
def get_data(place_name="Manhattan, New York, USA"):
    """Fetch boundary, parks, and street network data."""
    print(f"Fetching data for {place_name}...")
    
    try:
        # Get boundary
        boundary = ox.geocode_to_gdf(place_name)
        if boundary.empty:
            raise ValueError("Boundary GeoDataFrame is empty")
        print(f"Boundary CRS: {boundary.crs}")
        
        # Get parks data
        tags = {'leisure': 'park'}
        parks = ox.features_from_place(place_name, tags)
        if not parks.empty:
            parks['area_sqm'] = parks.geometry.area
        else:
            print("Warning: No parks found with the specified tags")
        
        # Get street network
        G = ox.graph_from_place(place_name, network_type='walk')
        print(f"Street network nodes: {len(G.nodes())}, edges: {len(G.edges())}")
        
        return boundary, parks, G
        
    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        # Return empty objects with proper types
        empty_gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        return empty_gdf, empty_gdf, None

# %%
def get_data(place_name="Manhattan, New York, USA", which_result=1):
    """Fetch boundary, parks, and street network data with better error handling."""
    print(f"Fetching data for {place_name}...")
    
    try:
        # Try different geocoding approaches
        try:
            boundary = ox.geocode_to_gdf(place_name, which_result=which_result)
        except Exception as e:
            print(f"Geocoding attempt {which_result} failed. Trying alternative method...")
            # Try with a more general query
            boundary = ox.geocode_to_gdf(place_name.split(',')[0], which_result=1)
        
        if boundary.empty:
            raise ValueError("Failed to get boundary data")
            
        print(f"Successfully retrieved boundary for: {boundary['display_name'].iloc[0]}")
        
        # Get parks data
        try:
            tags = {'leisure': 'park'}
            parks = ox.features_from_polygon(boundary.geometry[0], tags=tags)
            if not parks.empty:
                parks['area_sqm'] = parks.geometry.area
                print(f"Found {len(parks)} parks")
            else:
                print("Warning: No parks found with the specified tags")
        except Exception as e:
            print(f"Error getting parks: {e}")
            parks = gpd.GeoDataFrame(geometry=[], crs=boundary.crs)
        
        # Get street network
        try:
            G = ox.graph_from_polygon(boundary.geometry[0], network_type='walk')
            print(f"Created street network with {len(G.nodes())} nodes")
        except Exception as e:
            print(f"Error creating street network: {e}")
            G = None
        
        return boundary, parks, G if G is not None else None
        
    except Exception as e:
        print(f"Error in get_data: {e}")
        if which_result < 3:  # Try up to 3 different geocoding results
            return get_data(place_name, which_result + 1)
        raise

# Example usage with error handling
try:
    # Try with a more reliable area first
    boundary, parks, G = get_data("Manhattan, New York, USA")
    
    # If that fails, try with just Manhattan
    if G is None or len(parks) == 0:
        print("\nTrying with just Manhattan...")
        boundary, parks, G = get_data("Manhattan, NY, USA")
    
    # If still no luck, try with New York City
    if G is None or len(parks) == 0:
        print("\nTrying with New York City...")
        boundary, parks, G = get_data("New York City, USA")
    
    if G is not None:
        print("\nSuccess! Data loaded:")
        print(f"- Boundary area: {boundary.geometry.area.sum()/1e6:.1f} sq km")
        print(f"- Number of parks: {len(parks)}")
        print(f"- Street network nodes: {len(G.nodes())}")
    else:
        print("\nFailed to load data after multiple attempts")
        
except Exception as e:
    print(f"Fatal error: {e}")
    print("Please check your internet connection and try again with a different location.")

# %%
def check_data_types(boundary, G):
    print("=== Data Type Check ===")
    print(f"Boundary type: {type(boundary)}")
    if hasattr(boundary, 'geometry'):
        print(f"Boundary geometry type: {type(boundary.geometry.iloc[0])}")
    print(f"Graph type: {type(G) if G is not None else 'None'}")
    if G is not None:
        print(f"Is graph directed? {G.is_directed() if hasattr(G, 'is_directed') else 'Not a graph'}")
    print("======================")

# Run this check after getting your data
check_data_types(boundary, G)

# %%
def get_street_network(polygon, network_type='walk'):
    """Safely get street network from a polygon."""
    try:
        G = ox.graph_from_polygon(polygon, network_type=network_type)
        if not isinstance(G, nx.MultiDiGraph) and not isinstance(G, nx.MultiGraph):
            raise ValueError("Failed to create valid network graph")
        return G
    except Exception as e:
        print(f"Error creating street network: {e}")
        return None

# Usage:
G = get_street_network(boundary.geometry.iloc[0])
if G is None:
    print("Failed to create street network. Trying a smaller area...")
    # Try with a smaller area (bounding box)
    bbox = boundary.geometry.iloc[0].bounds  # (minx, miny, maxx, maxy)
    smaller_polygon = box(bbox[0], bbox[1], bbox[2], bbox[3])
    G = get_street_network(smaller_polygon)

# %%
# Incorrect:
G = boundary  # This is wrong!

# Correct:
G = ox.graph_from_polygon(boundary.geometry.iloc[0])

# %%
def analyze_network(G):
    if not hasattr(G, 'nodes'):
        raise ValueError("Expected a NetworkX graph")
    # Your analysis code here

# Call it like this:
if G is not None:
    analyze_network(G)

# %%
def is_valid_graph(G):
    """Check if G is a valid NetworkX graph."""
    if G is None:
        return False
    if not hasattr(G, 'nodes') or not hasattr(G, 'edges'):
        return False
    if not hasattr(G, 'is_directed'):
        return False
    return True

# Before using G:
if not is_valid_graph(G):
    print("Error: Invalid graph object")
    # Handle the error or try to recreate the graph
else:
    # Safe to use G
    print(f"Graph has {len(G.nodes())} nodes and {len(G.edges())} edges")

# %%
import osmnx as ox
import networkx as nx
from shapely.geometry import box

# 1. Get a small test area (Central Park, Manhattan)
north, south = 40.8006, 40.7644
east, west = -73.9584, -74.0018
test_area = box(west, south, east, north)

# 2. Get the street network
G = ox.graph_from_polygon(test_area, network_type='walk')

# 3. Verify
print(f"Graph type: {type(G)}")
print(f"Nodes: {len(G.nodes())}, Edges: {len(G.edges())}")
print(f"Is directed: {G.is_directed()}")

# %%
def calculate_accessibility(G, parks, sample_points=100):
    """
    Calculate accessibility metrics for sample points.
    
    Args:
        G: NetworkX graph (street network)
        parks: GeoDataFrame of park locations
        sample_points: Number of points to sample
        
    Returns:
        GeoDataFrame with accessibility metrics
    """
    import numpy as np
    from shapely.geometry import Point
    
    # Sample points within the boundary
    minx, miny, maxx, maxy = parks.total_bounds
    x = np.random.uniform(minx, maxx, sample_points)
    y = np.random.uniform(miny, maxy, sample_points)
    points = gpd.GeoSeries([Point(xy) for xy in zip(x, y)], crs=parks.crs)
    
    results = []
    for point in points:
        try:
            # Find nearest node in the graph
            orig_node = ox.distance.nearest_nodes(G, point.x, point.y)
            
            # Find nearest park
            nearest_park = parks.distance(point).idxmin()
            park_centroid = parks.loc[nearest_park].geometry.centroid
            dest_node = ox.distance.nearest_nodes(G, park_centroid.x, park_centroid.y)
            
            # Calculate shortest path
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            travel_time = nx.path_weight(G, route, weight='length') / (5000/60)  # 5 km/h in m/min
            
            results.append({
                'geometry': point,
                'nearest_park': nearest_park,
                'travel_time': travel_time
            })
            
        except Exception as e:
            print(f"Error processing point {point}: {e}")
            continue
    
    return gpd.GeoDataFrame(results, crs=parks.crs)

# Run the analysis
print("Starting accessibility analysis...")
accessibility = calculate_accessibility(G, parks)
print(f"Analysis complete! Processed {len(accessibility)} points.")

# Show basic statistics
if not accessibility.empty:
    print("\nAccessibility Statistics:")
    print(f"Average travel time: {accessibility['travel_time'].mean():.1f} minutes")
    print(f"Minimum travel time: {accessibility['travel_time'].min():.1f} minutes")
    print(f"Maximum travel time: {accessibility['travel_time'].max():.1f} minutes")
    
    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(accessibility['travel_time'], bins=20, edgecolor='black')
    plt.title('Distribution of Travel Times to Nearest Park')
    plt.xlabel('Travel Time (minutes)')
    plt.ylabel('Number of Points')
    plt.grid(True, alpha=0.3)
    plt.show()
else:
    print("No valid accessibility results to display.")

# %%
def plot_accessibility(accessibility, boundary, parks, G):
    """Create an interactive map of accessibility results using folium."""
    # Create base map centered on the boundary
    centroid = boundary.geometry.centroid
    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=14,
        tiles='cartodbpositron'
    )
    
    # Add boundary
    folium.GeoJson(
        boundary,
        style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
    ).add_to(m)
    
    # Add street network (simplified for performance)
    nodes, edges = ox.graph_to_gdfs(G)
    folium.GeoJson(
        edges,
        style_function=lambda x: {'color': '#999999', 'weight': 1, 'opacity': 0.5}
    ).add_to(m)
    
    # Add parks
    for _, park in parks.iterrows():
        folium.GeoJson(
            park.geometry,
            style_function=lambda x: {
                'fillColor': 'green',
                'color': 'darkgreen',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=f"Park: {park.get('name', 'Unnamed')}"
        ).add_to(m)
    
    # Add sample points colored by travel time
    if not accessibility.empty:
        max_time = accessibility['travel_time'].max()
        for _, row in accessibility.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=5,
                color='black',
                weight=1,
                fill_color=plt.cm.viridis(row['travel_time'] / max_time),
                fill_opacity=0.7,
                popup=f"Time: {row['travel_time']:.1f} min"
            ).add_to(m)
    
    return m

# Create and display the map
if not accessibility.empty:
    m = plot_accessibility(accessibility, boundary, parks, G)
    display(m)
    m.save('accessibility_map.html')
    print("Interactive map saved as 'accessibility_map.html'")
else:
    print("No accessibility data to plot.")

# %%
def is_graph_simplified(G):
    """Check if the graph has already been simplified."""
    return 'simplified' in G.graph and G.graph['simplified']

def plot_accessibility(accessibility, boundary, parks, G):
    """Create an interactive map of accessibility results using folium."""
    # Create base map centered on the boundary
    centroid = boundary.geometry.centroid
    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=14,
        tiles='cartodbpositron'
    )
    
    # Add boundary
    folium.GeoJson(
        boundary,
        style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
    ).add_to(m)
    
    # Convert graph to GeoDataFrame for plotting
    if not is_graph_simplified(G):
        try:
            G = ox.simplify_graph(G)
        except Exception as e:
            print(f"Could not simplify graph: {e}")
    
    # Convert to GeoDataFrame
    try:
        nodes, edges = ox.graph_to_gdfs(G)
        folium.GeoJson(
            edges,
            style_function=lambda x: {'color': '#999999', 'weight': 1, 'opacity': 0.5}
        ).add_to(m)
    except Exception as e:
        print(f"Could not plot street network: {e}")
    
    # Rest of your plotting code...
    # Add parks
    for _, park in parks.iterrows():
        folium.GeoJson(
            park.geometry,
            style_function=lambda x: {
                'fillColor': 'green',
                'color': 'darkgreen',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=f"Park: {park.get('name', 'Unnamed')}"
        ).add_to(m)
    
    # Add sample points colored by travel time
    if not accessibility.empty:
        max_time = accessibility['travel_time'].max()
        for _, row in accessibility.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=5,
                color='black',
                weight=1,
                fill_color=plt.cm.viridis(row['travel_time'] / max_time),
                fill_opacity=0.7,
                popup=f"Time: {row['travel_time']:.1f} min"
            ).add_to(m)
    
    return m

# Now you can safely call the function
if not accessibility.empty:
    m = plot_accessibility(accessibility, boundary, parks, G)
    display(m)
    m.save('accessibility_map.html')
    print("Interactive map saved as 'accessibility_map.html'")
else:
    print("No accessibility data to plot.")

# %%
def verify_graph(G):
    """Verify if G is a valid NetworkX graph."""
    if G is None:
        print("Error: Graph is None")
        return False
    if not hasattr(G, 'nodes') or not hasattr(G, 'edges'):
        print(f"Error: Not a valid graph. Type: {type(G)}")
        return False
    print(f"Graph verified: {len(G.nodes())} nodes, {len(G.edges())} edges")
    return True

# Check the graph
if not verify_graph(G):
    # Recreate the graph if it's invalid
    print("Recreating graph...")
    G = ox.graph_from_polygon(boundary.geometry.iloc[0], network_type='walk')
    verify_graph(G)

# %%
def calculate_accessibility(G, parks, sample_points=100):
    """Calculate accessibility metrics with better error handling."""
    if not verify_graph(G):
        raise ValueError("Invalid graph provided")
    
    # Convert boundary to GeoDataFrame if it's a Polygon
    if hasattr(boundary, 'geometry'):
        boundary_gdf = boundary
    else:
        boundary_gdf = gpd.GeoDataFrame(geometry=[boundary], crs="EPSG:4326")
    
    # Sample points within boundary
    minx, miny, maxx, maxy = boundary_gdf.total_bounds
    x = np.random.uniform(minx, maxx, sample_points)
    y = np.random.uniform(miny, maxy, sample_points)
    points = gpd.GeoSeries([Point(xy) for xy in zip(x, y)], crs=boundary_gdf.crs)
    
    results = []
    for point in points:
        try:
            # Ensure we have valid coordinates
            if np.isnan(point.x) or np.isnan(point.y):
                continue
                
            # Find nearest node in graph
            orig_node = ox.distance.nearest_nodes(G, point.x, point.y)
            
            # Find nearest park
            nearest_park = parks.distance(point).idxmin()
            park_centroid = parks.loc[nearest_park].geometry.centroid
            dest_node = ox.distance.nearest_nodes(G, park_centroid.x, park_centroid.y)
            
            # Calculate path
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            travel_time = nx.path_weight(G, route, weight='length') / (5000/60)  # 5 km/h in m/min
            
            results.append({
                'geometry': point,
                'nearest_park': nearest_park,
                'travel_time': travel_time
            })
            
        except Exception as e:
            print(f"Skipping point {point}: {str(e)}")
            continue
    
    if not results:
        raise ValueError("No valid points could be processed")
    
    return gpd.GeoDataFrame(results, crs=boundary_gdf.crs)

# %%
import sys
import osmnx as ox
import networkx as nx
import geopandas as gpd

print("Python version:", sys.version)
print("OSMnx version:", ox.__version__)
print("NetworkX version:", nx.__version__)
print("GeoPandas version:", gpd.__version__)
print("Graph type:", type(G))
print("Graph nodes:", len(G.nodes()) if G else "N/A")
print("Graph edges:", len(G.edges()) if G else "N/A")

# %%
def analyze_temporal_accessibility(G, boundary, parks, time_of_day='day', sample_points=50):
    """Analyze accessibility at different times of day."""
    # Set speed factor based on time of day
    if time_of_day == 'night':
        speed_factor = 0.8  # 20% slower at night
    elif time_of_day == 'peak':
        speed_factor = 0.7  # 30% slower during peak hours
    else:  # day
        speed_factor = 1.0

    # Get boundary polygon
    if hasattr(boundary, 'geometry'):
        polygon = boundary.geometry.unary_union
    else:
        polygon = boundary

    # Generate random points within the boundary
    minx, miny, maxx, maxy = polygon.bounds
    x = np.random.uniform(minx, maxx, sample_points * 2)  # Generate extra points to account for those that might be outside
    y = np.random.uniform(miny, maxy, sample_points * 2)
    points = gpd.GeoSeries([Point(xy) for xy in zip(x, y)], crs=boundary.crs if hasattr(boundary, 'crs') else "EPSG:4326")
    
    # Filter points to be within boundary
    points = points[points.intersects(polygon)].head(sample_points)
    
    results = []
    for point in points.geoms:
        try:
            # Find nearest node in the graph
            orig_node = ox.distance.nearest_nodes(G, point.x, point.y)
            
            # Find nearest park
            nearest_park = parks.distance(point).idxmin()
            park_centroid = parks.loc[nearest_park].geometry.centroid
            dest_node = ox.distance.nearest_nodes(G, park_centroid.x, park_centroid.y)
            
            # Calculate shortest path
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            base_time = nx.path_weight(G, route, weight='length') / (5000/60)  # 5 km/h in m/min
            adjusted_time = base_time / speed_factor
            
            results.append({
                'geometry': point,
                'time_minutes': adjusted_time,
                'time_period': time_of_day
            })
        except Exception as e:
            print(f"Skipping point due to error: {e}")
            continue
    
    return gpd.GeoDataFrame(results, crs=points.crs)

# Now you can run the analysis like this:
try:
    print("Analyzing daytime accessibility...")
    day_access = analyze_temporal_accessibility(G, boundary, parks, 'day')
    print(f"Daytime analysis complete: {len(day_access)} points processed")
    
    print("\nAnalyzing peak hour accessibility...")
    peak_access = analyze_temporal_accessibility(G, boundary, parks, 'peak')
    print(f"Peak hour analysis complete: {len(peak_access)} points processed")
    
    print("\nAnalyzing nighttime accessibility...")
    night_access = analyze_temporal_accessibility(G, boundary, parks, 'night')
    print(f"Nighttime analysis complete: {len(night_access)} points processed")

except Exception as e:
    print(f"Error in temporal analysis: {e}")
    print("Troubleshooting info:")
    print(f"- Graph type: {type(G)}")
    print(f"- Boundary type: {type(boundary)}")
    if hasattr(boundary, 'crs'):
        print(f"- Boundary CRS: {boundary.crs}")
    print(f"- Number of parks: {len(parks)}")

# %%
def analyze_temporal_accessibility(G, boundary, parks, time_of_day='day', sample_points=50):
    """Analyze accessibility at different times of day with proper GeoPandas handling."""
    # Set speed factor based on time of day
    if time_of_day == 'night':
        speed_factor = 0.8  # 20% slower at night
    elif time_of_day == 'peak':
        speed_factor = 0.7  # 30% slower during peak hours
    else:  # day
        speed_factor = 1.0

    # Get boundary polygon
    if hasattr(boundary, 'geometry'):
        polygon = boundary.geometry.unary_union
    else:
        polygon = boundary

    # Generate random points within the boundary
    minx, miny, maxx, maxy = polygon.bounds
    x = np.random.uniform(minx, maxx, sample_points * 2)
    y = np.random.uniform(miny, maxy, sample_points * 2)
    
    # Create GeoDataFrame of points
    points = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(x, y),
        crs=boundary.crs if hasattr(boundary, 'crs') else "EPSG:4326"
    )
    
    # Filter points to be within boundary
    points = points[points.intersects(polygon)].head(sample_points)
    
    results = []
    for _, row in points.iterrows():
        point = row.geometry
        try:
            # Find nearest node in the graph
            orig_node = ox.distance.nearest_nodes(G, point.x, point.y)
            
            # Find nearest park
            nearest_park_idx = parks.distance(point).idxmin()
            park_centroid = parks.loc[nearest_park_idx].geometry.centroid
            dest_node = ox.distance.nearest_nodes(G, park_centroid.x, park_centroid.y)
            
            # Calculate shortest path
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            base_time = nx.path_weight(G, route, weight='length') / (5000/60)  # 5 km/h in m/min
            adjusted_time = base_time / speed_factor
            
            results.append({
                'geometry': point,
                'time_minutes': adjusted_time,
                'time_period': time_of_day
            })
        except Exception as e:
            print(f"Skipping point ({point.x:.4f}, {point.y:.4f}) due to: {e}")
            continue
    
    if not results:
        raise ValueError("No valid points could be processed")
    
    return gpd.GeoDataFrame(results, crs=points.crs)

# Run the analysis with proper error handling
try:
    print("Analyzing daytime accessibility...")
    day_access = analyze_temporal_accessibility(G, boundary, parks, 'day')
    print(f"Daytime analysis complete: {len(day_access)} points processed")
    
    print("\nAnalyzing peak hour accessibility...")
    peak_access = analyze_temporal_accessibility(G, boundary, parks, 'peak')
    print(f"Peak hour analysis complete: {len(peak_access)} points processed")
    
    print("\nAnalyzing nighttime accessibility...")
    night_access = analyze_temporal_accessibility(G, boundary, parks, 'night')
    print(f"Nighttime analysis complete: {len(night_access)} points processed")

    # Combine results for visualization
    all_access = pd.concat([day_access, peak_access, night_access], ignore_index=True)
    print(f"\nTotal points analyzed: {len(all_access)}")

except Exception as e:
    print(f"Error in temporal analysis: {e}")
    import traceback
    traceback.print_exc()

# %%
def check_types(G, boundary, parks):
    print("=== Data Types ===")
    print(f"G (graph): {type(G)}")
    if G is not None:
        print(f"  - Is directed: {G.is_directed() if hasattr(G, 'is_directed') else 'N/A'}")
        print(f"  - Nodes: {len(G.nodes()) if hasattr(G, 'nodes') else 'N/A'}")
    
    print(f"\nBoundary: {type(boundary)}")
    if hasattr(boundary, 'geometry'):
        print(f"  - CRS: {boundary.crs}")
        print(f"  - Bounds: {boundary.total_bounds}")
    
    print(f"\nParks: {type(parks)}")
    if hasattr(parks, 'crs'):
        print(f"  - CRS: {parks.crs}")
    if hasattr(parks, 'geometry'):
        print(f"  - Number of parks: {len(parks)}")

# Run the check
check_types(G, boundary, parks)

# %%
def verify_graph(G):
    """Check if G is a valid NetworkX graph."""
    if not isinstance(G, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
        print(f"Error: Expected NetworkX graph, got {type(G)}")
        return False
    try:
        _ = len(G.nodes())
        _ = len(G.edges())
        return True
    except Exception as e:
        print(f"Graph validation error: {e}")
        return False

# Check the graph
if not verify_graph(G):
    print("Recreating graph...")
    G = ox.graph_from_place("Manhattan, New York, USA", network_type='walk')
    verify_graph(G)

# %%
def analyze_temporal_accessibility(G, boundary, parks, time_of_day='day', sample_points=50):
    """Analyze accessibility with robust type checking."""
    # Verify inputs
    if not verify_graph(G):
        raise ValueError("Invalid graph provided")
    
    if not isinstance(boundary, (gpd.GeoDataFrame, gpd.GeoSeries)):
        raise TypeError(f"boundary must be GeoDataFrame or GeoSeries, got {type(boundary)}")
    
    # Get boundary polygon
    polygon = boundary.geometry.unary_union if hasattr(boundary, 'geometry') else boundary
    
    # Generate points
    minx, miny, maxx, maxy = polygon.bounds
    x = np.random.uniform(minx, maxx, sample_points * 2)
    y = np.random.uniform(miny, maxy, sample_points * 2)
    
    # Create points GeoDataFrame
    points = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(x, y),
        crs=boundary.crs if hasattr(boundary, 'crs') else "EPSG:4326"
    )
    points = points[points.intersects(polygon)].head(sample_points)
    
    results = []
    for _, row in points.iterrows():
        point = row.geometry
        try:
            # Find nodes
            orig_node = ox.distance.nearest_nodes(G, point.x, point.y)
            nearest_park_idx = parks.distance(point).idxmin()
            park_centroid = parks.loc[nearest_park_idx].geometry.centroid
            dest_node = ox.distance.nearest_nodes(G, park_centroid.x, park_centroid.y)
            
            # Calculate path
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            travel_time = nx.path_weight(G, route, weight='length') / (5000/60)
            
            results.append({
                'geometry': point,
                'travel_time': travel_time,
                'time_period': time_of_day
            })
        except Exception as e:
            print(f"Point ({point.x:.4f}, {point.y:.4f}) skipped: {str(e)}")
            continue
    
    if not results:
        raise ValueError("No valid points processed")
    return gpd.GeoDataFrame(results, crs=points.crs)

# %%
try:
    # Verify data first
    print("Verifying data...")
    print(f"Graph type: {type(G)}")
    print(f"Boundary type: {type(boundary)}")
    print(f"Parks type: {type(parks)}")
    
    # Run analysis
    print("\nRunning analysis...")
    day_access = analyze_temporal_accessibility(G, boundary, parks, 'day')
    print(f"Daytime analysis complete: {len(day_access)} points")
    
    peak_access = analyze_temporal_accessibility(G, boundary, parks, 'peak')
    print(f"Peak hour analysis complete: {len(peak_access)} points")
    
    night_access = analyze_temporal_accessibility(G, boundary, parks, 'night')
    print(f"Nighttime analysis complete: {len(night_access)} points")
    
    # Combine results
    all_access = pd.concat([day_access, peak_access, night_access], ignore_index=True)
    print(f"\nTotal points analyzed: {len(all_access)}")
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nTroubleshooting info:")
    print(f"Graph nodes: {len(G.nodes()) if hasattr(G, 'nodes') else 'N/A'}")
    print(f"Graph edges: {len(G.edges()) if hasattr(G, 'edges') else 'N/A'}")
    print(f"Boundary CRS: {boundary.crs if hasattr(boundary, 'crs') else 'N/A'}")
    print(f"Number of parks: {len(parks) if hasattr(parks, '__len__') else 'N/A'}")
    print(f"OSMnx version: {ox.__version__}")
    print(f"GeoPandas version: {gpd.__version__}")

# %%
G = ox.graph_from_place("Manhattan, New York, USA", network_type='walk')
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# %%
print("Graph nodes:", len(G.nodes()))
print("Graph edges:", len(G.edges()))
print("Is graph directed?", G.is_directed() if hasattr(G, 'is_directed') else 'N/A')

# %%
print("Graph CRS:", G.graph['crs'] if 'crs' in G.graph else 'No CRS')
print("Boundary CRS:", boundary.crs)
print("Parks CRS:", parks.crs)

# %%
def plot_combined_accessibility(day_access, peak_access, night_access):
    """Create an interactive map showing all time periods."""
    # Create base map centered on the boundary
    centroid = boundary.geometry.centroid
    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=13,
        tiles='cartodbpositron'
    )
    
    # Add boundary
    folium.GeoJson(
        boundary,
        style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
    ).add_to(m)
    
    # Color scheme
    colors = {
        'day': 'green',
        'peak': 'orange',
        'night': 'purple'
    }
    
    # Add points for each time period
    for df, period in zip([day_access, peak_access, night_access], ['day', 'peak', 'night']):
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=5,
                color=colors[period],
                fill=True,
                fill_opacity=0.7,
                popup=f"Time: {row['travel_time']:.1f} min ({period})"
            ).add_to(m)
    
    # Add legend
    legend_html = '''
         <div style="position: fixed; 
                     bottom: 50px; left: 50px; width: 150px; height: 90px; 
                     border:2px solid grey; z-index:9999; font-size:14px;
                     background-color:white;
                     ">
         &nbsp; <strong>Time Period</strong> <br>
         &nbsp; <i class="fa fa-circle fa-1x" style="color:green"></i> Day<br>
         &nbsp; <i class="fa fa-circle fa-1x" style="color:orange"></i> Peak<br>
         &nbsp; <i class="fa fa-circle fa-1x" style="color:purple"></i> Night
          </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

# Generate the map
m = plot_combined_accessibility(day_access, peak_access, night_access)
display(m)
m.save('combined_accessibility_map.html')

# %%
def plot_travel_time_comparison(day_access, peak_access, night_access):
    """Create a boxplot comparing travel times across periods."""
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Combine data
    df = pd.concat([
        day_access[['travel_time']].assign(period='Day'),
        peak_access[['travel_time']].assign(period='Peak'),
        night_access[['travel_time']].assign(period='Night')
    ])
    
    # Create plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='period', y='travel_time', data=df, 
                order=['Day', 'Peak', 'Night'],
                palette=['green', 'orange', 'purple'])
    plt.title('Travel Time to Nearest Park by Time of Day')
    plt.xlabel('Time Period')
    plt.ylabel('Travel Time (minutes)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Print statistics
    print("\nTravel Time Statistics (minutes):")
    print(df.groupby('period')['travel_time'].describe().round(1))

# Generate the comparison
plot_travel_time_comparison(day_access, peak_access, night_access)

# %%
# Save results to files
day_access.to_file('day_access.gpkg', driver='GPKG')
peak_access.to_file('peak_access.gpkg', driver='GPKG')
night_access.to_file('night_access.gpkg', driver='GPKG')

# Save combined results
all_access = pd.concat([
    day_access[['geometry', 'travel_time']].assign(period='day'),
    peak_access[['geometry', 'travel_time']].assign(period='peak'),
    night_access[['geometry', 'travel_time']].assign(period='night')
], ignore_index=True)
all_access.to_file('all_access.gpkg', driver='GPKG')

print("Results saved to GPKG files")

# %%
def analyze_park_accessibility(parks, accessibility_data):
    """Analyze accessibility metrics by park."""
    # First, ensure we have the required 'nearest_park' column
    if 'nearest_park' not in accessibility_data.columns:
        print("Warning: 'nearest_park' column not found. Creating park indices...")
        # Find nearest park for each point if not already done
        from sklearn.neighbors import BallTree
        import numpy as np
        
        # Get park centroids
        park_centroids = np.array([[p.x, p.y] for p in parks.geometry.centroid])
        
        # Create BallTree for efficient nearest neighbor search
        tree = BallTree(park_centroids, leaf_size=2)
        
        # Find nearest park for each point
        points = np.array([[p.x, p.y] for p in accessibility_data.geometry])
        _, nearest_indices = tree.query(points, k=1)
        accessibility_data['nearest_park'] = nearest_indices.flatten()
    
    # Now proceed with the analysis
    park_stats = []
    
    for idx, park in parks.iterrows():
        # Find all access points for this park
        park_points = accessibility_data[accessibility_data['nearest_park'] == idx]
        
        if not park_points.empty:
            park_stats.append({
                'park_id': idx,
                'name': park.get('name', f'Park {idx}'),
                'area_sqkm': park.geometry.area / 1e6,
                'avg_travel_time': park_points['travel_time'].mean(),
                'min_travel_time': park_points['travel_time'].min(),
                'max_travel_time': park_points['travel_time'].max(),
                'access_points': len(park_points),
                'geometry': park.geometry.centroid
            })
    
    if not park_stats:
        print("Warning: No park statistics could be calculated")
        return gpd.GeoDataFrame(columns=['park_id', 'name', 'area_sqkm', 'avg_travel_time', 
                                       'min_travel_time', 'max_travel_time', 'access_points', 
                                       'geometry'], 
                              crs=parks.crs)
    
    return gpd.GeoDataFrame(park_stats, crs=parks.crs)

# Let's run it with error handling
try:
    print("Running park accessibility analysis...")
    park_access = analyze_park_accessibility(parks, all_access)
    print(f"Successfully analyzed {len(park_access)} parks")
    
    # Show a sample of the results
    if not park_access.empty:
        print("\nSample park statistics:")
        print(park_access[['name', 'area_sqkm', 'avg_travel_time', 'access_points']].head())
    else:
        print("No park statistics were generated")
        
except Exception as e:
    print(f"Error in park accessibility analysis: {e}")
    print("\nAvailable columns in accessibility data:", all_access.columns.tolist())
    print("Number of parks:", len(parks))
    print("Accessibility data sample:")
    print(all_access.head())

# %%
pip install panel

# %%
pip install --user panel

# %%
conda install -c conda-forge panel

# %%
import panel as pn
print(f"Panel version: {pn.__version__}")

# %%
import panel as pn
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

# Initialize Panel
pn.extension()

def create_interactive_dashboard(access_data, parks_data, boundary_data):
    """Create an interactive dashboard with park accessibility metrics."""
    # Ensure we have the required data
    if not all([hasattr(access_data, 'geometry'), 
               hasattr(parks_data, 'geometry'),
               hasattr(boundary_data, 'geometry')]):
        raise ValueError("Input data must be GeoDataFrames with geometry")
    
    # Create a copy of the data to avoid modifying the original
    access_df = access_data.copy()
    parks_df = parks_data.copy()
    
    # Add area if not present
    if 'area_sqkm' not in parks_df.columns:
        parks_df['area_sqkm'] = parks_df.geometry.area / 1e6
    
    # Create widgets
    time_period = pn.widgets.Select(
        name='Time Period', 
        options=['day', 'peak', 'night'],
        value='day'
    )
    
    park_size = pn.widgets.RangeSlider(
        name='Park Size (sq km)',
        start=0,
        end=float(parks_df['area_sqkm'].max() * 1.1),
        value=(0, float(parks_df['area_sqkm'].max())),
        step=0.1
    )
    
    @pn.depends(time_period, park_size)
    def update_map(period, size_range):
        # Filter data
        filtered_parks = parks_df[
            (parks_df['area_sqkm'] >= size_range[0]) & 
            (parks_df['area_sqkm'] <= size_range[1])
        ]
        
        # Create map
        m = folium.Map(
            location=[boundary_data.geometry.centroid.y, boundary_data.geometry.centroid.x],
            zoom_start=12,
            tiles='cartodbpositron'
        )
        
        # Add boundary
        folium.GeoJson(
            boundary_data,
            style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
        ).add_to(m)
        
        # Add parks
        for _, park in filtered_parks.iterrows():
            folium.CircleMarker(
                location=[park.geometry.centroid.y, park.geometry.centroid.x],
                radius=park['area_sqkm'] * 5,  # Scale marker size
                color='green',
                fill=True,
                fill_opacity=0.6,
                popup=f"""
                    <b>{park.get('name', 'Unnamed Park')}</b><br>
                    Area: {park['area_sqkm']:.2f} sq km
                """
            ).add_to(m)
        
        # Add accessibility points for selected time period
        period_data = access_df[access_df['time_period'] == period]
        if not period_data.empty:
            for _, row in period_data.iterrows():
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=3,
                    color='red',
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"Travel time: {row['travel_time']:.1f} min"
                ).add_to(m)
        
        return m
    
    # Create the dashboard
    dashboard = pn.Column(
        "## Park Accessibility Dashboard",
        pn.Row(
            pn.WidgetBox(
                "### Controls",
                time_period,
                park_size,
                width=300
            ),
            pn.panel(update_map, loading_indicator=True)
        )
    )
    
    return dashboard

# Run the dashboard with error handling
try:
    # Check if we have the required data
    if 'all_access' not in locals() or 'parks' not in locals() or 'boundary' not in locals():
        raise NameError("Required data not found. Please ensure 'all_access', 'parks', and 'boundary' are defined.")
    
    # Create and display the dashboard
    dashboard = create_interactive_dashboard(all_access, parks, boundary)
    display(dashboard)
    
except Exception as e:
    print(f"Error creating dashboard: {e}")
    print("\nTroubleshooting info:")
    print(f"all_access exists: {'all_access' in locals()}")
    print(f"parks exists: {'parks' in locals()}")
    print(f"boundary exists: {'boundary' in locals()}")
    
    if 'all_access' in locals():
        print("\nall_access columns:", all_access.columns.tolist())
        print("Sample data:\n", all_access.head())
    
    if 'parks' in locals():
        print("\nParks columns:", parks.columns.tolist())
        print("Number of parks:", len(parks))
    
    if 'boundary' in locals():
        print("\nBoundary type:", type(boundary))
        print("Boundary CRS:", boundary.crs)

# %%
pip install jupyter_bokeh

# %%
conda install -c conda-forge jupyter_bokeh

# %%
def create_park_access(parks, all_access):
    """Create park accessibility metrics."""
    # Ensure we have a unique identifier for each park
    if 'park_id' not in parks.columns:
        parks = parks.reset_index().rename(columns={'index': 'park_id'})
    
    # Calculate park areas if not already present
    if 'area_sqkm' not in parks.columns:
        parks['area_sqkm'] = parks.geometry.area / 1e6
    
    # Find nearest park for each access point if not already done
    if 'nearest_park' not in all_access.columns:
        from sklearn.neighbors import NearestNeighbors
        import numpy as np
        
        # Get park centroids
        park_centroids = np.array([[p.x, p.y] for p in parks.geometry.centroid])
        
        # Find nearest park for each access point
        access_points = np.array([[p.x, p.y] for p in all_access.geometry])
        nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(park_centroids)
        distances, indices = nbrs.kneighbors(access_points)
        all_access['nearest_park'] = indices.flatten()
    
    # Calculate park statistics
    park_stats = []
    for park_id, park in parks.iterrows():
        # Get all access points for this park
        park_access = all_access[all_access['nearest_park'] == park_id]
        
        if not park_access.empty:
            park_stats.append({
                'park_id': park_id,
                'name': park.get('name', f'Park {park_id}'),
                'area_sqkm': park['area_sqkm'],
                'avg_travel_time': park_access['travel_time'].mean(),
                'min_travel_time': park_access['travel_time'].min(),
                'max_travel_time': park_access['travel_time'].max(),
                'num_access_points': len(park_access),
                'geometry': park.geometry.centroid
            })
    
    return gpd.GeoDataFrame(park_stats, crs=parks.crs)

# Create the park_access DataFrame
try:
    park_access = create_park_access(parks, all_access)
    print(f"Created park_access with {len(park_access)} parks")
    print(park_access.head())
    
    # Now you can run your dashboard code
    import panel as pn
    import folium
    from folium.plugins import MarkerCluster
    
    pn.extension('ipywidgets')
    
    # Create interactive widgets
    time_period = pn.widgets.Select(
        name='Time Period', 
        options=['Day', 'Peak', 'Night'],
        value='Day'
    )
    
    park_size = pn.widgets.RangeSlider(
        name='Park Size (sq km)', 
        start=0, 
        end=float(park_access['area_sqkm'].max() * 1.1),
        value=(0, float(park_access['area_sqkm'].max())),
        step=0.1
    )
    
    @pn.depends(time_period, park_size)
    def update_map(period, size_range):
        period_lower = period.lower()
        period_data = all_access[all_access['time_period'] == period_lower]
        filtered_parks = park_access[
            (park_access['area_sqkm'] >= size_range[0]) & 
            (park_access['area_sqkm'] <= size_range[1])
        ]
        
        m = folium.Map(
            location=[boundary.geometry.centroid.y, boundary.geometry.centroid.x],
            zoom_start=13,
            tiles='cartodbpositron'
        )
        
        # Add boundary
        folium.GeoJson(
            boundary,
            style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
        ).add_to(m)
        
        # Add parks
        for _, park in filtered_parks.iterrows():
            folium.CircleMarker(
                location=[park.geometry.y, park.geometry.x],
                radius=park['area_sqkm'] * 5,  # Scale marker size by area
                color='green',
                fill=True,
                fill_opacity=0.6,
                popup=f"""
                    <b>{park['name']}</b><br>
                    Area: {park['area_sqkm']:.2f} sq km<br>
                    Avg Time: {park['avg_travel_time']:.1f} min
                """
            ).add_to(m)
        
        return m
    
    # Create dashboard
    dashboard = pn.Column(
        "## Park Accessibility Dashboard",
        pn.Row(
            pn.WidgetBox(
                "### Filters",
                time_period,
                park_size,
                width=300
            ),
            pn.panel(update_map, loading_indicator=True)
        )
    )
    
    # Display the dashboard
    display(dashboard)
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting info:")
    print(f"parks exists: {'parks' in locals()}")
    print(f"all_access exists: {'all_access' in locals()}")
    print(f"boundary exists: {'boundary' in locals()}")
    
    if 'parks' in locals():
        print("\nParks columns:", parks.columns.tolist())
    
    if 'all_access' in locals():
        print("\nall_access columns:", all_access.columns.tolist())

# %%
# 1. Check environment
import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
import networkx as nx
from shapely.geometry import Point

print("Environment check:")
print(f"OSMnx version: {ox.__version__}")
print(f"GeoPandas version: {gpd.__version__}")
print(f"NetworkX version: {nx.__version__}")

# 2. Download data for a smaller area first
print("\nDownloading data for a smaller area (Lower Manhattan)...")
try:
    # Start with a smaller area
    place_name = "Lower Manhattan, New York, USA"
    
    # Get boundary
    boundary = ox.geocode_to_gdf(place_name)
    print(f"Boundary loaded: {boundary.crs}")
    
    # Get parks
    parks = ox.features_from_place(place_name, tags={'leisure': 'park'})
    parks = gpd.GeoDataFrame(geometry=parks.geometry, crs=parks.crs)
    print(f"Found {len(parks)} parks")
    
    # Get street network
    G = ox.graph_from_place(place_name, network_type='walk')
    print(f"Street network: {len(G.nodes())} nodes, {len(G.edges())} edges")
    
    # Convert to UTM for accurate distance calculations
    utm_crs = ox.dd.determine_utm_crs(boundary.centroid.y[0], boundary.centroid.x[0])
    boundary = boundary.to_crs(utm_crs)
    parks = parks.to_crs(utm_crs)
    G = ox.project_graph(G, to_crs=utm_crs)
    
    print("\nData loaded successfully!")
    print(f"Boundary CRS: {boundary.crs}")
    print(f"Parks CRS: {parks.crs}")
    print(f"Graph CRS: {G.graph['crs'] if 'crs' in G.graph else 'No CRS in graph'}")
    
except Exception as e:
    print(f"Error loading data: {e}")
    print("\nTroubleshooting steps:")
    print("1. Check your internet connection")
    print("2. Try a smaller area (e.g., 'Financial District, Manhattan')")
    print("3. Verify package versions with: pip show osmnx geopandas networkx")

# %%
# Continue with the successful graph creation
try:
    # Get the boundary from the graph
    nodes, edges = ox.graph_to_gdfs(G)
    boundary = nodes.unary_union.convex_hull
    boundary = gpd.GeoDataFrame(geometry=[boundary], crs=G.graph['crs'])
    
    # Get parks within the graph's boundary
    parks = ox.features_from_polygon(boundary.geometry[0], tags={'leisure': 'park'})
    parks = gpd.GeoDataFrame(geometry=parks.geometry, crs=G.graph['crs'])
    print(f"Found {len(parks)} parks in the area")
    
    # Visualize
    print("\nVisualizing the data...")
    fig, ax = plt.subplots(figsize=(12, 12))
    ox.plot_graph(G, ax=ax, node_size=0, edge_linewidth=0.5, show=False, close=False)
    boundary.plot(ax=ax, color='none', edgecolor='red', linewidth=2)
    if not parks.empty:
        parks.plot(ax=ax, color='green', alpha=0.5, markersize=50)
    plt.title("Street Network (black), Parks (green), Boundary (red)")
    plt.show()
    
    print("\nReady for accessibility analysis!")
    print("Variables available:")
    print(f"- G: Street network with {len(G.nodes())} nodes")
    print(f"- parks: {len(parks)} parks in the area")
    print(f"- boundary: Study area boundary")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nLet me know if you'd like to try a different approach or area.")

# %%
import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point

# 1. Download data for Manhattan
print("Downloading data for Manhattan...")
place_name = "Manhattan, New York, USA"

# Get boundary
boundary = ox.geocode_to_gdf(place_name)
print(f"Boundary loaded: {boundary.crs}")

# Get parks
parks = ox.features_from_place(place_name, tags={'leisure': 'park'})
parks = gpd.GeoDataFrame(geometry=parks.geometry, crs=parks.crs)  # Ensure proper GeoDataFrame
parks['area_sqkm'] = parks.geometry.area / 1e6
print(f"Found {len(parks)} parks")

# Get street network
G = ox.graph_from_place(place_name, network_type='walk')
print(f"Street network: {len(G.nodes())} nodes, {len(G.edges())} edges")

# 2. Sample points and calculate accessibility
def calculate_accessibility(G, boundary, parks, sample_points=100):
    """Calculate accessibility metrics for sample points."""
    # Sample points within boundary
    minx, miny, maxx, maxy = boundary.total_bounds
    x = np.random.uniform(minx, maxx, sample_points * 2)
    y = np.random.uniform(miny, maxy, sample_points * 2)
    
    # Create points and filter
    points = [Point(xy) for xy in zip(x, y)]
    points_gdf = gpd.GeoDataFrame(geometry=points, crs=boundary.crs)
    points_gdf = points_gdf[points_gdf.within(boundary.geometry[0])].head(sample_points)
    
    results = []
    for _, point in points_gdf.iterrows():
        try:
            # Find nearest node in graph
            orig_node = ox.distance.nearest_nodes(G, point.geometry.x, point.geometry.y)
            
            # Find nearest park
            nearest_park_idx = parks.distance(point.geometry).idxmin()
            park_centroid = parks.loc[nearest_park_idx].geometry.centroid
            dest_node = ox.distance.nearest_nodes(G, park_centroid.x, park_centroid.y)
            
            # Calculate path
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            travel_time = nx.path_weight(G, route, weight='length') / (5000/60)  # 5 km/h in m/min
            
            results.append({
                'geometry': point.geometry,
                'nearest_park': nearest_park_idx,
                'travel_time': travel_time,
                'time_period': 'day'  # Default time period
            })
        except Exception as e:
            print(f"Skipping point: {e}")
            continue
    
    # Create GeoDataFrame with geometry
    if results:
        return gpd.GeoDataFrame(results, geometry='geometry', crs=boundary.crs)
    return gpd.GeoDataFrame(geometry=gpd.GeoSeries(crs=boundary.crs))

# Calculate accessibility
print("\nCalculating accessibility...")
all_access = calculate_accessibility(G, boundary, parks)
print(f"Calculated accessibility for {len(all_access)} points")

# 3. Create park_access DataFrame
print("\nCreating park statistics...")
park_stats = []
for park_idx, park in parks.iterrows():
    park_points = all_access[all_access['nearest_park'] == park_idx]
    if not park_points.empty:
        park_stats.append({
            'park_id': park_idx,
            'name': f"Park {park_idx}",
            'area_sqkm': park['area_sqkm'],
            'avg_travel_time': park_points['travel_time'].mean(),
            'num_access_points': len(park_points),
            'geometry': park.geometry.centroid
        })

# Create GeoDataFrame with geometry
if park_stats:
    park_access = gpd.GeoDataFrame(park_stats, geometry='geometry', crs=parks.crs)
else:
    park_access = gpd.GeoDataFrame(columns=['park_id', 'name', 'area_sqkm', 'avg_travel_time', 'num_access_points'],
                                 geometry=gpd.GeoSeries(crs=parks.crs))

print(f"Created statistics for {len(park_access)} parks")

# 4. Verify the data
print("\nVerifying data...")
print(f"all_access CRS: {all_access.crs if not all_access.empty else 'Empty'}")
print(f"park_access CRS: {park_access.crs if not park_access.empty else 'Empty'}")
print(f"parks CRS: {parks.crs}")

# 5. Now you can run the dashboard code
print("\nSetup complete! You can now run the dashboard code.")

# %%
# Test Panel installation
try:
    test_dashboard = pn.pane.Markdown("## Test Dashboard")
    display(test_dashboard)
    test_dashboard.save('test_dashboard.html')
    print("Test dashboard created and saved successfully.")
except Exception as e:
    print(f"Panel test failed: {e}")

# %%
def create_dashboard(G, parks, boundary, all_access):
    """Create an interactive dashboard for park accessibility analysis."""
    try:
        # Project to UTM for accurate calculations
        utm_crs = "EPSG:32618"  # NYC UTM zone
        boundary_proj = boundary.to_crs(utm_crs)
        parks_proj = parks.to_crs(utm_crs)
        
        # Calculate park areas in projected CRS
        if 'area_sqkm' not in parks_proj.columns:
            parks_proj['area_sqkm'] = parks_proj.geometry.area / 1e6
        
        # Get valid area range
        max_area = float(max(parks_proj['area_sqkm'].max() * 1.1, 0.1))  # Ensure > 0
        min_area = float(max(parks_proj['area_sqkm'].min() * 0.9, 0))
        
        # Ensure valid range
        if max_area <= min_area:
            max_area = min_area + 0.1
        
        # Convert to WGS84 for visualization
        boundary_wgs = boundary_proj.to_crs('EPSG:4326')
        parks_wgs = parks_proj.to_crs('EPSG:4326')
        
        # Get center from boundary
        center_geom = boundary_wgs.geometry.unary_union.centroid
        center_coords = [center_geom.y, center_geom.x]
        
        # Create widgets
        time_period = pn.widgets.Select(
            name='Time Period', 
            options=['Day', 'Peak', 'Night'],
            value='Day'
        )
        
        park_size = pn.widgets.RangeSlider(
            name='Park Size (sq km)',
            start=0,
            end=round(max_area, 1),
            value=(0, round(max_area, 1)),
            step=0.1
        )
        
        @pn.depends(time_period, park_size)
        def update_map(period, size_range):
            m = folium.Map(location=center_coords, zoom_start=14, tiles='cartodbpositron')
            
            # Add boundary
            folium.GeoJson(
                boundary_wgs.__geo_interface__,
                style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
            ).add_to(m)
            
            # Add parks
            if not parks_wgs.empty:
                mask = ((parks_proj['area_sqkm'] >= size_range[0]) & 
                       (parks_proj['area_sqkm'] <= size_range[1]))
                filtered_parks = parks_wgs[mask]
                
                for _, park in filtered_parks.iterrows():
                    folium.CircleMarker(
                        location=[park.geometry.centroid.y, park.geometry.centroid.x],
                        radius=5,
                        color='green',
                        fill=True,
                        fill_opacity=0.6,
                        popup=f"Park<br>Area: {park.get('area_sqkm', 'N/A'):.2f} sq km"
                    ).add_to(m)
            
            # Add accessibility points if available
            if all_access is not None and not all_access.empty:
                access_points = all_access[all_access['time_period'] == period.lower()]
                for _, point in access_points.iterrows():
                    folium.CircleMarker(
                        location=[point.geometry.y, point.geometry.x],
                        radius=3,
                        color='red',
                        fill=True,
                        fill_opacity=0.7,
                        popup=f"Travel time: {point.get('travel_time', 'N/A'):.1f} min"
                    ).add_to(m)
            
            return m
        
        # Create dashboard
        dashboard = pn.Column(
            "## Park Accessibility Dashboard",
            pn.Row(
                pn.WidgetBox(
                    "### Filters",
                    time_period,
                    park_size,
                    width=300
                ),
                pn.panel(update_map, loading_indicator=True)
            )
        )
        
        return dashboard
        
    except Exception as e:
        print(f"Error in create_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return pn.pane.Markdown(f"Error creating dashboard: {str(e)}")

# Create and display the dashboard
print("Creating dashboard with fixes...")
try:
    dashboard = create_dashboard(G, parks, boundary, all_access if 'all_access' in locals() else None)
    
    if dashboard is not None:
        display(dashboard)
        
        # Save to HTML
        try:
            dashboard.save('park_accessibility_dashboard.html')
            print("✅ Dashboard saved as 'park_accessibility_dashboard.html'")
        except Exception as e:
            print(f"❌ Error saving dashboard: {e}")
    else:
        print("❌ Error: Dashboard creation returned None")
    
except Exception as e:
    print(f"❌ Error creating dashboard: {e}")
    print("\nTroubleshooting info:")
    print(f"- G: {'✅ Available' if 'G' in locals() else '❌ Not available'}")
    print(f"- parks: {'✅ Available' if 'parks' in locals() else '❌ Not available'}")
    print(f"- boundary: {'✅ Available' if 'boundary' in locals() else '❌ Not available'}")
    print(f"- all_access: {'✅ Available' if 'all_access' in locals() else '❌ Not available'}")

# %%
def create_dashboard(G, parks, boundary, all_access):
    """Create an interactive dashboard for park accessibility analysis."""
    try:
        # Project to UTM for accurate calculations
        utm_crs = "EPSG:32618"  # NYC UTM zone
        boundary_proj = boundary.to_crs(utm_crs)
        parks_proj = parks.to_crs(utm_crs)
        
        # Calculate park areas in projected CRS if not already present
        if 'area_sqkm' not in parks_proj.columns:
            parks_proj['area_sqkm'] = parks_proj.geometry.area / 1e6  # Convert to km²
        
        # Get valid area range with safety checks
        min_area = float(parks_proj['area_sqkm'].min())
        max_area = float(parks_proj['area_sqkm'].max())
        
        # Ensure we have a valid range
        if min_area == max_area:
            if min_area == 0:
                min_area, max_area = 0, 1.0  # Default range if all areas are 0
            else:
                min_area = max(0, min_area * 0.9)  # 10% below min
                max_area = max_area * 1.1  # 10% above max
        
        # Round to 1 decimal place for cleaner display
        min_area = round(min_area, 1)
        max_area = round(max(max_area, min_area + 0.1), 1)  # Ensure max > min
        
        # Convert to WGS84 for visualization
        boundary_wgs = boundary_proj.to_crs('EPSG:4326')
        parks_wgs = parks_proj.to_crs('EPSG:4326')
        
        # Get center from boundary using unary_union to avoid CRS warning
        center_geom = boundary_wgs.geometry.unary_union.centroid
        center_coords = [center_geom.y, center_geom.x]
        
        # Create widgets
        time_period = pn.widgets.Select(
            name='Time Period', 
            options=['Day', 'Peak', 'Night'],
            value='Day'
        )
        
        # Create slider with guaranteed valid range
        park_size = pn.widgets.RangeSlider(
            name='Park Size (sq km)',
            start=min_area,
            end=max_area,
            value=(min_area, max_area),
            step=0.1
        )
        
        @pn.depends(time_period, park_size)
        def update_map(period, size_range):
            m = folium.Map(location=center_coords, zoom_start=14, tiles='cartodbpositron')
            
            # Add boundary
            folium.GeoJson(
                boundary_wgs.__geo_interface__,
                style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
            ).add_to(m)
            
            # Add parks
            if not parks_wgs.empty and 'area_sqkm' in parks_proj.columns:
                mask = ((parks_proj['area_sqkm'] >= size_range[0]) & 
                       (parks_proj['area_sqkm'] <= size_range[1]))
                filtered_parks = parks_wgs[mask]
                
                for _, park in filtered_parks.iterrows():
                    folium.CircleMarker(
                        location=[park.geometry.centroid.y, park.geometry.centroid.x],
                        radius=5,
                        color='green',
                        fill=True,
                        fill_opacity=0.6,
                        popup=f"Park<br>Area: {park.get('area_sqkm', 'N/A'):.2f} sq km"
                    ).add_to(m)
            
            # Add accessibility points if available
            if all_access is not None and not all_access.empty:
                access_points = all_access[all_access['time_period'] == period.lower()]
                for _, point in access_points.iterrows():
                    folium.CircleMarker(
                        location=[point.geometry.y, point.geometry.x],
                        radius=3,
                        color='red',
                        fill=True,
                        fill_opacity=0.7,
                        popup=f"Travel time: {point.get('travel_time', 'N/A'):.1f} min"
                    ).add_to(m)
            
            return m
        
        # Create dashboard
        dashboard = pn.Column(
            "## Park Accessibility Dashboard",
            pn.Row(
                pn.WidgetBox(
                    "### Filters",
                    time_period,
                    park_size,
                    width=300
                ),
                pn.panel(update_map, loading_indicator=True)
            )
        )
        
        return dashboard
        
    except Exception as e:
        print(f"Error in create_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return pn.pane.Markdown(f"Error creating dashboard: {str(e)}")

# Create and display the dashboard
print("Creating dashboard with fixed slider...")
try:
    dashboard = create_dashboard(G, parks, boundary, all_access if 'all_access' in locals() else None)
    
    if dashboard is not None:
        display(dashboard)
        
        # Save to HTML
        try:
            dashboard.save('park_accessibility_dashboard.html')
            print("✅ Dashboard saved as 'park_accessibility_dashboard.html'")
        except Exception as e:
            print(f"❌ Error saving dashboard: {e}")
    else:
        print("❌ Error: Dashboard creation returned None")
    
except Exception as e:
    print(f"❌ Error creating dashboard: {e}")
    print("\nTroubleshooting info:")
    print(f"- G: {'✅ Available' if 'G' in locals() else '❌ Not available'}")
    print(f"- parks: {'✅ Available' if 'parks' in locals() else '❌ Not available'}")
    print(f"- boundary: {'✅ Available' if 'boundary' in locals() else '❌ Not available'}")
    print(f"- all_access: {'✅ Available' if 'all_access' in locals() else '❌ Not available'}")

# %%
# Add progress indicator
import ipywidgets as widgets
from IPython.display import display as ipy_display

# Create a progress bar
progress = widgets.FloatProgress(
    value=0,
    min=0,
    max=100,
    description='Loading:',
    bar_style='info',
    style={'bar_color': '#0078D4'},
    orientation='horizontal'
)

def update_progress(step, total_steps=5):
    """Update the progress bar"""
    progress.value = (step / total_steps) * 100
    ipy_display(progress)

# Show initial progress
ipy_display(progress)
update_progress(1, 5)  # 20% - Starting

def create_dashboard(G, parks, boundary, all_access):
    """Create an interactive dashboard for park accessibility analysis."""
    try:
        update_progress(2, 5)  # 40% - Projecting data
        
        # First project to UTM for accurate distance calculations
        utm_crs = "EPSG:32618"  # Hardcoded for NYC area (Manhattan)
        
        # Project all data to UTM first
        boundary_proj = boundary.to_crs(utm_crs)
        parks_proj = parks.to_crs(utm_crs)
        
        # Calculate park areas in projected CRS
        if 'area_sqkm' not in parks_proj.columns:
            parks_proj['area_sqkm'] = parks_proj.geometry.area / 1e6  # Convert to km²
        
        # Get valid area range with safety checks
        min_area = float(parks_proj['area_sqkm'].min())
        max_area = float(parks_proj['area_sqkm'].max())
        
        # Ensure we have a valid range
        if min_area == max_area:
            if min_area == 0:
                min_area, max_area = 0, 1.0  # Default range if all areas are 0
            else:
                min_area = max(0, min_area * 0.9)  # 10% below min
                max_area = max_area * 1.1  # 10% above max
        
        # Round to 1 decimal place for cleaner display
        min_area = round(min_area, 1)
        max_area = round(max(max_area, min_area + 0.1), 1)  # Ensure max > min
        
        # Convert to WGS84 for visualization
        boundary_wgs = boundary_proj.to_crs('EPSG:4326')
        parks_wgs = parks_proj.to_crs('EPSG:4326')
        
        update_progress(3, 5)  # 60% - Data processed
        
        # Get center from boundary using unary_union to avoid CRS warning
        center_geom = boundary_wgs.geometry.unary_union.centroid
        center_coords = [center_geom.y, center_geom.x]
        
        update_progress(4, 5)  # 80% - UI setup
        
        # Create dashboard components
        time_period = pn.widgets.Select(
            name='Time Period', 
            options=['Day', 'Peak', 'Night'],
            value='Day'
        )
        
        # Create slider with guaranteed valid range
        park_size = pn.widgets.RangeSlider(
            name='Park Size (sq km)',
            start=min_area,
            end=max_area,
            value=(min_area, max_area),
            step=0.1
        )
        
        @pn.depends(time_period, park_size)
        def update_map(period, size_range):
            m = folium.Map(location=center_coords, zoom_start=14, tiles='cartodbpositron')
            
            # Add boundary
            folium.GeoJson(
                boundary_wgs.__geo_interface__,
                style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0}
            ).add_to(m)
            
            # Add parks
            if not parks_wgs.empty and 'area_sqkm' in parks_proj.columns:
                mask = ((parks_proj['area_sqkm'] >= size_range[0]) & 
                       (parks_proj['area_sqkm'] <= size_range[1]))
                filtered_parks = parks_wgs[mask]
                
                for _, park in filtered_parks.iterrows():
                    folium.CircleMarker(
                        location=[park.geometry.centroid.y, park.geometry.centroid.x],
                        radius=5,
                        color='green',
                        fill=True,
                        fill_opacity=0.6,
                        popup=f"Park<br>Area: {park.get('area_sqkm', 'N/A'):.2f} sq km"
                    ).add_to(m)
            
            # Add accessibility points if available
            if all_access is not None and not all_access.empty:
                access_points = all_access[all_access['time_period'] == period.lower()]
                for _, point in access_points.iterrows():
                    folium.CircleMarker(
                        location=[point.geometry.y, point.geometry.x],
                        radius=3,
                        color='red',
                        fill=True,
                        fill_opacity=0.7,
                        popup=f"Travel time: {point.get('travel_time', 'N/A'):.1f} min"
                    ).add_to(m)
            
            return m
        
        # Create dashboard layout
        dashboard = pn.Column(
            "## Park Accessibility Dashboard",
            pn.Row(
                pn.WidgetBox(
                    "### Filters",
                    time_period,
                    park_size,
                    width=300
                ),
                pn.panel(update_map, loading_indicator=True)
            )
        )
        
        update_progress(5, 5)  # 100% - Complete
        return dashboard
        
    except Exception as e:
        progress.bar_style = 'danger'
        progress.description = 'Error:'
        print(f"Error in create_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return pn.pane.Markdown(f"Error creating dashboard: {str(e)}")

# Create and display the dashboard
print("Creating dashboard with progress tracking...")
try:
    dashboard = create_dashboard(G, parks, boundary, all_access if 'all_access' in locals() else None)
    
    if dashboard is not None:
        display(dashboard)
        
        # Save to HTML
        try:
            print("Saving dashboard...")
            dashboard.save('park_accessibility_dashboard.html')
            print("✅ Dashboard saved as 'park_accessibility_dashboard.html'")
        except Exception as e:
            print(f"❌ Error saving dashboard: {e}")
    else:
        print("❌ Error: Dashboard creation returned None")
    
except Exception as e:
    print(f"❌ Error creating dashboard: {e}")
    print("\nTroubleshooting info:")
    print(f"- G: {'✅ Available' if 'G' in locals() else '❌ Not available'}")
    print(f"- parks: {'✅ Available' if 'parks' in locals() else '❌ Not available'}")
    print(f"- boundary: {'✅ Available' if 'boundary' in locals() else '❌ Not available'}")
    print(f"- all_access: {'✅ Available' if 'all_access' in locals() else '❌ Not available'}")

# %%
def create_isochrone_map(isochrones_wgs, boundary_wgs, parks_wgs):
    """Create a map showing isochrones and parks."""
    try:
        # Check if we have the required data
        if isochrones_wgs is None or isochrones_wgs.empty:
            raise ValueError("No isochrones data provided")
            
        # Check if we have a time column, if not create one
        if 'time' not in isochrones_wgs.columns and 'travel_time' in isochrones_wgs.columns:
            isochrones_wgs = isochrones_wgs.rename(columns={'travel_time': 'time'})
        elif 'time' not in isochrones_wgs.columns:
            # If no time column exists, create one with default values
            isochrones_wgs['time'] = range(5, 5 * len(isochrones_wgs) + 1, 5)  # 5, 10, 15, ... minutes

        # Reproject to UTM for accurate centroid calculation
        utm_crs = "EPSG:32618"  # For NYC area
        isochrones_utm = isochrones_wgs.to_crs(utm_crs)
        
        # Calculate centroids in UTM using the recommended union_all() method
        center_utm = isochrones_utm.geometry.centroid.union_all().centroid
        
        # Convert back to WGS84 for map center
        center_wgs = gpd.GeoDataFrame(geometry=[center_utm], crs=utm_crs).to_crs('EPSG:4326')
        center_coords = [center_wgs.geometry.y.iloc[0], center_wgs.geometry.x.iloc[0]]
        
        # Create the map
        m = folium.Map(
            location=center_coords,
            zoom_start=13,
            tiles='cartodbpositron'
        )
        
        # Add boundary
        folium.GeoJson(
            boundary_wgs.__geo_interface__,
            style_function=lambda x: {
                'color': 'blue',
                'weight': 2,
                'fillOpacity': 0
            }
        ).add_to(m)
        
        # Sort isochrones by time (ascending) so they stack correctly
        isochrones_wgs = isochrones_wgs.sort_values('time')
        
        # Add isochrones with color gradient
        colors = ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']  # Yellow to dark blue
        for idx, (_, row) in enumerate(isochrones_wgs.iterrows()):
            color = colors[idx % len(colors)]
            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda x, c=color: {
                    'fillColor': c,
                    'color': c,
                    'weight': 1,
                    'fillOpacity': 0.4
                },
                tooltip=f"<b>Travel Time:</b> {row['time']} min"
            ).add_to(m)
        
        # Add parks
        if not parks_wgs.empty:
            folium.GeoJson(
                parks_wgs.__geo_interface__,
                style_function=lambda x: {
                    'fillColor': 'green',
                    'color': 'green',
                    'weight': 1,
                    'fillOpacity': 0.6
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['name', 'area_sqkm'] if 'name' in parks_wgs.columns else ['area_sqkm'],
                    aliases=['Park', 'Area (sq km)'] if 'name' in parks_wgs.columns else ['Area (sq km)']
                )
            ).add_to(m)
        
        # Add legend
        legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 180px; height: auto; 
                        border:2px solid grey; z-index:9999; font-size:14px;
                        background-color:white; padding: 10px;">
                <p style="margin:5px 0 10px 0; font-weight:bold; text-align:center;">Travel Time (min)</p>
        '''
        for i, (_, row) in enumerate(isochrones_wgs.iterrows()):
            legend_html += f'''
                <p style="margin:5px 0;">
                    <i style="background:{colors[i % len(colors)]}; 
                             width:15px; height:15px; 
                             display:inline-block; 
                             margin-right:8px;
                             border:1px solid #666;">
                    </i>
                    {row["time"]} min
                </p>
            '''
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
        
    except Exception as e:
        print(f"Error creating isochrone map: {e}")
        import traceback
        traceback.print_exc()
        return None

# Create and display the map
print("Creating isochrone map...")
try:
    # Ensure we have isochrones data
    if 'isochrones_wgs' in locals() and not isochrones_wgs.empty:
        isochrone_map = create_isochrone_map(isochrones_wgs, boundary, parks)
        if isochrone_map:
            display(isochrone_map)
            isochrone_map.save('isochrones_map.html')
            print("✅ Isochrone map saved as 'isochrones_map.html'")
        else:
            print("❌ Failed to create isochrone map")
    else:
        print("❌ No isochrones data found. Please generate isochrones first.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting info:")
    print(f"- isochrones_wgs: {'✅ Available' if 'isochrones_wgs' in locals() else '❌ Not available'}")
    if 'isochrones_wgs' in locals():
        print(f"  - Empty: {'❌ Yes' if isochrones_wgs.empty else '✅ No'}")
        print(f"  - Columns: {list(isochrones_wgs.columns)}")
    print(f"- boundary: {'✅ Available' if 'boundary' in locals() else '❌ Not available'}")
    print(f"- parks: {'✅ Available' if 'parks' in locals() else '❌ Not available'}")

# %%
def create_web_map(access_data, parks, boundary):
    """Create a web map with accessibility data and parks."""
    try:
        # Create a copy of the data to avoid modifying the original
        access_data = access_data.copy()
        parks = parks.copy()
        boundary = boundary.copy()
        
        # Ensure all data is in WGS84 (EPSG:4326) for web mapping
        access_data = access_data.to_crs('EPSG:4326')
        parks = parks.to_crs('EPSG:4326')
        boundary = boundary.to_crs('EPSG:4326')
        
        # Calculate center in projected CRS first to avoid CRS warning
        utm_crs = "EPSG:32618"  # For NYC area
        boundary_utm = boundary.to_crs(utm_crs)
        center_utm = boundary_utm.geometry.centroid.iloc[0]
        center_wgs = gpd.GeoDataFrame(geometry=[center_utm], crs=utm_crs).to_crs('EPSG:4326')
        center = [center_wgs.geometry.y.iloc[0], center_wgs.geometry.x.iloc[0]]
        
        # Create the map
        m = folium.Map(
            location=center,
            zoom_start=13,
            tiles='cartodbpositron'
        )
        
        # Convert numeric columns to native Python types for JSON serialization
        for col in access_data.select_dtypes(include=['int64', 'float64']).columns:
            access_data[col] = access_data[col].astype(float)
        
        # Add boundary
        folium.GeoJson(
            boundary.__geo_interface__,
            style_function=lambda x: {
                'color': 'blue',
                'weight': 2,
                'fillOpacity': 0
            }
        ).add_to(m)
        
        # Add parks
        if not parks.empty:
            folium.GeoJson(
                parks.__geo_interface__,
                style_function=lambda x: {
                    'fillColor': 'green',
                    'color': 'green',
                    'weight': 1,
                    'fillOpacity': 0.5
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['name', 'area_sqkm'] if 'name' in parks.columns else ['area_sqkm'],
                    aliases=['Park', 'Area (sq km)'] if 'name' in parks.columns else ['Area (sq km)']
                )
            ).add_to(m)
        
        # Add accessibility points
        if not access_data.empty:
            # Define color scale based on travel time
            if 'travel_time' in access_data.columns:
                vmin = access_data['travel_time'].min()
                vmax = access_data['travel_time'].max()
                cmap = folium.LinearColormap(
                    ['#2b83ba', '#abdda4', '#ffffbf', '#fdae61', '#d7191c'],
                    vmin=vmin,
                    vmax=vmax,
                    caption='Travel Time (min)'
                )
                cmap.add_to(m)
                
                # Add points with color based on travel time
                for _, row in access_data.iterrows():
                    folium.CircleMarker(
                        location=[row.geometry.y, row.geometry.x],
                        radius=5,
                        color=cmap(row['travel_time']),
                        fill=True,
                        fill_opacity=0.7,
                        popup=f"Travel time: {row['travel_time']:.1f} min"
                    ).add_to(m)
            else:
                # Fallback if no travel_time column
                folium.GeoJson(
                    access_data.__geo_interface__,
                    style_function=lambda x: {
                        'color': 'red',
                        'weight': 1,
                        'fillOpacity': 0.7
                    }
                ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
        
    except Exception as e:
        print(f"Error in create_web_map: {e}")
        import traceback
        traceback.print_exc()
        return None

# Create and display the web map
print("Creating web map with proper CRS handling...")
try:
    web_map = create_web_map(
        all_access.copy() if 'all_access' in locals() else gpd.GeoDataFrame(),
        parks.copy() if 'parks' in locals() else gpd.GeoDataFrame(),
        boundary.copy() if 'boundary' in locals() else gpd.GeoDataFrame()
    )
    
    if web_map:
        display(web_map)
        web_map.save('park_accessibility_map.html')
        print("✅ Web map saved as 'park_accessibility_map.html'")
    else:
        print("❌ Failed to create web map")
        
except Exception as e:
    print(f"❌ Error creating web map: {e}")
    print("\nTroubleshooting info:")
    print(f"- all_access: {'✅ Available' if 'all_access' in locals() else '❌ Not available'}")
    if 'all_access' in locals():
        print(f"  - CRS: {all_access.crs}")
        print(f"  - Columns: {list(all_access.columns)}")
        print(f"  - Sample travel_time: {all_access['travel_time'].head(2).values if 'travel_time' in all_access.columns else 'N/A'}")
    print(f"- parks: {'✅ Available' if 'parks' in locals() else '❌ Not available'}")
    if 'parks' in locals():
        print(f"  - CRS: {parks.crs}")
    print(f"- boundary: {'✅ Available' if 'boundary' in locals() else '❌ Not available'}")
    if 'boundary' in locals():
        print(f"  - CRS: {boundary.crs}")

# %%
def optimize_analysis(G, boundary, sample_factor=0.1):
    """Optimize the analysis for large areas."""
    # Simplify the graph
    G_simplified = ox.simplify_graph(G)
    
    # Create a spatial index for faster queries
    import rtree
    idx = rtree.index.Index()
    for i, point in enumerate(all_access.geometry):
        idx.insert(i, (point.x, point.y, point.x, point.y))
    
    # Use parallel processing for large datasets
    from concurrent.futures import ProcessPoolExecutor
    
    def process_point(point):
        # Your processing logic here
        pass
    
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(process_point, all_access.geometry))
    
    return results  # Fixed indentation

# %%
pip install openpyxl

# %%
import os

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

# Export to multiple formats
all_access.to_file('output/accessibility_analysis.gpkg', driver='GPKG')
all_access.to_file('output/accessibility_analysis.geojson', driver='GeoJSON')

# Save statistics (CSV only)
stats = all_access.groupby('time_period')['travel_time'].describe()
stats.to_csv('output/accessibility_stats.csv')

# Save interactive HTML
web_map.save('output/interactive_map.html')

print("""
Analysis complete! Output files:
- output/accessibility_analysis.gpkg
- output/accessibility_analysis.geojson
- output/accessibility_stats.csv
- output/interactive_map.html
""")

# %%
# Export to multiple formats
all_access.to_file('output/accessibility_analysis.gpkg', driver='GPKG')
all_access.to_file('output/accessibility_analysis.geojson', driver='GeoJSON')

# Save statistics
stats = all_access.groupby('time_period')['travel_time'].describe()
stats.to_csv('output/accessibility_stats.csv')
stats.to_excel('output/accessibility_stats.xlsx')

# Save interactive HTML
web_map.save('output/interactive_map.html')

print("""
Analysis complete! Output files:
- output/accessibility_analysis.gpkg
- output/accessibility_analysis.geojson
- output/accessibility_stats.csv
- output/accessibility_stats.xlsx
- output/interactive_map.html
""")

# %%
print(parks.columns)

# %%
parks['area_sqm'] = parks.geometry.area

# %%
# Check current CRS
print("Current CRS:", parks.crs)

# Project to a local CRS (using EPSG:3857 - Web Mercator, or choose a local UTM zone)
parks_projected = parks.to_crs(epsg=3857)

# Now calculate area
parks['area_sqm'] = parks_projected.geometry.area
print("Areas calculated in square meters")

# %%
parks['climate_score'] = calculate_climate_benefits(parks)
print("Climate benefits calculated!")

# %%
def calculate_climate_benefits(parks):
    """Calculate climate benefits for each park."""
    print("Calculating climate benefits...")
    
    # Simple scoring system (customize weights as needed)
    climate_scores = []
    for _, park in parks.iterrows():
        score = 0
        
        # Larger parks get higher scores
        area_ha = park['area_sqm'] / 10000  # Convert to hectares
        score += min(area_ha * 0.1, 10)  # Max 10 points for size
        
        # Add points for water features (if data available)
        if 'water' in park and park['water']:
            score += 5
            
        # Add points for tree cover (if data available)
        if 'trees' in park and park['trees']:
            score += min(park['trees'] * 0.01, 5)  # 1 point per 100 trees, max 5
            
        climate_scores.append(score)
    
    return climate_scores

# Add climate scores to parks
parks['climate_score'] = calculate_climate_benefits(parks)
print("Climate benefits calculated!")

# %%
def optimize_performance(G, boundary, sample_size=100):
    """
    Optimize performance for large-scale network analysis.
    
    Parameters:
    -----------
    G : networkx.Graph
        Input graph to simplify (if not already simplified)
    boundary : geopandas.GeoDataFrame
        Boundary for sampling points
    sample_size : int, optional
        Number of points to sample (default: 100)
        
    Returns:
    --------
    tuple
        (simplified_graph, sample_points)
    """
    import numpy as np
    from shapely.geometry import Point
    import geopandas as gpd
    import osmnx as ox
    from tqdm import tqdm
    
    # Input validation
    if not isinstance(sample_size, int) or sample_size <= 0:
        raise ValueError("sample_size must be a positive integer")
    
    if not hasattr(boundary, 'geometry'):
        raise ValueError("boundary must be a GeoDataFrame with a geometry column")
    
    print("Optimizing performance...")
    
    # Check if graph is already simplified
    if not G.graph.get('simplified', False):
        print("Simplifying graph...")
        G_simplified = ox.simplify_graph(G)
    else:
        print("Graph is already simplified, using as is...")
        G_simplified = G
    
    # Rest of the function remains the same
    print(f"Sampling {sample_size} points within boundary...")
    points = []
    minx, miny, maxx, maxy = boundary.total_bounds
    boundary_geom = boundary.geometry.unary_union
    
    with tqdm(total=sample_size, desc="Sampling points") as pbar:
        while len(points) < sample_size:
            n_needed = sample_size - len(points)
            x = np.random.uniform(minx, maxx, n_needed * 2)
            y = np.random.uniform(miny, maxy, n_needed * 2)
            
            for xi, yi in zip(x, y):
                point = Point(xi, yi)
                if point.within(boundary_geom):
                    points.append(point)
                    pbar.update(1)
                    if len(points) >= sample_size:
                        break
    
    points_gdf = gpd.GeoSeries(points, crs=boundary.crs)
    
    print(f"Optimized analysis for {len(points_gdf)} sample points")
    return G_simplified, points_gdf

# Now you can safely call it even if the graph is already simplified
try:
    G_optimized, sample_points = optimize_performance(G, boundary, sample_size=100)
    print("Optimization complete!")
except Exception as e:
    print(f"Error during optimization: {str(e)}")

# %%
import folium
from folium.plugins import MarkerCluster

# Create a base map centered on the sample points
m = folium.Map(location=[sample_points.y.mean(), sample_points.x.mean()], 
               zoom_start=13, 
               tiles='cartodbpositron')

# Add boundary
folium.GeoJson(boundary.geometry[0]).add_to(m)

# Add sample points with clustering for better visualization
marker_cluster = MarkerCluster().add_to(m)
for idx, point in sample_points.items():
    folium.CircleMarker(
        location=[point.y, point.x],
        radius=3,
        color='blue',
        fill=True,
        fill_color='blue'
    ).add_to(marker_cluster)

# Add layer control
folium.LayerControl().add_to(m)

# Display the map
print("Displaying sample points on map...")
display(m)

# %%
m.save('output/sample_points_map.html')
print("Map saved to 'output/sample_points_map.html'")

# %%
import pandas as pd
import numpy as np

# Assuming you have these variables from previous steps:
# - sample_points: The points we generated earlier
# - G_optimized: The simplified graph
# - parks: The parks GeoDataFrame

def calculate_travel_times(points, G, parks, mode='walk', speed_kmh=5):
    """
    Calculate travel times from points to nearest park.
    
    Parameters:
    -----------
    points : GeoSeries
        Origin points
    G : networkx.Graph
        Street network
    parks : GeoDataFrame
        Parks data
    mode : str
        'walk' or 'bike'
    speed_kmh : float
        Travel speed in km/h
        
    Returns:
    --------
    numpy.ndarray
        Array of travel times in minutes
    """
    # This is a simplified example - you'll need to implement the actual routing
    # Here we'll just return random times for demonstration
    return np.random.uniform(5, 60, size=len(points))

# Calculate walking times (assuming 5 km/h walking speed)
print("Calculating walking times...")
walk_times = calculate_travel_times(sample_points, G_optimized, parks, mode='walk', speed_kmh=5)

# Calculate cycling times (assuming 15 km/h cycling speed)
print("Calculating cycling times...")
bike_times = calculate_travel_times(sample_points, G_optimized, parks, mode='bike', speed_kmh=15)

# Create comparison DataFrame
modes_comparison = pd.DataFrame({
    'walk_time': walk_times,
    'bike_time': bike_times,
    'time_saving': walk_times - bike_times  # Time saved by cycling
})

print("\nFirst few rows of travel time comparison:")
print(modes_comparison.head())

# Now we can plot the comparison
plot_comparison(modes_comparison)

# %%
import os
from datetime import datetime

def save_results(modes_comparison, day_access, peak_access, night_access, parks, output_dir='output'):
    """
    Save all analysis results to organized output files.
    
    Parameters:
    -----------
    modes_comparison : GeoDataFrame
        Transportation mode comparison results
    day_access : GeoDataFrame
        Daytime accessibility results
    peak_access : GeoDataFrame
        Peak hour accessibility results
    night_access : GeoDataFrame
        Nighttime accessibility results
    parks : GeoDataFrame
        Parks data with climate scores
    output_dir : str, optional
        Output directory (default: 'output')
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        print(f"\nSaving results to '{output_dir}/'...")
        
        # Save transportation comparison
        transport_path = os.path.join(output_dir, f'transport_comparison_{timestamp}.geojson')
        modes_comparison.to_file(transport_path, driver='GeoJSON')
        print(f"✓ Saved transport comparison to {transport_path}")
        
        # Save temporal accessibility data
        temporal_data = {
            'day': day_access,
            'peak': peak_access,
            'night': night_access
        }
        
        for time_period, data in temporal_data.items():
            path = os.path.join(output_dir, f'accessibility_{time_period}_{timestamp}.geojson')
            data.to_file(path, driver='GeoJSON')
            print(f"✓ Saved {time_period} accessibility to {path}")
        
        # Save parks data
        parks_path = os.path.join(output_dir, f'parks_with_climate_scores_{timestamp}.geojson')
        parks.to_file(parks_path, driver='GeoJSON')
        print(f"✓ Saved parks data to {parks_path}")
        
        # Create a summary file
        summary_path = os.path.join(output_dir, f'summary_{timestamp}.txt')
        with open(summary_path, 'w') as f:
            f.write("Green Space Accessibility Analysis - Results Summary\n")
            f.write("="*50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Datasets Saved:\n")
            f.write(f"- Transport comparison: {os.path.basename(transport_path)}\n")
            f.write(f"- Parks with climate scores: {os.path.basename(parks_path)}\n")
            f.write("\nAccessibility Data:\n")
            for time_period in temporal_data:
                f.write(f"- {time_period.capitalize()}: accessibility_{time_period}_{timestamp}.geojson\n")
        
        print(f"\n✓ Analysis complete! All results saved to '{output_dir}/'")
        print(f"✓ Summary file: {summary_path}")
        
    except Exception as e:
        print(f"Error saving results: {str(e)}")
        raise

# Example usage (commented out since we don't have all variables defined)
# try:
#     save_results(modes_comparison, day_access, peak_access, night_access, parks)
# except NameError as e:
#     print(f"Error: {str(e)}")
#     print("Please make sure all required variables are defined before calling save_results().")

# %%
pip install folium osmnx geopandas numpy

# %%
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import numpy as np
import networkx as nx
from shapely.geometry import Point, Polygon
import osmnx as ox
import os
from branca.colormap import linear

def create_isochrone_map(center_point, network_type='walk', trip_times=[5, 10, 15, 20], 
                        travel_speed=4.5, output_file='output/isochrone_map.html'):
    """
    Create an interactive isochrone map showing travel time areas.
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    # Create a folium map centered on the point
    m = folium.Map(location=center_point, zoom_start=14, tiles='cartodbpositron')
    
    # Add the center point
    folium.Marker(
        location=center_point,
        icon=folium.Icon(color='red', icon='info-sign'),
        popup="Center Point"
    ).add_to(m)
    
    try:
        # Get the street network
        print("Downloading street network...")
        G = ox.graph_from_point(center_point, 
                              dist=2000,  # 2km radius
                              network_type=network_type,
                              simplify=True)
        
        # Get the nearest node to our center point
        center_node = ox.distance.nearest_nodes(G, center_point[1], center_point[0])
        
        # Calculate the area within each isochrone
        isochrone_polys = []
        for time in sorted(trip_times, reverse=True):
            # Calculate distance in meters for the time
            distance = (travel_speed * 1000 / 60) * time  # meters per minute * minutes
            
            # Get subgraph of nodes within the distance
            subgraph = nx.ego_graph(G, center_node, radius=distance, distance='length')
            
            # Get the convex hull of the nodes
            node_points = [Point(data['x'], data['y']) for node, data in subgraph.nodes(data=True)]
            if len(node_points) > 2:  # Need at least 3 points to create a polygon
                # Using union_all() instead of unary_union
                polygon = gpd.GeoSeries(node_points).union_all().convex_hull
                isochrone_polys.append((time, polygon))
        
        # Create a colormap
        colormap = linear.Blues_09.scale(0, max(trip_times))
        
        # Add isochrone polygons to the map
        for time, polygon in isochrone_polys:
            # Create a GeoJSON from the polygon
            geojson = gpd.GeoSeries([polygon]).__geo_interface__
            
            # Get color from the colormap
            color = colormap(time)
            
            # Create the style function with the correct scope
            def style_function(feature, color=color):
                return {
                    'fillColor': color,
                    'color': color,
                    'weight': 2,
                    'fillOpacity': 0.3
                }
            
            # Add the GeoJson to the map
            folium.GeoJson(
                geojson,
                style_function=style_function,
                tooltip=f'< {time} minutes'
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save the map
        m.save(output_file)
        print(f"Isochrone map saved to {output_file}")
        return m
        
    except Exception as e:
        print(f"Error creating isochrone map: {str(e)}")
        raise

# Example usage:
if __name__ == "__main__":
    # Example coordinates (replace with your area of interest)
    center_lat, center_lon = 40.7128, -74.0060  # New York City coordinates
    
    # Create the map
    isochrone_map = create_isochrone_map(
        center_point=(center_lat, center_lon),
        network_type='walk',  # 'walk', 'bike', or 'drive'
        trip_times=[5, 10, 15, 20],  # in minutes
        travel_speed=4.5,  # km/h
        output_file='output/isochrone_map.html'
    )
    
    # Display the map (in Jupyter)
    if isochrone_map:
        display(isochrone_map)

# %%
pip install tenacity

# %%
def create_single_park_isochrone(park, network_type, trip_times, travel_speed, output_file):
    """Create an isochrone map for a single park with better error handling."""
    try:
        # Ensure park geometry is valid
        if not hasattr(park, 'geometry') or park.geometry is None:
            print("  Warning: Park has no valid geometry")
            return False
            
        # Get park center point safely
        try:
            center = [float(park.geometry.centroid.y), float(park.geometry.centroid.x)]
        except (AttributeError, ValueError) as e:
            print(f"  Warning: Could not get park center: {str(e)}")
            return False
            
        # Create a map centered on the park
        m = folium.Map(location=center, zoom_start=14, tiles='cartodbpositron')
        
        # Add the park to the map
        try:
            folium.GeoJson(
                park.geometry.__geo_interface__,
                style_function=lambda x: {
                    'fillColor': '#2ecc71',
                    'color': '#27ae60',
                    'weight': 2,
                    'fillOpacity': 0.6
                },
                tooltip=str(park.get('name', 'Park'))
            ).add_to(m)
        except Exception as e:
            print(f"  Warning: Could not add park to map: {str(e)}")
            return False
            
        try:
            # Get the street network with retry logic
            print(f"Downloading network data for park: {park.get('name', 'Unnamed')}...")
            G = get_network_graph(center, network_type)
            
            # Get the nearest node to the park center
            center_node = ox.distance.nearest_nodes(G, center[1], center[0])
            
            # Calculate isochrones
            isochrone_polys = []
            for time in sorted(trip_times, reverse=True):
                try:
                    distance = float(travel_speed) * 1000.0 / 60.0 * float(time)
                    subgraph = nx.ego_graph(G, center_node, radius=distance, distance='length')
                    node_points = [Point(float(data['x']), float(data['y'])) 
                                 for node, data in subgraph.nodes(data=True)]
                    
                    if len(node_points) > 2:
                        polygon = gpd.GeoSeries(node_points).union_all().convex_hull
                        isochrone_polys.append((float(time), polygon))
                except Exception as e:
                    print(f"  Warning: Could not create isochrone for {time} min: {str(e)}")
                    continue
            
            if not isochrone_polys:
                print("  Warning: No isochrones could be created for this park")
                return False
            
            # Create a colormap
            colormap = linear.Blues_09.scale(0, float(max(trip_times)))
            
            # Add isochrones to the map
            for time, polygon in isochrone_polys:
                try:
                    color = colormap(float(time))
                    folium.GeoJson(
                        polygon.__geo_interface__,
                        style_function=lambda x, c=color: {
                            'fillColor': c,
                            'color': c,
                            'weight': 2,
                            'fillOpacity': 0.3
                        },
                        tooltip=f'< {time} minutes'
                    ).add_to(m)
                except Exception as e:
                    print(f"  Warning: Could not add isochrone for {time} min: {str(e)}")
                    continue
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Save the map
            m.save(output_file)
            print(f"  ✓ Saved isochrone map to {output_file}")
            return True
            
        except Exception as e:
            print(f"  Error processing park: {str(e)}")
            # Save a basic map even if isochrones fail
            try:
                basic_output = output_file.replace('.html', '_basic.html')
                m.save(basic_output)
                print(f"  ✓ Saved basic map (without isochrones) to {basic_output}")
            except:
                print("  Could not save basic map")
            return False
            
    except Exception as e:
        print(f"  Fatal error creating map: {str(e)}")
        return False

# %%
parks_gdf = load_parks_data("/home/sriya/mapping/cdp-mapping-systems/Assignments/final project/output/accessibility_analysis.geojson")

# %%
# First, let's make sure we have all the required packages
try:
    import geopandas as gpd
    import folium
    from shapely.geometry import Point
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:
    print("Installing required packages...")
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "geopandas", "folium", "shapely", "tenacity"])
    import geopandas as gpd
    import folium
    from shapely.geometry import Point
    from tenacity import retry, stop_after_attempt, wait_exponential

# Function to load parks data (modify this according to your data source)
def load_parks_data(file_path):
    """Load parks data from a file (GeoJSON, Shapefile, etc.)"""
    try:
        if file_path.endswith('.geojson'):
            return gpd.read_file(file_path)
        elif file_path.endswith('.shp'):
            return gpd.read_file(file_path)
        else:
            raise ValueError("Unsupported file format. Please use GeoJSON or Shapefile.")
    except Exception as e:
        print(f"Error loading parks data: {str(e)}")
        return None

# Function to create a sample parks GeoDataFrame (use this if you don't have a file)
def create_sample_parks(center_lat=40.7128, center_lon=-74.0060, num_parks=5):
    """Create a sample GeoDataFrame with parks"""
    from shapely.geometry import Point
    import numpy as np
    
    parks = []
    for i in range(num_parks):
        # Create points in a grid around the center
        lat = center_lat + (np.random.rand() - 0.5) * 0.1
        lon = center_lon + (np.random.rand() - 0.5) * 0.1
        parks.append({
            'name': f'Park {i+1}',
            'geometry': Point(lon, lat).buffer(0.005)  # Create small circular parks
        })
    
    return gpd.GeoDataFrame(parks, crs="EPSG:4326")

# Main execution
if __name__ == "__main__":
    # Option 1: Load your parks data from a file
    # parks_gdf = load_parks_data("path_to_your_parks_file.geojson")
    
    # Option 2: Create sample parks (if you don't have a file)
    print("Creating sample parks data...")
    parks_gdf = create_sample_parks(num_parks=3)  # Create 3 sample parks
    
    if parks_gdf is not None and not parks_gdf.empty:
        # Now use the create_park_isochrones function
        # Make sure to define all the required functions first (create_park_isochrones, create_single_park_isochrone, etc.)
        
        # Here you would call:
        # create_park_isochrones(
        #     parks_gdf=parks_gdf,
        #     network_type='walk',
        #     trip_times=[5, 10, 15, 20],
        #     travel_speed=4.5,
        #     output_dir='output/park_isochrones'
        # )
        print("Parks data loaded successfully! Uncomment the function call above to generate isochrones.")
        print(f"Number of parks: {len(parks_gdf)}")
        print(parks_gdf.head())
    else:
        print("Failed to load or create parks data.")

# %%
parks_gdf = load_parks_data("/home/sriya/mapping/cdp-mapping-systems/Assignments/final project/output/accessibility_analysis.geojson")

# %%
import folium
import geopandas as gpd
from IPython.display import display

# Load the parks data
parks_gdf = gpd.read_file("output/accessibility_analysis.geojson")

# Create a map centered on the first park's location
first_point = parks_gdf.geometry.centroid.iloc[0]
m = folium.Map(location=[first_point.y, first_point.x], zoom_start=13)

# Add parks to the map
for idx, park in parks_gdf.iterrows():
    # Create a popup with park information
    popup_text = f"<b>Park {idx}</b>"
    if 'name' in parks_gdf.columns:
        popup_text = f"<b>{park['name']}</b>"
    
    # Add the park to the map
    folium.GeoJson(
        park.geometry.__geo_interface__,
        style_function=lambda x: {
            'fillColor': '#2ecc71',
            'color': '#27ae60',
            'weight': 2,
            'fillOpacity': 0.6
        },
        tooltip=popup_text
    ).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Display the map
display(m)

# Save the map
output_file = "output/parks_map.html"
m.save(output_file)
print(f"Map saved to {output_file}")

# %%
import folium
import geopandas as gpd
import osmnx as ox
import networkx as nx
from shapely.geometry import Point
from tqdm import tqdm
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import random
import time
from branca.colormap import linear

# Configure OSMnx
ox.config(use_cache=True, log_console=True)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_network_graph(center, network_type, radius=2000):
    """Get street network with retry logic."""
    try:
        return ox.graph_from_point(
            center,
            dist=radius,
            network_type=network_type,
            simplify=True
        )
    except Exception as e:
        print(f"Network request failed: {str(e)}")
        if "timeout" in str(e).lower():
            wait_time = random.uniform(5, 15)
            print(f"Waiting {wait_time:.1f} seconds before retry...")
            time.sleep(wait_time)
        raise

def create_park_isochrone_map(parks_gdf, network_type='walk', trip_times=[5, 10, 15, 20], 
                            travel_speed=4.5, output_file='output/parks_isochrone_map.html'):
    """
    Create an interactive map with isochrones for all parks.
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    # Create a base map centered on the first park
    first_point = parks_gdf.geometry.centroid.iloc[0]
    m = folium.Map(location=[first_point.y, first_point.x], zoom_start=13, tiles='cartodbpositron')
    
    # Create a feature group for isochrones
    isochrone_group = folium.FeatureGroup(name='Isochrones', show=False)
    
    # Process each park
    for idx, park in tqdm(parks_gdf.iterrows(), total=len(parks_gdf), desc="Processing parks"):
        try:
            # Get park center
            center = [park.geometry.centroid.y, park.geometry.centroid.x]
            
            # Get the street network
            G = get_network_graph(center, network_type)
            center_node = ox.distance.nearest_nodes(G, center[1], center[0])
            
            # Calculate isochrones
            for time in sorted(trip_times, reverse=True):
                distance = (travel_speed * 1000 / 60) * time
                subgraph = nx.ego_graph(G, center_node, radius=distance, distance='length')
                node_points = [Point(data['x'], data['y']) for _, data in subgraph.nodes(data=True)]
                
                if len(node_points) > 2:
                    polygon = gpd.GeoSeries(node_points).unary_union.convex_hull
                    
                    # Add to map
                    folium.GeoJson(
                        polygon.__geo_interface__

# %%
def create_park_isochrone_map(parks_gdf, network_type='walk', trip_times=[5, 10, 15, 20], 
                            travel_speed=4.5, output_file='output/parks_isochrone_map.html'):
    """
    Create an interactive map with isochrones for all parks.
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    # Create a base map centered on the first park
    first_point = parks_gdf.geometry.centroid.iloc[0]
    m = folium.Map(location=[first_point.y, first_point.x], zoom_start=13, tiles='cartodbpositron')
    
    # Create a colormap
    colormap = linear.Blues_09.scale(0, max(trip_times))
    
    # Add a colorbar
    colormap.caption = 'Travel Time (minutes)'
    colormap.add_to(m)
    
    # Create feature groups
    isochrone_group = folium.FeatureGroup(name='Isochrones', show=True)
    parks_group = folium.FeatureGroup(name='Parks', show=True)
    
    # Process each park
    for idx, park in tqdm(parks_gdf.iterrows(), total=len(parks_gdf), desc="Processing parks"):
        try:
            # Get park center
            center = [park.geometry.centroid.y, park.geometry.centroid.x]
            
            # Add park to the map
            folium.GeoJson(
                park.geometry.__geo_interface__,
                style_function=lambda x: {
                    'fillColor': '#2ecc71',
                    'color': '#27ae60',
                    'weight': 2,
                    'fillOpacity': 0.6
                },
                tooltip=park.get('name', f'Park {idx}')
            ).add_to(parks_group)
            
            # Get the street network
            G = get_network_graph(center, network_type)
            center_node = ox.distance.nearest_nodes(G, center[1], center[0])
            
            # Calculate isochrones
            for time in sorted(trip_times, reverse=True):
                distance = (travel_speed * 1000 / 60) * time
                subgraph = nx.ego_graph(G, center_node, radius=distance, distance='length')
                node_points = [Point(data['x'], data['y']) for _, data in subgraph.nodes(data=True)]
                
                if len(node_points) > 2:
                    polygon = gpd.GeoSeries(node_points).unary_union.convex_hull
                    
                    # Add to map
                    folium.GeoJson(
                        polygon.__geo_interface__,
                        style_function=lambda x, t=time, c=colormap: {
                            'fillColor': c(t),
                            'color': c(t),
                            'weight': 2,
                            'fillOpacity': 0.3
                        },
                        tooltip=f'< {time} minutes to park'
                    ).add_to(isochrone_group)
                    
        except Exception as e:
            print(f"Error processing park {idx}: {str(e)}")
            continue
    
    # Add all layers to the map
    parks_group.add_to(m)
    isochrone_group.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map
    m.save(output_file)
    print(f"\nMap with isochrones saved to: {output_file}")
    return m

# Load your parks data
parks_gdf = gpd.read_file("output/accessibility_analysis.geojson")

# Create and display the map
isochrone_map = create_park_isochrone_map(
    parks_gdf=parks_gdf,
    network_type='walk',
    trip_times=[5, 10, 15, 20],
    travel_speed=4.5,
    output_file='output/parks_isochrone_map.html'
)

# Display the map in the notebook
display(isochrone_map)

# %%
# Let's fix the D3.js code in the HTML template
fixed_js = """
// ... (previous JavaScript code remains the same until the drag functions)

// Drag functions
function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}

function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}

function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
}

// Update the drag behavior in the node creation
const node = g.append("g")
    .selectAll(".node")
    .data(graph.nodes)
    .enter().append("g")
    .attr("class", "node")
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));
"""

# Now let's update the HTML content with the fixed JavaScript
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Parks Network</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        /* ... (keep all the existing styles the same) ... */
    </style>
</head>
<body>
    <div class="controls">
        <button onclick="zoomIn()">+</button>
        <button onclick="zoomOut()">-</button>
        <button onclick="resetZoom()">Reset</button>
        <button onclick="toggleLabels()">Toggle Labels</button>
    </div>
    <div id="tooltip" class="tooltip" style="opacity: 0;"></div>
    
    <script>
        // Configuration
        const config = {{
            width: window.innerWidth,
            height: window.innerHeight,
            chargeStrength: -100,
            linkDistance: 100,
            gravity: 0.1
        }};
        
        // Set up the SVG
        const svg = d3.select("body").append("svg")
            .attr("width", config.width)
            .attr("height", config.height);
            
        // Add zoom/pan behavior
        const g = svg.append("g")
            .call(d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", (event) => {{
                    g.attr("transform", event.transform);
                }}))
            .append("g");
            
        // Tooltip
        const tooltip = d3.select("#tooltip");
        
        // Load the data
        const graph = {json.dumps(network_data)};
        
        // Create the force simulation
        const simulation = d3.forceSimulation(graph.nodes)
            .force("link", d3.forceLink(graph.links).id(d => d.id).distance(d => d.value * 10))
            .force("charge", d3.forceManyBody().strength(config.chargeStrength))
            .force("center", d3.forceCenter(config.width / 2, config.height / 2))
            .force("x", d3.forceX(config.width / 2).strength(config.gravity))
            .force("y", d3.forceY(config.height / 2).strength(config.gravity));
        
        // Create the links
        const link = g.append("g")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke-width", d => Math.sqrt(d.value));
        
        // Create the nodes
        const node = g.append("g")
            .selectAll(".node")
            .data(graph.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // Add circles to the nodes
        node.append("circle")
            .attr("r", d => Math.sqrt(d.size) * 2 || 5)
            .style("fill", d => d.color)
            .on("mouseover", showTooltip)
            .on("mousemove", moveTooltip)
            .on("mouseout", hideTooltip);
        
        // Add labels to the nodes
        const labels = node.append("text")
            .attr("dy", ".35em")
            .text(d => d.name)
            .attr("text-anchor", "middle")
            .attr("y", d => Math.sqrt(d.size) * 2 + 5 || 10);
        
        // Update positions on each tick
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        // Drag functions
        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
        
        // Tooltip functions
        function showTooltip(event, d) {{
            tooltip
                .style("opacity", 1)
                .html(`<strong>${{d.name}}</strong><br>ID: ${{d.id}}<br>Size: ${{d.size.toFixed(2)}}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}
        
        function moveTooltip(event) {{
            tooltip
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}
        
        function hideTooltip() {{
            tooltip.style("opacity", 0);
        }}
        
        // Zoom functions
        function zoomIn() {{
            svg.transition().duration(300).call(
                svg.transition().call,
                d3.zoom().scaleBy,
                1.5
            );
        }}
        
        function zoomOut() {{
            svg.transition().duration(300).call(
                svg.transition().call,
                d3.zoom().scaleBy,
                0.75
            );
        }}
        
        function resetZoom() {{
            svg.transition().duration(750).call(
                svg.transition().call,
                d3.zoom().transform,
                d3.zoomIdentity
            );
        }}
        
        // Toggle labels
        function toggleLabels() {{
            const labels = d3.selectAll("text");
            labels.style("display", labels.style("display") === "none" ? "block" : "none");
        }}
        
        // Handle window resize
        window.addEventListener('resize', () => {{
            const width = window.innerWidth;
            const height = window.innerHeight;
            
            svg.attr("width", width).attr("height", height);
            simulation.force("center", d3.forceCenter(width / 2, height / 2));
            simulation.force("x", d3.forceX(width / 2).strength(config.gravity));
            simulation.force("y", d3.forceY(height / 2).strength(config.gravity));
            simulation.alpha(0.3).restart();
        }});
    </script>
</body>
</html>
"""

# Save the fixed HTML file
output_file = "output/parks_network_fixed.html"
with open(output_file, "w") as f:
    f.write(html_content)

print(f"Fixed interactive network map saved to: {output_file}")

# %%
import geopandas as gpd
import json
import os

# 1. Load your parks data
parks_gdf = gpd.read_file("output/accessibility_analysis.geojson")

# Ensure the GeoDataFrame is in WGS84 (EPSG:4326) for web mapping
if parks_gdf.crs.to_epsg() != 4326:
    parks_gdf = parks_gdf.to_crs(epsg=4326)

# 2. Create a function to generate the map HTML
def create_geographic_map(parks_gdf, output_file):
    # Convert parks to GeoJSON
    parks_geojson = json.loads(parks_gdf.to_json())
    
    # Create the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Geographic Parks Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            body {{ margin: 0; padding: 0; }}
            #map {{ height: 100vh; width: 100%; }}
            .park-info {{ 
                padding: 10px; 
                background: white;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
            }}
            .park-info h3 {{ margin-top: 0; }}
            .legend {{ 
                padding: 10px; 
                background: white;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                line-height: 1.5;
            }}
            .legend i {{ 
                width: 18px;
                height: 18px;
                float: left;
                margin-right: 8px;
                opacity: 0.7;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        
        <script>
            // Initialize the map
            const map = L.map('map').setView([{parks_gdf.geometry.centroid.y.mean()}, {parks_gdf.geometry.centroid.x.mean()}], 13);
            
            // Add OpenStreetMap base layer
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);
            
            // Add parks to the map
            const parks = {json.dumps(parks_geojson)};
            
            // Create a feature group for the parks
            const parksLayer = L.geoJSON(parks, {{
                pointToLayer: function(feature, latlng) {{
                    // For point data
                    return L.circleMarker(latlng, {{
                        radius: 8,
                        fillColor: '#2ecc71',
                        color: '#27ae60',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }});
                }},
                onEachFeature: function(feature, layer) {{
                    // Add popup with park information
                    let popupContent = `<div class="park-info">`;
                    popupContent += `<h3>${{feature.properties.name || 'Unnamed Park'}}</h3>`;
                    
                    // Add all properties to the popup
                    for (const [key, value] of Object.entries(feature.properties)) {{
                        if (value && key !== 'name') {{
                            popupContent += `<b>${{key}}:</b> ${{value}}<br>`;
                        }}
                    }}
                    
                    popupContent += `</div>`;
                    layer.bindPopup(popupContent);
                    
                    // Add hover effect
                    layer.on('mouseover', function() {{
                        this.setStyle({{
                            weight: 3,
                            color: '#e74c3c',
                            fillOpacity: 1
                        }});
                        this.bringToFront();
                    }});
                    
                    layer.on('mouseout', function() {{
                        this.setStyle({{
                            weight: 1,
                            color: '#27ae60',
                            fillOpacity: 0.8
                        }});
                    }});
                }}
            }}).addTo(map);
            
            // Fit map to park bounds
            map.fitBounds(parksLayer.getBounds().pad(0.1));
            
            // Add scale control
            L.control.scale({{imperial: false}}).addTo(map);
            
            // Add layer control
            const baseMaps = {{
                "OpenStreetMap": L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'),
                "Satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}')
            }};
            
            // Add base maps
            baseMaps["OpenStreetMap"].addTo(map);
            
            // Add layer control
            L.control.layers(baseMaps, {{"Parks": parksLayer}}, {{collapsed: false}}).addTo(map);
            
            // Add legend
            const legend = L.control({{position: 'bottomright'}});
            legend.onAdd = function() {{
                const div = L.DomUtil.create('div', 'legend');
                div.innerHTML = `
                    <h4>Legend</h4>
                    <div><i style="background: #2ecc80"></i> Park</div>
                    <div><i style="background: #e74c3c; border-radius: 50%; width: 10px; height: 10px;"></i> Hovered Park</div>
                `;
                return div;
            }};
            legend.addTo(map);
            
            // Add search control
            const searchControl = new L.Control.Search({{
                layer: parksLayer,
                propertyName: 'name',
                marker: false,
                moveToLocation: function(latlng, title, map) {{
                    map.setView(latlng, 16);
                }}
            }});
            searchControl.on('search:locationfound', function(e) {{
                e.layer.openPopup();
            }});
            map.addControl(searchControl);
        </script>
    </body>
    </html>
    """
    
    # Save the HTML file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    return output_file

# 3. Generate the map
output_file = "output/parks_geographic_map.html"
map_path = create_geographic_map(parks_gdf, output_file)
print(f"Geographic map saved to: {map_path}")

# 4. Display the map in the notebook
from IPython.display import IFrame
display(IFrame(src=map_path, width='100%', height=600))

# %%
def create_geographic_map(parks_gdf, output_file):
    # Make a copy to avoid modifying the original
    parks = parks_gdf.copy()
    
    # Convert to a projected CRS (using Web Mercator for global coverage)
    projected_crs = 'EPSG:3857'  # Web Mercator
    if parks.crs != projected_crs:
        projected = parks.to_crs(projected_crs)
        # Calculate centroid in the projected CRS
        center = projected.geometry.centroid
        center_lon, center_lat = center.x.mean(), center.y.mean()
        # Convert center back to WGS84
        from pyproj import Transformer
        transformer = Transformer.from_crs(projected_crs, 'EPSG:4326', always_xy=True)
        center_lon, center_lat = transformer.transform(center_lon, center_lat)
    else:
        # If already in WGS84, use directly
        center = parks.geometry.centroid
        center_lon, center_lat = center.x.mean(), center.y.mean()
    
    # Ensure the GeoDataFrame is in WGS84 (EPSG:4326) for web mapping
    if parks.crs != 'EPSG:4326':
        parks = parks.to_crs('EPSG:4326')
    
    # Convert parks to GeoJSON
    parks_geojson = json.loads(parks.to_json())
    
    # Create the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Geographic Parks Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            body {{ margin: 0; padding: 0; }}
            #map {{ height: 100vh; width: 100%; }}
            .park-info {{ 
                padding: 10px; 
                background: white;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
            }}
            .park-info h3 {{ margin-top: 0; }}
            .legend {{ 
                padding: 10px; 
                background: white;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                line-height: 1.5;
            }}
            .legend i {{ 
                width: 18px;
                height: 18px;
                float: left;
                margin-right: 8px;
                opacity: 0.7;
            }}
            .search-control {{ 
                margin-top: 10px !important; 
                margin-right: 10px !important;
            }}
            .search-input {{ 
                width: 200px !important; 
                padding: 5px !important;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        
        <script>
            // Initialize the map
            const map = L.map('map').setView([{center_lat}, {center_lon}], 13);
            
            // Add OpenStreetMap base layer
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);
            
            // Add parks to the map
            const parks = {json.dumps(parks_geojson)};
            
            // Create a feature group for the parks
            const parksLayer = L.geoJSON(parks, {{
                pointToLayer: function(feature, latlng) {{
                    // For point data
                    return L.circleMarker(latlng, {{
                        radius: 8,
                        fillColor: '#2ecc71',
                        color: '#27ae60',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }});
                }},
                onEachFeature: function(feature, layer) {{
                    // Add popup with park information
                    let popupContent = `<div class="park-info">`;
                    popupContent += `<h3>${{feature.properties.name || 'Unnamed Park'}}</h3>`;
                    
                    // Add all properties to the popup
                    for (const [key, value] of Object.entries(feature.properties)) {{
                        if (value !== null && value !== undefined && key !== 'name') {{
                            popupContent += `<b>${{key.replace('_', ' ')}}:</b> ${{value}}<br>`;
                        }}
                    }}
                    
                    popupContent += `</div>`;
                    layer.bindPopup(popupContent);
                    
                    // Add hover effect
                    layer.on('mouseover', function() {{
                        this.setStyle({{
                            weight: 3,
                            color: '#e74c3c',
                            fillOpacity: 1
                        }});
                        this.bringToFront();
                    }});
                    
                    layer.on('mouseout', function() {{
                        this.setStyle({{
                            weight: 1,
                            color: '#27ae60',
                            fillOpacity: 0.8
                        }});
                    }});
                }}
            }}).addTo(map);
            
            // Fit map to park bounds with some padding
            if (parksLayer.getBounds().isValid()) {{
                map.fitBounds(parksLayer.getBounds().pad(0.1));
            }}
            
            // Add scale control
            L.control.scale({{imperial: false}}).addTo(map);
            
            // Add base maps
            const baseMaps = {{
                "OpenStreetMap": L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'),
                "Satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}')
            }};
            
            // Add layer control
            L.control.layers(baseMaps, {{"Parks": parksLayer}}, {{collapsed: false}}).addTo(map);
            
            // Add legend
            const legend = L.control({{position: 'bottomright'}});
            legend.onAdd = function() {{
                const div = L.DomUtil.create('div', 'legend');
                div.innerHTML = `
                    <h4>Legend</h4>
                    <div><i style="background: #2ecc71; border-radius: 50%; width: 12px; height: 12px; display: inline-block;"></i> Park</div>
                    <div><i style="background: #e74c3c; border-radius: 50%; width: 12px; height: 12px; display: inline-block;"></i> Hovered Park</div>
                `;
                return div;
            }};
            legend.addTo(map);
            
            // Add search control
            const searchControl = L.control({{position: 'topright'}});
            searchControl.onAdd = function() {{
                const div = L.DomUtil.create('div', 'search-control');
                div.innerHTML = '<input type="text" id="search" class="search-input" placeholder="Search parks...">';
                return div;
            }};
            searchControl.addTo(map);
            
            // Add search functionality
            document.getElementById('search').addEventListener('input', function() {{
                const searchTerm = this.value.toLowerCase();
                parksLayer.eachLayer(function(layer) {{
                    const name = layer.feature.properties.name || '';
                    if (name.toLowerCase().includes(searchTerm)) {{
                        layer.setStyle({fillColor: '#3498db', color: '#2980b9'});
                        if (searchTerm) {{
                            layer.openPopup();
                        }}
                    }} else {{
                        layer.setStyle({fillColor: '#2ecc71', color: '#27ae60'});
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    # Save the HTML file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    return output_file

# Generate the map with the corrected centroid calculation
output_file = "output/parks_geographic_map_fixed.html"
map_path = create_geographic_map(parks_gdf, output_file)
print(f"Geographic map saved to: {map_path}")

# Display the map in the notebook
from IPython.display import IFrame
display(IFrame(src=map_path, width='100%', height=600))


