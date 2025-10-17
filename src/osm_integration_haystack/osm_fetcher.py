from http import client
from locale import normalize
from typing import List, Dict, Optional, Tuple, Union
from haystack import Document, component

from osm_integration_haystack.overpass_client import OverpassClient

@component
class OSMFetcher:
    
    def __init__(
        self,
        preset_center: Optional[Tuple[float, float]] = None,
        preset_radius_m: Optional[int] = None,
        target_osm_types: Optional[Union[str, List[str]]] = None,
        target_osm_tags: Optional[Union[str, List[str]]] = None,
        maximum_query_size: Optional[int] = 1000000,
        overpass_timeout: Optional[int] = 25
    ):
        self.preset_center = preset_center
        self.preset_radius_m = preset_radius_m
        self.target_osm_types = self._normalize_osm_types(target_osm_types) if target_osm_types else ['node', 'way', 'relation']
        self.target_osm_tags = self._normalize_osm_tags(target_osm_tags) if target_osm_tags else None
        self.maximum_query_size = maximum_query_size
        self.timeout = overpass_timeout


    @component.output_types(documents=List[Document])
    def run(
        self,
        center: Optional[Tuple[float, float]] = None,
        radius_m: Optional[int] = None,
    ) -> Dict[str, List[Document]]:

        ctr = center or self.preset_center
        rad = radius_m or self.preset_radius_m
        if ctr is None or rad is None:
            raise ValueError("center/radius_m 未提供：请在 __init__ 设默认，或在 run() 传入。")

        docs = self._fetch_by_radius(ctr, rad)
        return {"documents": docs}

    # 内部工具：你说的 fetchbyradius
    def _fetch_by_radius(self, center: Tuple[float, float], radius_m: int) -> List[Document]:
        # 1) OverpassClient 拉 JSON
        # lat_user, lon_user = center[0], center[1]
        # client = OverpassClient(self.timeout, self.maximum_query_size)

        # 2) Converter 转 content/meta + 计算 distance_m（相对 center）
        # 3) 包成 List[Document] 返回
        ...

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
        