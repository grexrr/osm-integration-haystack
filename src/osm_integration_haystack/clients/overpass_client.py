from typing import List, Tuple
import time
import json
import requests

class OverpassClient:

    _OSM_ENDPOINT = "https://overpass-api.de/api/interpreter"
    _OSM_TYPES = ['node', 'way', 'relation']
    
    def __init__(self, timeout: int = 25, maxsize: int = 1000000) -> None:
        self.timeout = timeout
        self.maxsize = maxsize
        self.headers = {
            'User-Agent': 'OSM-Integration-Haystack/1.0 (your-email@example.com)'
        }

  
    
    def fetch_osm_data(self, lat_user: float, lon_user: float, radius: float, tags:List[str]=None, osm_types: str = "node") -> dict:
        
        query = self._build_geojson_query(lat_user, lon_user, radius, tags, osm_types)
        res = requests.post(self._OSM_ENDPOINT, data=query)

        print(f"Status: {res.status_code}")
        print(f"Response: {res.text[:200]}...")

        return res.json()
    

    def _build_geojson_query(self, lat_user:float, lon_user:float, radius:float, tags:List[str]=None, osm_types:str="node") -> str:
        
        # s, w, n, e = bbox[0], bbox[1], bbox[2], bbox[3]
        # bbox_query = f"({s},{w},{n},{e})"
        # target_types = [osm_types] if osm_types else self._OSM_TYPES
        queries = []
        for osm_type in osm_types:
            if tags:
                for tag in tags:
                    queries.append(f"{osm_type}[{tag}](around:{radius},{lat_user},{lon_user});")
            else:
                queries.append(f"{osm_type}(around:{radius},{lat_user},{lon_user});")
        

        query_body = "\n".join(queries)  #combine query body

        res = f"""
        [out:json]
        [timeout:{self.timeout}];
        (
            {query_body}
        );
        out geom;
        """

        print("Current Query:")
        print(res)
        
        return res

    def save_file(
            self, 
            data,
            path:str ="examples/test_output_json/test_output.json",
            mode = "w"
            ):
        with open(path, mode) as f:
            json.dump(data, f, indent=2)
        return

if __name__ == "__main__":
    client = OverpassClient()
    lat_user, lon_user, radius = 51.898403, -8.473978, 200

    # tags = [
    # "shop",
    # "service",
    # "tourism",
    # "amenity",
    # "emergency",
    # "building",
    # "healthcare"
    # ]
    tags = None
    
    types = ["node"]

    data = client.fetch_osm_data(lat_user, lon_user, radius, tags, types)
    data = client.fetch_osm_data(lat_user, lon_user, radius, tags, types)
    client.save_file(data)