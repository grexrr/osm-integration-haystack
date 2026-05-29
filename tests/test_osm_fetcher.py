import unittest
from haystack import Document
from osm_integration_haystack import OSMFetcher

class TestOSMFetcher(unittest.TestCase):
    
    def setUp(self):
        self.center = (51.898403, -8.473978)
        self.radius = 200
        self.maximum_query_mb = 100  
        self.overpass_timeout = 25      

    def test_normalize_osm_types(self):
        fetcher = OSMFetcher(
            preset_center=self.center,     
            preset_radius_m=self.radius,    
            maximum_query_mb=100,  # 直接使用数值
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
 
        center = (51.898403, -8.473978)  # Cork, Ireland
        radius = 200  
        
        fetcher = OSMFetcher(
            preset_center=center,
            preset_radius_m=radius,
            target_osm_types=["node"],  
            target_osm_tags=["shop", "amenity"],  
            maximum_query_mb=1,  
            overpass_timeout=15
        )
        
        print("=" * 60)
        print("开始测试OSMFetcher核心功能")
        print(f"中心点: {center}")
        print(f"半径: {radius}米")
        print(f"目标类型: {fetcher.target_osm_types}")
        print(f"目标标签: {fetcher.target_osm_tags}")
        print("=" * 60)
        
        try:
            # 执行获取
            result = fetcher.run()
            documents = result["documents"]
            
            print(f"\n✅ 成功获取到 {len(documents)} 个Document")
            
            if documents:
                print("\n" + "=" * 60)
                print("Document结构分析:")
                print("=" * 60)
                
                # 分析第一个Document
                first_doc = documents[0]
                print(f"\n📄 第一个Document (距离: {first_doc.meta.get('distance_m', 'N/A'):.1f}米):")
                print(f"Content: {first_doc.content}")
                print(f"Meta keys: {list(first_doc.meta.keys())}")
                
                # 详细打印meta信息
                print("\n📋 Meta详细信息:")
                for key, value in first_doc.meta.items():
                    if isinstance(value, dict):
                        print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
                
                # 验证Haystack Document要求
                print("\n" + "=" * 60)
                print("Haystack Document兼容性检查:")
                print("=" * 60)
                
                # 检查必要属性
                checks = [
                    ("content存在", hasattr(first_doc, 'content') and first_doc.content is not None),
                    ("meta存在", hasattr(first_doc, 'meta') and first_doc.meta is not None),
                    ("content是字符串", isinstance(first_doc.content, str)),
                    ("meta是字典", isinstance(first_doc.meta, dict)),
                    ("content不为空", len(first_doc.content.strip()) > 0),
                    ("包含地理位置", 'lat' in first_doc.meta and 'lon' in first_doc.meta),
                    ("包含距离信息", 'distance_m' in first_doc.meta),
                    ("包含OSM ID", 'osm_id' in first_doc.meta),
                    ("包含OSM类型", 'osm_type' in first_doc.meta),
                ]
                
                all_passed = True
                for check_name, passed in checks:
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check_name}: {passed}")
                    if not passed:
                        all_passed = False
                
                print(f"\n🎯 总体兼容性: {'✅ 通过' if all_passed else '❌ 失败'}")
                
                # 显示前3个Document的摘要
                print("\n" + "=" * 60)
                print("前3个Document摘要:")
                print("=" * 60)
                
                for i, doc in enumerate(documents[:3]):
                    distance = doc.meta.get('distance_m', 0)
                    name = doc.meta.get('name', 'Unknown')
                    category = doc.meta.get('category', 'Unknown')
                    osm_type = doc.meta.get('osm_type', 'Unknown')
                    
                    print(f"\n{i+1}. {name} ({category})")
                    print(f"   距离: {distance:.1f}米 | 类型: {osm_type}")
                    print(f"   内容: {doc.content[:100]}{'...' if len(doc.content) > 100 else ''}")
                
                # 距离排序验证
                distances = [doc.meta.get('distance_m', float('inf')) for doc in documents]
                is_sorted = all(distances[i] <= distances[i+1] for i in range(len(distances)-1))
                print(f"\n📊 距离排序检查: {'✅ 正确排序' if is_sorted else '❌ 排序错误'}")
                
            else:
                print("⚠️  没有获取到任何Document")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
    
