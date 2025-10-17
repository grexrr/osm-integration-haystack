import unittest
from osm_integration_haystack.osm_fetcher import OSMFetcher

class Test_OSM_Fetcher(unittest.TestCase):
    
    def setUp(self):
        self.center = (51.898403, -8.473978)
        self.radius = 200
        self.maximum_query_size = 100  # 修复：赋值
        self.overpass_timeout = 25      # 修复：赋值

    def test_normalize_osm_types(self):
        fetcher = OSMFetcher(
            preset_center=self.center,      # 修复：使用正确的参数名
            preset_radius_m=self.radius,    # 修复：使用正确的参数名
            maximum_query_size=self.maximum_query_size,
            overpass_timeout=self.overpass_timeout
        )
        
        result = fetcher._normalize_osm_types("node")
        self.assertEqual(result, ["node"])
        
        result = fetcher._normalize_osm_types(["node", "way"])
        self.assertEqual(result, ["node", "way"])
        
        result = fetcher._normalize_osm_types(None)
        self.assertEqual(set(result), {"node", "way", "relation"})
        self.assertEqual(len(result), 3)
        

if __name__ == "__main__":
    unittest.main()


    # center, radius = (51.898403, -8.473978), 200
    # types = "node"
    # tags = [
    #     "shop",
    #     "service",
    #     "tourism",
    #     "amenity",
    #     "emergency",
    #     "building",
    #     "healthcare"
    #     ]
    
    # fetcher = OSMFetcher(center, radius, types, tags)
    # print(fetcher.target_osm_tags)
    # print(fetcher.target_osm_types)