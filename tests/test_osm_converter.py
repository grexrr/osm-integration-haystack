import unittest
import json
import os
from osm_integration_haystack import DocConverter


class TestOSMDocConverter(unittest.TestCase):
    
    def setUp(self):
        self.converter = DocConverter()
        
        test_file_path = os.path.join(os.path.dirname(__file__), "test_osm_output.json")
        with open(test_file_path, "r") as f:
            self.test_data = json.load(f)
    
    def test_read_json(self):
        print("[Test][OSM Converter] JSON Data Reading")
        print(f"[Test][OSM Converter] Input: test_data has {len(self.test_data.get('elements', []))} elements")
        
        result = self.converter.read_json(self.test_data)
        
        print(f"[Test][OSM Converter] Output: raw_length = {result.raw_length}")
        print(f"[Test][OSM Converter] Output: tag_freq count = {len(result.tag_freq)}")
        print(f"[Test][OSM Converter] Output: top_set size = {len(result.top_set)}")
        
        self.assertIsNotNone(result.raw)
        self.assertIsInstance(result.raw, list)
        self.assertGreater(result.raw_length, 0)
        
        first_element = result.raw[0]
        print(f"[Test][OSM Converter] First element: ID={first_element['id']}, Type={first_element['type']}, Tags={len(first_element.get('tags', {}))}")
        self.assertIn("type", first_element)
        self.assertIn("id", first_element)
        self.assertIn("lat", first_element)
        self.assertIn("lon", first_element)
        self.assertIn("tags", first_element)
        
        self.assertIsNotNone(result.tag_freq)
        self.assertGreater(len(result.tag_freq), 0)
        
        self.assertIsNotNone(result.top_set)
        self.assertIsInstance(result.top_set, set)
    
    def test_clean_data(self):
        print("[Test][OSM Converter] Data Cleaning")
        self.converter.read_json(self.test_data)
        print(f"[Test][OSM Converter] Input: raw data has {len(self.converter.raw)} elements")
        
        result = self.converter.clean_data()
        
        print(f"[Test][OSM Converter] Output: cleansed data has {len(result.cleansed)} elements")
        self.assertIsNotNone(result.cleansed)
        self.assertIsInstance(result.cleansed, dict)
        self.assertGreater(len(result.cleansed), 0)
        
        # 检查第一个清理后的元素
        first_id = list(result.cleansed.keys())[0]
        first_cleansed = result.cleansed[first_id]
        print(f"[Test][OSM Converter] Checking first cleaned element ID: {first_id}")
        
        # 检查meta字段
        self.assertIn("meta", first_cleansed)
        meta = first_cleansed["meta"]
        print(f"[Test][OSM Converter] Meta fields: {list(meta.keys())}")
        
        # 检查必需的meta字段
        required_meta_fields = ["source", "osm_id", "osm_type", "lat", "lon"]
        print(f"[Test][OSM Converter] Checking required fields: {required_meta_fields}")
        for field in required_meta_fields:
            self.assertIn(field, meta)
        
        # 检查source字段
        print(f"[Test][OSM Converter] Source field: {meta['source']}")
        self.assertEqual(meta["source"], "openstreetmap")
        
        # 检查content字段
        print(f"[Test][OSM Converter] Content: '{first_cleansed['content']}'")
        self.assertIn("content", first_cleansed)
        self.assertIsInstance(first_cleansed["content"], str)
    
    def test_whitelist_tags_priority(self):
        print("[Test][OSM Converter] Whitelist Tags Priority")
        self.converter.read_json(self.test_data)
        self.converter.clean_data()
        
        whitelist_count = 0
        print(f"[Test][OSM Converter] Input: checking {len(self.converter.cleansed)} elements for whitelist tags")
        print(f"[Test][OSM Converter] Whitelist tags: {self.converter.WHITELIST_TAGS_PRIORITY}")
        
        for element_id, cleansed_element in self.converter.cleansed.items():
            meta = cleansed_element["meta"]
            
            original_element = next(e for e in self.converter.raw if e["id"] == element_id)
            tags = original_element.get("tags", {})
            
            has_whitelist_tag = any(tag in tags for tag in self.converter.WHITELIST_TAGS_PRIORITY)
            if has_whitelist_tag:
                whitelist_count += 1
                found_tags = [tag for tag in self.converter.WHITELIST_TAGS_PRIORITY if tag in tags]
                print(f"[Test][OSM Converter] Element {element_id} has whitelist tags: {found_tags}, category: {meta.get('category', 'None')}")
                self.assertIn("category", meta)
                self.assertIsNotNone(meta["category"])
        
        print(f"[Test][OSM Converter] Output: found {whitelist_count} elements with whitelist tags")
    
    def test_address_processing(self):
        print("[Test][OSM Converter] Address Processing")
        self.converter.read_json(self.test_data)
        self.converter.clean_data()
        
        address_count = 0
        print(f"[Test][OSM Converter] Input: checking {len(self.converter.cleansed)} elements for address tags")
        
        for element_id, cleansed_element in self.converter.cleansed.items():
            original_element = next(e for e in self.converter.raw if e["id"] == element_id)
            tags = original_element.get("tags", {})
            
            addr_tags = {k: v for k, v in tags.items() if k.startswith("addr:")}
            if addr_tags:
                meta = cleansed_element["meta"]
                print(f"[Test][OSM Converter] Element {element_id} has address tags: {list(addr_tags.keys())}")
                
                processed_addr_tags = {k: v for k, v in addr_tags.items() if k in self.converter.top_set}
                print(f"[Test][OSM Converter] Processed address tags (in top_set): {list(processed_addr_tags.keys())}")
                
                if processed_addr_tags:
                    address_count += 1
                    self.assertIn("address", meta)
                    self.assertIsInstance(meta["address"], dict)
                    print(f"[Test][OSM Converter] Address field: {meta['address']}")
                    
                    for addr_key, addr_value in processed_addr_tags.items():
                        addr_type = addr_key.split(":", 1)[1]
                        print(f"[Test][OSM Converter] Checking {addr_type}: {addr_value}")
                        self.assertIn(addr_type, meta["address"])
                        self.assertEqual(meta["address"][addr_type], addr_value)
        
        print(f"[Test][OSM Converter] Output: processed {address_count} elements with address tags")
    
    def test_opening_hours_processing(self):
        print("[Test][OSM Converter] Opening Hours Processing")
        self.converter.read_json(self.test_data)
        self.converter.clean_data()
        
        hours_count = 0
        print(f"[Test][OSM Converter] Input: checking {len(self.converter.cleansed)} elements for opening_hours")
        
        for element_id, cleansed_element in self.converter.cleansed.items():
            original_element = next(e for e in self.converter.raw if e["id"] == element_id)
            tags = original_element.get("tags", {})
            
            if "opening_hours" in tags:
                hours_count += 1
                meta = cleansed_element["meta"]
                print(f"[Test][OSM Converter] Element {element_id} has opening_hours: {tags['opening_hours']}")
                self.assertIn("tags", meta)
                self.assertIn("opening_hours", meta["tags"])
                self.assertEqual(meta["tags"]["opening_hours"], tags["opening_hours"])
                
                content = cleansed_element["content"]
                print(f"[Test][OSM Converter] Content contains opening_hours: {'opening_hours=' in content}")
                self.assertIn("opening_hours=", content)
        
        print(f"[Test][OSM Converter] Output: found {hours_count} elements with opening hours")
    
    def test_name_processing(self):
        print("[Test][OSM Converter] Name Processing")
        self.converter.read_json(self.test_data)
        self.converter.clean_data()
        
        name_count = 0
        print(f"[Test][OSM Converter] Input: checking {len(self.converter.cleansed)} elements for names")
        
        for element_id, cleansed_element in self.converter.cleansed.items():
            meta = cleansed_element["meta"]
            
            if "name" in meta:
                name_count += 1
                print(f"[Test][OSM Converter] Element {element_id} has name: {meta['name']}")
                self.assertIsNotNone(meta["name"])
                self.assertIsInstance(meta["name"], str)
                
                # 检查content中是否包含名称（注意capitalize处理）
                content = cleansed_element["content"]
                
                # 如果名称来自category（白名单标签），会被capitalize处理
                if "category" in meta and meta["category"] == meta["name"]:
                    expected_name_in_content = meta["name"].capitalize()
                    print(f"[Test][OSM Converter] Name from category, capitalized: {expected_name_in_content}")
                else:
                    expected_name_in_content = meta["name"]
                    print(f"[Test][OSM Converter] Name from name field: {expected_name_in_content}")
                
                print(f"[Test][OSM Converter] Content: '{content}'")
                print(f"[Test][OSM Converter] Name in content: {expected_name_in_content in content}")
                self.assertIn(expected_name_in_content, content)
        
        print(f"[Test][OSM Converter] Output: found {name_count} elements with names")
    
    def test_tag_normalization(self):
        print("[Test][OSM Converter] Tag Normalization")
        self.converter.read_json(self.test_data)
        self.converter.clean_data()
        
        norm_count = 0
        print(f"[Test][OSM Converter] Input: checking {len(self.converter.cleansed)} elements for normalized tags")
        
        for element_id, cleansed_element in self.converter.cleansed.items():
            meta = cleansed_element["meta"]
            
            if "tags_norm" in meta:
                norm_count += 1
                tags_norm = meta["tags_norm"]
                print(f"[Test][OSM Converter] Element {element_id} has {len(tags_norm)} normalized tags: {list(tags_norm.keys())}")
                self.assertIsInstance(tags_norm, dict)
                
                # 检查标准化后的键名不包含特殊字符
                for norm_key in tags_norm.keys():
                    print(f"[Test][OSM Converter] Checking normalized key: '{norm_key}'")
                    self.assertNotIn(":", norm_key)
                    self.assertNotRegex(norm_key, r"[^0-9A-Za-z_]")
        
        print(f"[Test][OSM Converter] Output: found {norm_count} elements with normalized tags")
    
    def test_value_normalization(self):
        print("[Test][OSM Converter] Value Normalization")
        # 推测：yes/no值应该被转换为True/False
        test_values = {
            "yes": True,
            "no": False,
            "YES": True,
            "NO": False,
            "other": "other"
        }
        
        print(f"[Test][OSM Converter] Input: testing {len(test_values)} values")
        for input_val, expected_output in test_values.items():
            result = self.converter._norm_val(input_val)
            print(f"[Test][OSM Converter] '{input_val}' -> {result} (expected: {expected_output})")
            self.assertEqual(result, expected_output)
        
        print(f"[Test][OSM Converter] Output: all {len(test_values)} values normalized correctly")
    
    def test_key_normalization(self):
        print("[Test][OSM Converter] Key Normalization")
        # 推测：键名应该被标准化
        test_cases = [
            ("addr:street", "addr_street"),
            ("opening_hours", "opening_hours"),
            ("wheelchair", "wheelchair"),
            ("contact:phone", "contact_phone")
        ]
        
        print(f"[Test][OSM Converter] Input: testing {len(test_cases)} key normalization cases")
        for input_key, expected_output in test_cases:
            result = self.converter._norm_key(input_key)
            print(f"[Test][OSM Converter] '{input_key}' -> '{result}' (expected: '{expected_output}')")
            self.assertEqual(result, expected_output)
        
        print(f"[Test][OSM Converter] Output: all {len(test_cases)} keys normalized correctly")
    
    def test_get_methods(self):
        print("[Test][OSM Converter] Getter Methods")
        self.converter.read_json(self.test_data)
        self.converter.clean_data()
        
        print(f"[Test][OSM Converter] Input: converter has {len(self.converter.raw)} raw elements, {len(self.converter.cleansed)} cleansed elements")
        
        # 推测：getter方法应该返回正确的数据
        raw_data = self.converter.get_raw()
        cleansed_data = self.converter.get_cleansed()
        
        print(f"[Test][OSM Converter] Output: get_raw() returned {len(raw_data)} elements")
        print(f"[Test][OSM Converter] Output: get_cleansed() returned {len(cleansed_data)} elements")
        
        self.assertEqual(raw_data, self.converter.raw)
        self.assertEqual(cleansed_data, self.converter.cleansed)
        
        print(f"[Test][OSM Converter] Verification: getter methods return correct data")
    
    def test_get_top_n_tags(self):
        print("[Test][OSM Converter] Get Top N Tags")
        self.converter.read_json(self.test_data)
        
        print(f"[Test][OSM Converter] Input: tag_freq has {len(self.converter.tag_freq)} unique tags")
        
        # 推测：应该返回最常用的标签集合
        top_10_tags = self.converter.get_top_n_tags(10)
        top_20_tags = self.converter.get_top_n_tags(20)
        
        print(f"[Test][OSM Converter] Output: top_10_tags = {len(top_10_tags)} tags")
        print(f"[Test][OSM Converter] Output: top_20_tags = {len(top_20_tags)} tags")
        print(f"[Test][OSM Converter] Top 10 tags: {list(top_10_tags)}")
        
        self.assertIsInstance(top_10_tags, set)
        self.assertIsInstance(top_20_tags, set)
        self.assertLessEqual(len(top_10_tags), 10)
        self.assertLessEqual(len(top_20_tags), 20)
        self.assertLessEqual(len(top_10_tags), len(top_20_tags))
        
        print(f"[Test][OSM Converter] Verification: tag counts are correct")
    
    def test_content_generation(self):
        print("[Test][OSM Converter] Content Generation")
        self.converter.read_json(self.test_data)
        self.converter.clean_data()
        
        print(f"[Test][OSM Converter] Input: checking {len(self.converter.cleansed)} elements for content generation")
        
        content_stats = {"with_tags": 0, "without_tags": 0, "empty": 0}
        
        # 推测：content应该包含名称、地址和标签信息
        for element_id, cleansed_element in self.converter.cleansed.items():
            content = cleansed_element["content"]
            self.assertIsInstance(content, str)
            
            if not content:
                content_stats["empty"] += 1
            elif "Tags:" in content:
                content_stats["with_tags"] += 1
            else:
                content_stats["without_tags"] += 1
        
        print(f"[Test][OSM Converter] Output: content stats - With tags: {content_stats['with_tags']}, Without tags: {content_stats['without_tags']}, Empty: {content_stats['empty']}")
        
        # 显示几个示例content
        sample_count = 0
        for element_id, cleansed_element in self.converter.cleansed.items():
            if sample_count < 3:  # 只显示前3个示例
                content = cleansed_element["content"]
                print(f"[Test][OSM Converter] Sample content {sample_count + 1}: '{content}'")
                sample_count += 1


if __name__ == "__main__":
    unittest.main()