class TestOSMFetcherTokenBudget(unittest.TestCase):

    def setUp(self):
        self.fetcher = OSMFetcher(
            preset_center=(51.9, -8.4),
            preset_radius_m=200,
            max_token=100000,
        )

    def _doc(self, content, distance_m, verbose_meta=False):
        meta = {"lat": 51.9, "lon": -8.4, "distance_m": distance_m}
        if verbose_meta:
            meta["tags"] = {"amenity": "cafe"}
            meta["tags_norm"] = {"amenity": "cafe"}
        return Document(content=content, meta=meta)

    def _tokens(self, doc):
        return len(doc.content) // 4 + len(str(doc.meta)) // 4

    def test_no_trim_when_within_budget(self):
        docs = [self._doc("cafe", 10.0), self._doc("pub", 20.0)]
        result = self.fetcher._apply_token_budget(docs)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].content, "cafe")
        self.assertEqual(result[1].content, "pub")

    def test_phase1_removes_verbose_meta_when_over_budget(self):
        doc = self._doc("X" * 100, 10.0, verbose_meta=True)
        self.fetcher.max_token = self._tokens(doc) - 1
        result = self.fetcher._apply_token_budget([doc])
        self.assertNotIn("tags", result[0].meta)
        self.assertNotIn("tags_norm", result[0].meta)

    def test_phase1_truncates_long_content_when_over_budget(self):
        doc = self._doc("X" * 400, 10.0)
        self.fetcher.max_token = self._tokens(doc) - 1
        result = self.fetcher._apply_token_budget([doc])
        self.assertLessEqual(len(result[0].content), 300)

    def test_phase2_drops_farthest_when_still_over_budget_after_compression(self):
        docs = [
            self._doc("X" * 400, 10.0),
            self._doc("X" * 400, 20.0),
            self._doc("X" * 400, 30.0),
        ]
        self.fetcher.max_token = 100  # fits only 1 doc after compression
        result = self.fetcher._apply_token_budget(docs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].meta["distance_m"], 10.0)


    def test_slim_output_keeps_only_essential_fields(self):
        doc = Document(
            content="cafe",
            meta={
                "lat": 51.9, "lon": -8.4, "distance_m": 10.0,
                "name": "Test Cafe", "category": "cafe",
                "address": {"street": "Main St", "city": "Cork"},
                "tags": {"amenity": "cafe"}, "tags_norm": {"amenity": "cafe"},
                "osm_id": 123, "osm_type": "node", "source": "openstreetmap",
            }
        )
        fetcher = OSMFetcher(
            preset_center=(51.9, -8.4), preset_radius_m=200, slim_output=True
        )
        result = fetcher._slim_documents([doc])
        self.assertEqual(
            set(result[0].meta.keys()),
            {"lat", "lon", "distance_m", "name", "category", "address"},
        )

    def test_slim_output_truncates_long_content(self):
        doc = Document(
            content="X" * 500,
            meta={"lat": 51.9, "lon": -8.4, "distance_m": 10.0},
        )
        fetcher = OSMFetcher(
            preset_center=(51.9, -8.4), preset_radius_m=200, slim_output=True
        )
        result = fetcher._slim_documents([doc])
        self.assertLessEqual(len(result[0].content), 300)

    def test_budget_does_not_strip_meta_when_within_limit(self):
        doc = Document(
            content="cafe",
            meta={
                "lat": 51.9, "lon": -8.4, "distance_m": 10.0,
                "name": "Test Cafe", "tags": {"amenity": "cafe"}, "osm_id": 123,
            },
        )
        fetcher = OSMFetcher(
            preset_center=(51.9, -8.4), preset_radius_m=200,
            slim_output=False, max_token=100000,
        )
        result = fetcher._apply_token_budget([doc])
        self.assertIn("tags", result[0].meta)
        self.assertIn("osm_id", result[0].meta)

    def test_slim_output_with_over_budget_drops_farthest(self):
        fetcher = OSMFetcher(
            preset_center=(51.9, -8.4),
            preset_radius_m=200,
            slim_output=True,
            max_token=150,
        )
        docs = [
            Document(
                content="X" * 400,
                meta={"lat": 51.9, "lon": -8.4, "distance_m": 10.0,
                      "name": "A", "tags": {"amenity": "cafe"}},
            ),
            Document(
                content="X" * 400,
                meta={"lat": 51.9, "lon": -8.4, "distance_m": 20.0,
                      "name": "B", "tags": {"amenity": "pub"}},
            ),
        ]
        # slim first: meta reduced to slim fields, content truncated to 300
        slimmed = fetcher._slim_documents(docs)
        # then budget: max_token=150 means only 1 doc fits
        result = fetcher._apply_token_budget(slimmed)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].meta["distance_m"], 10.0)
        self.assertNotIn("tags", result[0].meta)


if __name__ == "__main__":
    unittest.main()
