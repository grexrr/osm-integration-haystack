# OSM Integration Haystack Demo

## 环境设置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 创建环境变量文件
在项目根目录创建 `.env` 文件：

```bash
# 复制示例文件
cp .env.example .env
```

或者手动创建 `.env` 文件：
```
OPENAI_API_KEY=your-actual-openai-api-key-here
```

### 3. 运行Demo
```bash
cd examples
python agent_osm_demo.py
```

## 功能说明

- **完整版**: 使用OpenAI API进行智能分析，需要有效的API key
- **简化版**: 直接显示搜索结果，不需要API key

## 注意事项

- 确保网络连接正常
- Overpass API需要可访问
- OpenAI API key需要有效且有足够的额度
