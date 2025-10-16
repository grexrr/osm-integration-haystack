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

from ast import List, Tuple
from collections import Counter
from typing import Any, Dict
import json
from unicodedata import category

from certifi import contents
from numpy import add


class OSM_Doc_Converter:

    WHITELIST_TAGS_PRIORITY = [
        # "aerialway", "aeroway", 
        "emergency",
        "amenity",
        "shop",
        "tourism",
        "building", 
        "craft",
        
        # "barrier", "boundary",
    ]

    CORE_TAGS = {
        
    }

    def __init__(self) -> None:
        self.raw = None
        self.raw_length = 0
        self.tag_freq = Counter()        
        self.cleansed = {}
    
    # ================ Load Data ================ 
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
    
    # ================ Process ================ 
    def clean_data(self) -> None:

        print("[OSM_Doc_Converter] Batch-processing data cleaning.")
        for element in self.raw:
            self._clean_element(element)

        return self

    def _clean_element(self, element) -> None:
        
        if "type" not in element or "id" not in element or ("lat" or "lon") not in element:
            return
        
        result = {
            "meta": {
                "tags_norm": {},
                "tags": {}
            }
        }

        # ================ Processing ================ 

        result["meta"]["source"] = "openstreetmap"
        result["meta"]["osm_id"] = element["id"]
        result["meta"]["osm_type"] = element["type"]
        result["meta"]["lat"] = element["lat"]
        result["meta"]["lon"] = element["lon"]
        
        # Processing Name Field
        processed_tags = set()

        name_field = None
        for category in self.WHITELIST_TAGS_PRIORITY:
            if category in element["tags"]:
                if "name" in element["tags"]:
                    name_str = element["tags"]["name"]
                    processed_tags.add("name")
                else:
                    name_str = element["tags"][category]
                    processed_tags.add(category)
                result["meta"]["name"] = name_str
                
                if category == "emergency":
                    category_str = category
                else:
                    category_str = element["tags"][category]

                result["meta"]["category"] = category_str
                if name_str == category_str:
                    name_field = f"{category_str.capitalize()}"
                else:
                    name_field = f"{category_str.capitalize()}: {name_str}"
                break
        
        # if not processed_tags:
        #     print(element["id"])
        # else:
        #     print(processed_tags)

        # Processing Address Field
        address_field = ""
        hours_field = ""
        for tag in element["tags"]:

            if tag not in self.get_top_n_tags(25):
                continue

            if tag.startswith("addr:"):
                
                # "addr:housenumber": "74"
                # tag: "addr:housenumber"
                # addr_val: 74
                # addr_type: housenumber
                addr_val = element["tags"][tag]
                addr_type = tag.split(":")[1]
                
                address_field += f"{addr_val} "
                
                if "address" not in result["meta"]:
                    result["meta"]["address"] = {}
                result["meta"]["address"][addr_type] = addr_val
                processed_tags.add(tag)
            
            elif tag == "opening_hours":
                hours = element["tags"]["opening_hours"]
                hours_field = f"{hours}"
                
            else:
                # Processing the rest
                if tag not in processed_tags:
                    result["meta"]["tags"][tag] = element["tags"][tag]
                    if ":" in tag:
                        k = tag.split(":")
                        norm_key = f"{k[0]}_{k[1]}"
                    else:
                        norm_key = tag
                    result["meta"]["tags_norm"][norm_key] = element["tags"][tag]
                    processed_tags.add(tag)
        
        parts = [name_field, address_field, hours_field]
        parts = [part for part in parts if part.strip()]  
        content_str = ", ".join(parts)
        result["content"] = content_str

        # ================ Processing Meta ================ 
        # print(result)
        self.cleansed[element["id"]] = result


    # ================ Read Stats ================ 

    def _norm_key(self, k: str) -> str:
        import re
        k = k.replace(":", "_")
        k = re.sub(r"[^0-9A-Za-z_]+", "_", k)
        k = re.sub(r"_+", "_", k).strip("_")
        return k

    def norm_val(v):
        return v.strip() if isinstance(v, str) else v

    def get_raw(self) -> Dict:
        return self.raw
    
    def get_cleansed(self) -> Dict:
        return self.cleansed

    def get_tag_freq(self, num:int=None) -> None:
        print("[OSM_Doc_Converter] Most common tags:")
        if not num:
            print(self.tag_freq.most_common())
        else:
            print(self.tag_freq.most_common(num))
        return self.tag_freq

    def get_top_n_tags(self, n):
        return set(tag for tag, _ in self.tag_freq.most_common(n))

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
    res = converter.read_json(data).get_tag_freq(20)


    # 过程json
    converter.read_json(data).clean_data()
    res = converter.cleansed
    with open("temp_output.json", "w") as f:
        json.dump(res, f, indent=2)
    # result = converter.get_cleansed()
    # print(result['elements'][0])