import unittest
from osm_integration_haystack import OverpassClient

class TestOverpassClient(unittest.TestCase):
    def setUp(self):
        self.center = (51.898403, -8.473978)
        self.radius = 1000.5
        self.maxsize_mb = 5
        self.overpass_timeout = 25   
    
    def test_query_build(self):
        
        print("[Testing][OverpassClient] Testing Query Build")
        
        client = OverpassClient(
            center=self.center,
            radius_m=self.radius,
            maxsize_mb=5,
            timeout=self.overpass_timeout,
            )
    
        print("=== test1: default behavior ===")
        query = client._build_geojson_query()
        expected_query = f"""
        [out:json][timeout:25][maxsize:5000000];
        (
            node(around:1000.5,51.898403,-8.473978);
way(around:1000.5,51.898403,-8.473978);
relation(around:1000.5,51.898403,-8.473978);
        );
        out geom;
        """
        self.assertTrue(query == expected_query)

        print("=== test2: specify types ===")
        types = ["node", "relation"]
        query = client._build_geojson_query(types=types)
        expected_query = f"""
        [out:json][timeout:25][maxsize:5000000];
        (
            node(around:1000.5,51.898403,-8.473978);
relation(around:1000.5,51.898403,-8.473978);
        );
        out geom;
        """
        self.assertTrue(query == expected_query)

        print("=== test3: specify only tags ===")
        tags = [
            "shop",
            "service",
            "tourism",
            "amenity",
            "emergency",
            "building",
            "healthcare"
            ]
        
        query = client._build_geojson_query(tags=tags)
        expected_query = f"""
        [out:json][timeout:25][maxsize:5000000];
        (
            node[shop](around:1000.5,51.898403,-8.473978);
node[service](around:1000.5,51.898403,-8.473978);
node[tourism](around:1000.5,51.898403,-8.473978);
node[amenity](around:1000.5,51.898403,-8.473978);
node[emergency](around:1000.5,51.898403,-8.473978);
node[building](around:1000.5,51.898403,-8.473978);
node[healthcare](around:1000.5,51.898403,-8.473978);
way[shop](around:1000.5,51.898403,-8.473978);
way[service](around:1000.5,51.898403,-8.473978);
way[tourism](around:1000.5,51.898403,-8.473978);
way[amenity](around:1000.5,51.898403,-8.473978);
way[emergency](around:1000.5,51.898403,-8.473978);
way[building](around:1000.5,51.898403,-8.473978);
way[healthcare](around:1000.5,51.898403,-8.473978);
relation[shop](around:1000.5,51.898403,-8.473978);
relation[service](around:1000.5,51.898403,-8.473978);
relation[tourism](around:1000.5,51.898403,-8.473978);
relation[amenity](around:1000.5,51.898403,-8.473978);
relation[emergency](around:1000.5,51.898403,-8.473978);
relation[building](around:1000.5,51.898403,-8.473978);
relation[healthcare](around:1000.5,51.898403,-8.473978);
        );
        out geom;
        """
        self.assertTrue(query == expected_query)

    def test_fetch_osm_data(self):
        client = OverpassClient(
            center=self.center,
            radius_m=self.radius,
            maxsize_mb=5,
            timeout=self.overpass_timeout
        )
        
        print("[Testing][OverpassClient] Testing Response")
        
        print("=== test1: default behavior ===")
        response1 = client.fetch_osm_data_raw()
        print(f"响应长度: {len(response1)} 字符")
        print(f"前200字符: {response1[:200]}")
        
        print("=== test2: specify types ===")
        client.set_types(["node", "relation"])
        response2 = client.fetch_osm_data_raw()
        print(f"响应长度: {len(response2)} 字符")
        
        print("=== test3: specify only tags ===")
        tags = ["shop", "amenity"]
        client.set_tags(tags)
        response3 = client.fetch_osm_data_raw()
        print(f"响应长度: {len(response3)} 字符")
        
        if "error" in response3.lower():
            print("❌ Query contains an error")
        else:
            print("✅ Query succeeded")
        return response1, response2, response3

if __name__ == "__main__":
    unittest.main()