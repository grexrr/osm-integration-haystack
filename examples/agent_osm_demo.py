import os
from pathlib import Path
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret
from osm_integration_haystack import OSMFetcher

# Load environment variables
def load_environment():
    """Load environment variables from .env file in root directory"""
    # Get project root directory
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent
    env_file = root_dir / ".env"
    
    if env_file.exists():
        # Manually parse .env file
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment file: {env_file}")
    else:
        print(f"⚠️  .env file not found: {env_file}")
        print("💡 Please create .env file and add: OPENAI_API_KEY=your-api-key-here")
    
    return os.getenv("OPENAI_API_KEY")

def create_coffee_finder_pipeline():
    """Create a Haystack pipeline to find nearby coffee shops"""
    
    # Load environment variables
    api_key = load_environment()
    
    if not api_key or api_key == "your-openai-api-key-here":
        raise ValueError("❌ Please set a valid OPENAI_API_KEY in .env file")
    
    # 1. Create OSMFetcher component
    osm_fetcher = OSMFetcher(
        preset_center=(51.898403, -8.473978),  # Cork, Ireland
        preset_radius_m=200,  # 200m radius
        target_osm_types=["node"],  # Only search nodes
        target_osm_tags=["amenity"],  # Search amenity types
        maximum_query_mb=2,  # Limit query size
        overpass_timeout=20
    )
    
    # 2. Create prompt builder
    prompt_template = """
    You are a geographic information assistant. Based on the provided OpenStreetMap data, help me find the nearest coffee shops.
    
    User location: {{ user_location }}
    Search radius: {{ radius }}m
    
    Available location data:
    {% for document in documents %}
    - {{ document.content }}
      Location: ({{ document.meta.lat }}, {{ document.meta.lon }})
      Distance: {{ document.meta.distance_m }}m
      Type: {{ document.meta.category }}
    {% endfor %}
    
    Please help me:
    1. Find all coffee shop related locations
    2. Sort by distance
    3. Recommend the nearest 3 coffee shops
    4. Provide detailed information for each coffee shop
    
    Please respond in English.
    """
    
    prompt_builder = PromptBuilder(template=prompt_template)
    
    # 3. Create LLM generator (using OpenAI)
    llm_generator = OpenAIGenerator(
        api_key=Secret.from_env_var("OPENAI_API_KEY"),  # Read directly from environment
        model="gpt-4-turbo"
    )
    
    # 4. Create pipeline
    pipeline = Pipeline()
    
    # Add components
    pipeline.add_component("osm_fetcher", osm_fetcher)
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm_generator", llm_generator)
    
    # Connect components
    pipeline.connect("osm_fetcher.documents", "prompt_builder.documents")
    pipeline.connect("prompt_builder.prompt", "llm_generator.prompt")
    
    return pipeline

def run_coffee_finder_demo():
    """Run coffee shop finder demo"""
    
    print("=" * 60)
    print("☕ Coffee Shop Finder Demo - Haystack Pipeline")
    print("=" * 60)
    
    # Create pipeline
    pipeline = create_coffee_finder_pipeline()
    
    # Prepare input data
    user_location = "Cork, Ireland (51.898403, -8.473978)"
    radius = 500
    
    print(f"📍 User location: {user_location}")
    print(f"🔍 Search radius: {radius}m")
    print("\nSearching for nearby coffee shops...")
    
    try:
        # Run pipeline
        result = pipeline.run({
            "osm_fetcher": {},  # Use preset center and radius
            "prompt_builder": {
                "user_location": user_location,
                "radius": radius
            }
        })
        
        print("\n" + "=" * 60)
        print("🤖 AI Assistant Response:")
        print("=" * 60)
        print(result["llm_generator"]["replies"][0])
        
    except Exception as e:
        print(f"❌ Runtime error: {str(e)}")
        print("\n💡 Please ensure:")
        print("1. OpenAI API key is installed")
        print("2. Network connection is normal")
        print("3. Overpass API is accessible")

def simple_coffee_finder():
    """Simplified version - no LLM, direct results display"""
    
    print("=" * 60)
    print("☕ Simplified Coffee Shop Finder")
    print("=" * 60)
    
    # Create OSMFetcher
    fetcher = OSMFetcher(
        preset_center=(51.898403, -8.473978),
        preset_radius_m=500,
        target_osm_types=["node"],
        target_osm_tags=["amenity"],
        maximum_query_mb=2,
        overpass_timeout=20
    )
    
    print("📍 Search location: Cork, Ireland")
    print("🔍 Search radius: 500m")
    print("🏷️  Target tags: amenity (facilities)")
    print("\nFetching data...")
    
    try:
        # Get data
        result = fetcher.run()
        documents = result["documents"]
        
        print(f"\n✅ Found {len(documents)} locations")
        
        # Filter coffee shop related locations
        coffee_related = []
        coffee_keywords = ["cafe", "coffee", "restaurant", "bar", "pub", "food"]
        
        for doc in documents:
            content_lower = doc.content.lower()
            category_lower = doc.meta.get("category", "").lower()
            
            if any(keyword in content_lower or keyword in category_lower 
                   for keyword in coffee_keywords):
                coffee_related.append(doc)
        
        print(f"\n☕ Found {len(coffee_related)} coffee shop/restaurant related locations:")
        print("-" * 60)
        
        for i, doc in enumerate(coffee_related[:5]):  # Show first 5
            distance = doc.meta.get("distance_m", 0)
            name = doc.meta.get("name", "Unknown name")
            category = doc.meta.get("category", "Unknown type")
            
            print(f"\n{i+1}. {name}")
            print(f"   Type: {category}")
            print(f"   Distance: {distance:.1f}m")
            print(f"   Details: {doc.content}")
            
            # Show address information
            if "address" in doc.meta:
                addr = doc.meta["address"]
                addr_parts = []
                for key in ["street", "housenumber", "city", "postcode"]:
                    if key in addr:
                        addr_parts.append(addr[key])
                if addr_parts:
                    print(f"   Address: {', '.join(addr_parts)}")
        
        if not coffee_related:
            print("\n😔 No coffee shop related locations found in the specified range")
            print("💡 Suggestions:")
            print("- Expand search radius")
            print("- Check network connection")
            print("- Try other locations")
            
    except Exception as e:
        print(f"❌ Data fetch failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Select run mode:")
    print("1. Full version (requires OpenAI API key)")
    print("2. Simplified version (direct results)")
    
    choice = input("Please enter choice (1 or 2): ").strip()
    
    if choice == "1":
        run_coffee_finder_demo()
    elif choice == "2":
        simple_coffee_finder()
    else:
        print("Invalid choice, running simplified version...")
        simple_coffee_finder()