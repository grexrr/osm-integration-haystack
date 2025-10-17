import unittest
from osm_integration_haystack import OSMFetcher

class TestOSMFetcher(unittest.TestCase):
    
    def setUp(self):
        self.center = (51.898403, -8.473978)
        self.radius = 200
        self.maximum_query_size = 100  
        self.overpass_timeout = 25      

    def test_normalize_osm_types(self):
        fetcher = OSMFetcher(
            preset_center=self.center,     
            preset_radius_m=self.radius,    
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
        
    def test_fetch_by_radius(self):
        return 
    
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