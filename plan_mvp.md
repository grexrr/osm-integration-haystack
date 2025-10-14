<!-- 4d92198c-3ce4-493b-b93a-b4fdf7a4f0c5 bc6fbe89-dc19-476c-a97f-4aee86905eb8 -->
# OSM Haystack Integration MVP

## 目标

创建一个可运行的最小演示，展示 OSM 数据查询并转换为 Haystack Documents，参考 [duckduckgo-api-haystack](https://github.com/GivAlz/duckduckgo-api-haystack) 的实现模式。

## 核心实现

### 1. Overpass API 客户端

**文件**: `src/haystack_osm_connector/clients/overpass.py`

实现基础查询功能：

- 简单的 HTTP 请求封装
- 支持边界框 + 标签查询（如查询某区域的餐厅）
- 错误处理和超时设置
- 返回 JSON 格式的 OSM 数据

### 2. OSM 到 Document 转换器

**文件**: `src/haystack_osm_connector/converters/osm_to_documents.py`

将 OSM 元素转换为 Haystack Document：

- 提取节点/路径的名称、标签作为元数据
- 生成可读的文本内容（如 "餐厅名称位于经度x纬度y"）
- 每个 OSM 元素 → 一个 Document

### 3. OSMFetcher 组件

**文件**: `src/haystack_osm_connector/components/osm_fetcher.py`

参考 DuckduckgoApiWebSearch 的模式：

- 使用 `@component` 装饰器
- `run()` 方法接收查询参数
- 返回 `{"documents": [...], "links": [...]}`
- 配置参数：`top_k`, `timeout` 等

### 4. 项目配置

**文件**: `pyproject.toml`, `requirements.txt`

修正当前配置：

- 更新包名为 `haystack_osm_connector`
- 添加依赖：`haystack-ai`, `requests`
- 修复 setuptools 配置

### 5. 演示示例

**文件**: `examples/basic_usage.py`

简单的使用示例：

- 查询某个城市（如罗马）的餐厅
- 打印返回的 Documents
- 展示如何在 Pipeline 中使用

## 技术要点

- **Overpass QL 查询语法**：使用简单的标签查询，如 `node["amenity"="restaurant"](bbox)`
- **API 端点**：`https://overpass-api.de/api/interpreter`
- **Document 结构**：
- `content`: 人类可读的描述
- `meta`: 包含坐标、标签、OSM ID 等

## MVP 范围限制

**包含**：

- 基于边界框的简单查询
- 节点（node）类型的支持
- 基础错误处理

**不包含**：

- Nominatim 地理编码（暂不需要）
- 复杂的 Overpass QL 查询
- 路径（way）和关系（relation）支持
- 单元测试（演示优先）
- 地理距离计算

### To-dos

- [ ] 修正 pyproject.toml 和创建 requirements.txt
- [ ] 实现 Overpass API 客户端基础查询功能
- [ ] 实现 OSM 到 Haystack Document 的转换器
- [ ] 完成 OSMFetcher 组件实现
- [ ] 创建演示示例 examples/basic_usage.py
- [ ] 更新 README.md 添加安装和使用说明