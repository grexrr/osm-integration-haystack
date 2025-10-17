# OSM Integration Haystack

Haystack component to fetch geographic data via the freely available OpenStreetMap (OSM) Overpass API.

-----

**Table of Contents**

- [Installation](#Installation)
- [Overview](#Overview)
- [Basic Usage](#Basic_Usage)
- [Configuration Parameters](#Configuration_Parameters)
- [Examples](#Examples)
- [API Rate Limitations](#API_Rate_Limitations)
- [License](#License)

## Installation

```console
pip install osm-integration-haystack
```

## Overview

This repository implements a Haystack component that integrates with OpenStreetMap data through the Overpass API. It allows you to fetch geographic information and convert it into Haystack Documents for use in RAG (Retrieval-Augmented Generation) pipelines.

When you give `OSMFetcher` a location and radius, it returns a list of nearby points of interest (POIs) as Haystack Documents. It uses the Overpass API to query OpenStreetMap data and converts the results into structured documents with geographic metadata.

## Basic Usage

Here's a simple example of how to use the `OSMFetcher` component:

```python
from osm_integration_haystack import OSMFetcher

# Create an instance of OSMFetcher
osm_fetcher = OSMFetcher(
    preset_center=(51.898403, -8.473978),  # Cork, Ireland
    preset_radius_m=500,  # 500m radius
    target_osm_types=["node"],  # Search nodes
    target_osm_tags=["amenity"],  # Search amenity types
    maximum_query_mb=2,  # Limit query size
    overpass_timeout=20
)

# Fetch nearby locations
results = osm_fetcher.run()

# Access the documents
documents = results["documents"]

print("Found locations:")
for doc in documents[:5]:  # Show first 5
    print(f"Name: {doc.meta.get('name', 'Unknown')}")
    print(f"Type: {doc.meta.get('category', 'Unknown')}")
    print(f"Distance: {doc.meta.get('distance_m', 0):.1f}m")
    print(f"Content: {doc.content}")
    print("\n")
```

### Haystack Pipeline Integration

You can also integrate `OSMFetcher` into a complete Haystack pipeline:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret
from osm_integration_haystack import OSMFetcher

# Create pipeline components
osm_fetcher = OSMFetcher(
    preset_center=(51.898403, -8.473978),
    preset_radius_m=200,
    target_osm_types=["node"],
    target_osm_tags=["amenity"],
    maximum_query_mb=2,
    overpass_timeout=20
)

prompt_builder = PromptBuilder(template="""
You are a geographic information assistant. Based on the provided OpenStreetMap data, help me find the nearest coffee shops.

User location: {{ user_location }}
Search radius: {{ radius }}m

Available location data:
{% for document in documents[:10] %}
- {{ document.content }}
  Location: ({{ document.meta.lat }}, {{ document.meta.lon }})
  Distance: {{ document.meta.distance_m }}m
  Type: {{ document.meta.category }}
{% endfor %}

Please help me find coffee shop related locations and recommend the nearest 3.
""")

llm_generator = OpenAIGenerator(
    api_key=Secret.from_env_var("OPENAI_API_KEY"),
    model="gpt-4-turbo"
)

# Create and connect pipeline
pipeline = Pipeline()
pipeline.add_component("osm_fetcher", osm_fetcher)
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("llm_generator", llm_generator)

pipeline.connect("osm_fetcher.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "llm_generator.prompt")

# Run the pipeline
result = pipeline.run({
    "osm_fetcher": {},
    "prompt_builder": {
        "user_location": "Cork, Ireland (51.898403, -8.473978)",
        "radius": 200
    }
})

print(result["llm_generator"]["replies"][0])
```

## Configuration Parameters

The `OSMFetcher` component accepts several parameters to customize its behavior:

- `preset_center (Tuple[float, float], optional)`: Default center coordinates (latitude, longitude).
- `preset_radius_m (int, optional)`: Default search radius in meters.
- `target_osm_types (Union[str, List[str]], optional)`: OSM element types to search ("node", "way", "relation"). Default: ["node", "way", "relation"].
- `target_osm_tags (Union[str, List[str]], optional)`: OSM tags to filter by (e.g., ["amenity", "shop"]). Default: None (all tags).
- `maximum_query_mb (int, optional)`: Maximum query size in MB to prevent API timeouts. Default: 5.
- `overpass_timeout (int, optional)`: Timeout for Overpass API requests in seconds. Default: 25.

### Document Structure

Each returned document contains:

- `content`: Human-readable description of the location
- `meta`: Geographic and OSM metadata including:
  - `lat`, `lon`: Coordinates
  - `distance_m`: Distance from search center
  - `osm_id`: OSM element ID
  - `osm_type`: OSM element type
  - `name`: Location name
  - `category`: Primary category
  - `address`: Address information (if available)
  - `tags`: Additional OSM tags

## Examples

### Coffee Shop Finder

Find nearby coffee shops and restaurants. You can run the example directly:

```bash
# Clone the repository
git clone https://github.com/grexrr/osm-integration-haystack.git
cd osm-integration-haystack

# Install dependencies
pip install -r requirements.txt

# Run the example
python examples/agent_osm_demo.py
```

The script will prompt you to choose between:
1. **Full version** (requires OpenAI API key) - Uses Haystack pipeline with LLM
2. **Simplified version** (no API key needed) - Direct results display

```python
# Search for coffee shops
coffee_fetcher = OSMFetcher(
    preset_center=(51.898403, -8.473978),
    preset_radius_m=500,
    target_osm_types=["node"],
    target_osm_tags=["amenity"],
    maximum_query_mb=2
)

results = coffee_fetcher.run()
documents = results["documents"]

# Filter for coffee-related locations
coffee_keywords = ["cafe", "coffee", "restaurant", "bar", "pub", "food"]
coffee_related = []

for doc in documents:
    content_lower = doc.content.lower()
    category_lower = doc.meta.get("category", "").lower()
    
    if any(keyword in content_lower or keyword in category_lower 
           for keyword in coffee_keywords):
        coffee_related.append(doc)

# Display results
for i, doc in enumerate(coffee_related[:5]):
    print(f"{i+1}. {doc.meta.get('name', 'Unknown')}")
    print(f"   Type: {doc.meta.get('category', 'Unknown')}")
    print(f"   Distance: {doc.meta.get('distance_m', 0):.1f}m")
```

## API Rate Limitations

The Overpass API has rate limitations to prevent abuse. If you encounter rate limiting:

- Reduce query frequency
- Use smaller search radii
- Limit `maximum_query_mb` parameter
- Implement retry logic with exponential backoff

For production use, consider using a commercial OSM data provider or hosting your own Overpass instance.

## License

`osm-integration-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.