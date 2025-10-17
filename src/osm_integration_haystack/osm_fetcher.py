from typing import List, Dict, Optional, Tuple, Union
from haystack import Document, component

from .overpass_client import OverpassClient
from .osm_doc_converter import DocConverter
from .utils.geo_utils import GeoRadiusFilter

@component
class OSMFetcher:
    
    def __init__(
        self,
        preset_center: Optional[Tuple[float, float]] = None,
        preset_radius_m: Optional[int] = None,
        target_osm_types: Optional[Union[str, List[str]]] = None,
        target_osm_tags: Optional[Union[str, List[str]]] = None,
        maximum_query_mb: Optional[int] = 5,
        max_token:int = 12000,
        overpass_timeout: Optional[int] = 25
    ):
        self.preset_center = preset_center
        self.preset_radius_m = preset_radius_m
        self.target_osm_types = self._normalize_osm_types(target_osm_types) if target_osm_types else ['node', 'way', 'relation']
        self.target_osm_tags = self._normalize_osm_tags(target_osm_tags) if target_osm_tags else None
        self.maximum_query_mb = maximum_query_mb
        self.max_token = max_token
        self.timeout = overpass_timeout


    @component.output_types(documents=List[Document])
    def run(self, center: Optional[Tuple[float, float]] = None, radius_m: Optional[int] = None,) -> Dict[str, List[Document]]:

        ctr = center or self.preset_center
        rad = radius_m or self.preset_radius_m
        if ctr is None or rad is None:
            raise ValueError("center/radius_m not provided: please set defaults in __init__ or pass them in run().")

        docs = self._fetch_by_radius(ctr, rad)
        return {"documents": docs}

    # 内部工具：fetchbyradius
    def _fetch_by_radius(self, center: Tuple[float, float], radius_m: int) -> List[Document]:
        # 1) OverpassClient 拉 JSON
        client = OverpassClient(
            center=center,
            radius_m=radius_m,
            target_types=self.target_osm_types,
            target_tags=self.target_osm_tags,
            maxsize_mb= self.maximum_query_mb,
            timeout=self.timeout
            )
        raw_data = client.fetch_osm_data()
        

        converter = DocConverter()
        converter.read_json(raw_data).clean_data()
        cleansed = converter.cleansed

        documents = []
        curr_token = 0
        for _, entry in cleansed.items():
            # 2) Converter 转 content/meta + 计算 distance_m（相对 center）
            dist = GeoRadiusFilter.haversine_distance(center, (entry["meta"]["lat"], entry["meta"]["lon"]))
            entry["meta"]["distance_m"] = dist
            # 3) 包成 List[Document] 返回
            doc = Document(
                content=entry["content"],
                meta=entry["meta"]
            )

            # doc_tokens = len(entry["content"]) // 4 + len(str(entry["meta"])) // 4
            documents.append(doc)

        documents.sort(key=lambda d: d.meta.get("distance_m", float("inf")))
        return documents

    def _normalize_osm_types(self, target_osm_types:Optional[Union[str, List[str]]]) -> List[str]:
        valid_osm_types = {'node', 'way', 'relation'}

        if target_osm_types is None:
            return list(valid_osm_types)
        
        if isinstance(target_osm_types, str):
            target_osm_types = [target_osm_types]
        else:
            for type_str in target_osm_types:
                if type_str not in valid_osm_types:
                    raise ValueError(f"[OSM Fetcher] Invalid OSM type: {type_str}. Must be one of {valid_osm_types}")
        
        return target_osm_types
    
    def _normalize_osm_tags(self, target_osm_tags: Optional[Union[str, List[str]]]) -> List[str]:
        if target_osm_tags is None:
            return []
        elif isinstance(target_osm_tags, str):
            return [target_osm_tags]
        else:
            return target_osm_tags
        