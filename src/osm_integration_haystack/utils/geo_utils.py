import math


class Geo_Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        使用 Haversine 公式计算两点间的距离（单位：公里）
        
        Args:
            lat1, lon1: 第一个点的纬度和经度
            lat2, lon2: 第二个点的纬度和经度
        
        Returns:
            float: 两点间的距离（公里）
        """

        R = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine 公式
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c