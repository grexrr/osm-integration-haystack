from typing import List, Tuple
import json
import requests


class OverpassClient:

    _OSM_ENDPOINT = "https://overpass-api.de/api/interpreter"
    _OSM_TYPES = ['node', 'way', 'relation']
    
    def __init__(self, 
                 center:Tuple[float, float], 
                 radius_m:float, 
                 target_types: List[str] = None,
                 target_tags: List[str] = None,
                 maxsize_mb: int = 5,
                 timeout: int = 25,
                 url: str = "https://github.com/grexrr/osm-integration-haystack"
                 ) -> None:
        self.lat_user = center[0]
        self.lon_user = center[1]
        self.radius_m = radius_m
        self.types = target_types
        self.tags = target_tags
        self.maxsize = maxsize_mb * 1000000
        self.timeout = timeout
        self.headers = {
            'User-Agent': f'OSM-Integration-Haystack/1.0 ({url})'
        } 

    def fetch_osm_data(self) -> dict:
        
        query = self._build_geojson_query(self.lat_user, self.lon_user, self.radius_m, self.tags, self.types)
        res = requests.post(self._OSM_ENDPOINT, data=query, headers=self.headers)

        print(f"Status: {res.status_code}")
        print(f"Response: {res.text[:200]}...")

        return res.json()

    def fetch_osm_data_raw(self) -> str:
        """just for test"""
        query = self._build_geojson_query(self.lat_user, self.lon_user, self.radius_m, self.tags, self.types)
        res = requests.post(self._OSM_ENDPOINT, data=query, headers=self.headers)
        
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text[:200]}...")
        if res.status_code != 200:
            raise Exception(f"Overpass API error {res.status_code}: {res.text}")
        
        return res.text

    def _build_geojson_query(self, lat_user:float=None, lon_user:float=None, radius:float=None, tags:List[str]=None, types:List[str]=None) -> str:
        
        lat_user = lat_user if lat_user else self.lat_user
        lon_user = lon_user if lon_user else self.lon_user
        radius = radius if radius else self.radius_m
        tags = tags if tags else self.tags
        types = types if types else self._OSM_TYPES

        queries = []
        for osm_type in types:
            if tags:
                for tag in tags:
                    queries.append(f"{osm_type}[{tag}](around:{radius},{lat_user},{lon_user});")
            else:
                queries.append(f"{osm_type}(around:{radius},{lat_user},{lon_user});")
        

        query_body = "\n".join(queries)  #combine query body

        res = f"""
        [out:json][timeout:{self.timeout}][maxsize:{self.maxsize}];
        (
            {query_body}
        );
        out geom;
        """

        print("Current Query:")
        print(res)
        
        return res

    def set_types(self, types:List[str]):
        self.types = types
        return self

    def set_tags(self, tags:List[str]):
        self.tags = tags
        return self

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

    tags = [
    "shop",
    "service",
    "tourism",
    "amenity",
    "emergency",
    "building",
    "healthcare"
    ]
    tags = None
    
    types = "node"

    data = client.fetch_osm_data(lat_user, lon_user, radius, tags, types)
    data = client.fetch_osm_data(lat_user, lon_user, radius, tags, types)
    client.save_file(data)