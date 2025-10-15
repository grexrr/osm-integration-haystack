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
from collections import Counter
from typing import Dict
import json


class OSM_Doc_Converter:
    def __init__(self) -> None:
        self.raw = None
        self.raw_length = 0
        self.tag_freq = Counter()        
        self.cleansed = None

    def read_json(self, data:Dict) -> None:
        try:
            print("[OSM_Doc_Converter] Reading Raw OSM GeoJson...")
            
            if elements := data['elements']:
                self.raw = elements
                self.raw_length = len(elements)
                print(f"[OSM_Doc_Converter] Loaded {self.raw_length} entries.")
            else:
                raise Exception("[OSM_Doc_Converter] No 'elements' found in the data.")

            self.tag_freq.update(f"{k}" for element in elements for k, _ in element.get("tags", {}).items())

        except Exception as e:
            raise Exception(f"[OSM_Doc_Converter] Error loading data: {e}")
        return self
    

    def clean_data(self) -> None:
        print("[OSM_Doc_Converter] Processing data cleaning.")
        
       
        for element in self.raw:
            name_field = None
            addr_field = None

            if "name" not in element["tags"] and "amenity" not in element["tags"]:
                continue 
            
            # process name_field
            if "name" in element["tags"]:
                name_str = element["tags"].pop("name")
                if "amenity" in element["tags"]:
                    amenity_str = element["tags"].pop("amenity")
                    name_field = f"Name: {name_str} ({amenity_str}), "
                else:
                    name_field = f"Name: {name_str}, "
                print(f"{name_field}")
            elif "amenity" in element["tags"]:
                amenity_str = element["tags"].pop("amenity")
                name_field = f"Name: {amenity_str}, "
                print(f"{name_field}")

            # process addr_field
            addr_items = []
            for key in list(element["tags"].keys()):
                if key.startswith("addr:"):
                    addr_items.append(element["tags"].pop(key))

            if addr_items:
                addr_field = "Address: " + ", ".join(addr_items) + ", "
                print(addr_field)

            print(element["tags"])
            print()



        return self

    def get_raw(self) -> Dict:
        return self.raw
    
    def get_cleansed(self) -> Dict:
        return self.cleansed

    def get_tag_freq(self) -> None:
        print("[OSM_Doc_Converter] Most common tags:")
        print(self.tag_freq.most_common(20))
        return self.tag_freq

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
    res = converter.read_json(data).clean_data()
    
    # result = converter.get_cleansed()
    # print(result['elements'][0])