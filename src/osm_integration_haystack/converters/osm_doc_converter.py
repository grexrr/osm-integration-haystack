# {
#   "source": "openstreetmap",
#   "osm_id": 5203945953,
#   "osm_type": "node",
#   "name": "Bunsen",
#   "category": "restaurant",
#   "lat": 51.8990915,
#   "lon": -8.4736065,
#   "bbox": null,
#   "tags": {
#     "amenity": "restaurant",
#     "addr:city": "Cork",
#     "addr:street": "French Church Street",
#     "cuisine": "beer",
#     "opening_hours": "Mo-We 12:00-21:30; Th,Sa 12:00-22:30; Su 13:00-21:30",
#     "phone": "+353 21 239 0660",
#     "website": "https://www.bunsen.ie/",
#     "wheelchair": "yes"
#   },
#   "overpass_query": "...",
#   "retrieved_at": "2025-10-14T..Z"
# }

from ast import Tuple
from typing import Dict
import json


class OSM_Doc_Converter:
    def __init__(self) -> None:
        self.raw = None
        self.cleansed = None

    def read_json(self, data:Dict) -> None:
        try:
            print("Reading Raw OSM GeoJson...")
            self.raw = data
            n = len(data.get('elements', []))
            print(f"[OSM_Doc_Converter] Loaded {n} entries.")
            if n == 0:
                print("[OSM_Doc_Converter] No entries found!")
        except Exception as e:
            raise Exception(f"Error loading data: {e}")
        return self
    
    def _observed_data(self, write=True) -> None:
        print("[OSM_Doc_Converter] Processing data cleaning.")
        
        # name_field
        entries_without_name = {}
        count = 0
        for element in self.raw["elements"]:
            if name := element["tags"].get("name"):
                print(name)
            else:
                count += 1
                entries_without_name[count] = element
        print(f"{count} entries without name!")

        if write:
            with open("/Users/grexrr/Documents/osm-integration-haystack/examples/test_output_json/temp_entries_without_name.json", "w") as f:
                json.dump(entries_without_name, f, indent=2)

        return self

    def clean_data(self) -> None:
        print("[OSM_Doc_Converter] Processing data cleaning.")
        

        self.cleansed = self.raw
        return self

    def set_user_location(self, lat: float, lon: float) ->  'OSM_Doc_Converter':
            """设置用户查询位置"""
            self.user_location = (lat, lon)
            return self

    def get_raw(self) -> Dict:
        return self.raw
    
    def get_cleansed(self) -> Dict:
        return self.cleansed

if __name__ == "__main__":

    # load testing data
    import json
    import os

    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "examples", "test_output_json", "test_output.json")
    with open(file_path, "r") as f:
        data = json.load(f)

    #read tags
    # tags = set()
    # elements = data["elements"]
    # for element in elements:
    #     tags.update(element["tags"])
    # print(tags)

    # start cleaning
    converter = OSM_Doc_Converter()
    converter.read_json(data)._observed_data()
    
    # result = converter.get_cleansed()
    # print(result['elements'][0])