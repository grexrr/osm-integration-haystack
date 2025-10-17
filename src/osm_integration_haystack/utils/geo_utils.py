import math
from typing import List, Tuple, Dict
from haystack import Document, component

@component
class GeoRadiusFilter:
    def __init__(self, max_radius_m: int = 5000):
        self.max_radius_m = max_radius_m

    @component.output_types(documents=List[Document])
    def run(
        self,
        documents: List[Document],
        center: Tuple[float, float],
        radius_m: int,
    ) -> Dict[str, List[Document]]:
        # 1) 参数校验
        lat, lon = center
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("center 超出经纬度范围")
        if radius_m <= 0:
            raise ValueError("radius_m 必须为正数")
        if radius_m > self.max_radius_m:
            radius_m = self.max_radius_m  # 或者直接报错

        # 2) 计算距离并写回 meta
        for d in documents:
            lat2 = d.meta.get("lat")
            lon2 = d.meta.get("lon")
            if lat2 is None or lon2 is None:
                d.meta["distance_m"] = float("inf")
                continue
            d.meta["distance_m"] = GeoRadiusFilter.haversine_distance(center, (lat2, lon2))

        # 3) 过滤 + 排序
        kept = [d for d in documents if d.meta.get("distance_m", float("inf")) <= radius_m]
        kept.sort(key=lambda x: x.meta.get("distance_m", float("inf")))

        return {"documents": kept}
    
    @staticmethod
    def haversine_distance(center1: Tuple[float, float], center2: Tuple[float, float]) -> float:
        R = 6371000.0 
        lat1, lon1 = center1[0], center1[1]
        lat2, lon2 = center2[0], center2[1]
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad)*math.cos(lat2_rad)*math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c  