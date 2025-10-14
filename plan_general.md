<!-- 3b9f2c19-5c41-4db0-a07f-de246aaab8e3 b74107ce-e414-49f0-a623-2f261ce1b670 -->
# Haystack OSM Connector 实现计划

## 项目结构设置

创建完整的 Python 包结构：

- `pyproject.toml` - 现代 Python 项目配置（使用 hatchling）
- 依赖项：`haystack-ai`, `requests`, `pydantic`
- 开发依赖：`pytest`, `pytest-cov`, `black`, `ruff`

## 核心组件实现

### 1. OSM 客户端层

**文件**: `src/haystack_osm_connector/clients/`

- `overpass_client.py` - Overpass API 查询客户端
- 支持按边界框、标签查询 OSM 数据
- 处理 API 响应和错误

- `nominatim_client.py` - Nominatim 地理编码客户端
- 地址搜索和反向地理编码
- 遵循 Nominatim 使用政策（user-agent 等）

### 2. 数据转换器

**文件**: `src/haystack_osm_connector/converters/osm_converter.py`

将 OSM 数据转换为 Haystack `Document` 对象：

- OSM 节点、路径、关系 → Haystack 文档
- 提取关键元数据（标签、坐标、类型）
- 生成可搜索的文本内容

### 3. Haystack 组件

**文件**: `src/haystack_osm_connector/components/`

- `osm_fetcher.py` - 自定义组件（类似 Haystack 的 Fetcher）
- 输入：查询参数（地点名称、边界框、标签）
- 输出：Haystack Document 列表
- 可集成到 Haystack Pipeline 中

- `osm_retriever.py` (可选进阶) - 基于位置的检索器
- 支持地理空间查询
- 距离计算和排序

### 4. 类型定义

**文件**: `src/haystack_osm_connector/types.py`

使用 Pydantic 定义数据模型：

- `OSMQuery` - 查询参数
- `OSMElement` - OSM 元素
- `BoundingBox` - 地理边界

## 测试

**目录**: `tests/`

- `test_overpass_client.py` - 客户端单元测试（使用 mock）
- `test_nominatim_client.py`
- `test_osm_converter.py` - 数据转换测试
- `test_osm_fetcher.py` - 组件集成测试

## 文档和示例

- **README.md** - 完整使用文档，包括：
- 安装说明
- 快速开始
- API 参考

- **examples/basic_usage.py** - 基础示例：
- 查询某个城市的餐厅
- 转换为 Haystack 文档

- **examples/pipeline_example.py** - Pipeline 集成示例：
- 在 Haystack Pipeline 中使用 OSM Fetcher
- 结合 RAG 应用场景

## 实现顺序

1. 项目配置和依赖管理
2. OSM 客户端（先 Overpass，后 Nominatim）
3. 数据转换器
4. Haystack Fetcher 组件
5. 测试
6. 文档和示例
7. （进阶）Retriever 组件

## 关键技术点

- **Haystack 组件规范**: 继承 `@component` 装饰器，定义 `run()` 方法
- **OSM 数据格式**: JSON 格式（Overpass QL 查询）
- **地理数据处理**: 经纬度、边界框计算
- **API 礼仪**: 限流、user-agent、缓存

### To-dos

- [ ] 创建 pyproject.toml 和项目配置文件
- [ ] 实现 Overpass API 客户端
- [ ] 实现 Nominatim API 客户端
- [ ] 实现 OSM 到 Haystack Document 转换器
- [ ] 实现 OSMFetcher Haystack 组件
- [ ] 编写单元测试和集成测试
- [ ] 创建使用示例和文档
- [ ] （可选）实现 OSMRetriever 高级组件