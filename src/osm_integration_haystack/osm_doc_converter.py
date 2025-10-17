from collections import Counter
from typing import Dict

class DocConverter:

    WHITELIST_TAGS_PRIORITY = [
        "emergency",
        "healthcare",
        "amenity",
        "shop",
        "tourism",
        "building", 
        "craft",
        "geological",
        "highway",
        "cycleway",
        "aerialway",
        "aeroway",
        "barrier",
        "boundary"
    ]

    def __init__(self) -> None:
        self.raw = None
        self.raw_length = 0
        self.tag_freq = Counter()   
        self.top_set = set()     
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
            self.top_set = set(self.get_top_n_tags(50))

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
        
        res = {
            "meta": {
            }
        }

        res["meta"]["source"] = "openstreetmap"
        res["meta"]["osm_id"] = element["id"]
        res["meta"]["osm_type"] = element["type"]
        res["meta"]["lat"] = element["lat"]
        res["meta"]["lon"] = element["lon"]
        
        
        processed_tags = set() 

        # Processing Name Field
        name_field = None
        for category in self.WHITELIST_TAGS_PRIORITY:
            if category in element["tags"]:
                if "name" in element["tags"]:
                    name_str = element["tags"]["name"]
                    processed_tags.add("name")
                else:
                    name_str = element["tags"][category]
                    processed_tags.add(category)
                res["meta"]["name"] = name_str
                
                if category == "emergency":
                    category_str = category
                else:
                    category_str = element["tags"][category]

                res["meta"]["category"] = category_str
                if name_str == category_str:
                    name_field = f"{category_str.capitalize()}"
                else:
                    name_field = f"{category_str.capitalize()}: {name_str}"
                break

        address_field = ""
        hours_field = ""
        
        addr_map = {}
        for tag in element["tags"]:

            if tag not in self.top_set:
                continue
            
            val = element["tags"][tag]
            if val in (None, "", []):
                continue

            if "tags" not in res["meta"]:
                res["meta"]["tags"] = {}
            if "tags_norm" not in res["meta"]:
                res["meta"]["tags_norm"] = {}

            if tag.startswith("addr:"):
                
                # Processing Addr: Field
                addr_type = tag.split(":", 1)[1]
                addr_map[addr_type] = val
                
                
                if "address" not in res["meta"]:
                    res["meta"]["address"] = {}
                res["meta"]["address"][addr_type] = val
                processed_tags.add(tag)
            
            elif tag == "opening_hours":
                # Processing opening_hour field
                hours_field = f"{val}"
                res["meta"]["tags"][tag] = val
                res["meta"]["tags_norm"][self._norm_key(tag)] = self._norm_val(val)
                processed_tags.add(tag)
                
            else:
                # Processing the rest
                if tag in processed_tags:
                    continue

                res["meta"]["tags"][tag] = val
                res["meta"]["tags_norm"][self._norm_key(tag)] = self._norm_val(val)
                processed_tags.add(tag)

        addr_obj = res["meta"].get("address", {})
        if addr_obj:
            addr_order = ["street", "housenumber", "city", "postcode"]
            addr_parts = [addr_obj[k] for k in addr_order if k in addr_obj]
            address_field = ", ".join(addr_parts)

        parts = [p for p in [name_field, address_field] if p]
        content = ", ".join(parts) if parts else ""

        tags_bits = []
        if hours_field:
            tags_bits.append(f"opening_hours={hours_field}")
        if tags_bits:
            res["content"] = (content + ". " if content else "") + "Tags: " + ", ".join(tags_bits)
        else:
            res["content"] = content + ("." if content else "")

        self.cleansed[element["id"]] = res


    # ================ tools ======s========== 

    def _norm_key(self, k: str) -> str:
        import re
        k = k.replace(":", "_")
        k = re.sub(r"[^0-9A-Za-z_]+", "_", k)
        k = re.sub(r"_+", "_", k).strip("_")
        return k

    def _norm_val(self, v):
        if isinstance(v, str):
            v = v.strip()
            if v.lower() == "yes":
                return True
            elif v.lower() == "no":
                return False
            return v
        return v

    def get_raw(self) -> Dict:
        return self.raw
    
    def get_cleansed(self) -> Dict:
        return self.cleansed

    def get_tag_freq(self, num:int=None) -> None:
        if not num:
            print(self.tag_freq.most_common())
        else:
            print(self.tag_freq.most_common(num))
        return self.tag_freq

    def get_top_n_tags(self, n):
        return set(tag for tag, _ in self.tag_freq.most_common(n))