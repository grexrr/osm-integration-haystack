import unittest
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
    
if __name__ == "__main__":
    unittest.main()
