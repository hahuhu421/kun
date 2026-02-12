# 合规审核Agent - 项目架构文档

## 1. 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     合规审核Agent                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  输入处理层   │───▶│  合规分析层   │───▶│  报告生成层   │  │
│  │              │    │              │    │              │  │
│  │ • 视频转录   │    │ • 规则匹配   │    │ • JSON报告   │  │
│  │ • 文本清洗   │    │ • AI语义分析 │    │ • TXT报告    │  │
│  │ • 数据提取   │    │ • 营养审核   │    │ • HTML报告   │  │
│  │ • PDF解析    │    │ • 报告比对   │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │        │
│         ▼                    ▼                    ▼        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  数据存储    │    │  规则库      │    │  输出目录    │  │
│  │              │    │              │    │              │  │
│  │ • SQLite DB  │    │ • 广告法规则 │    │ • 报告文件   │  │
│  │ • 历史记录   │    │ • GB28050    │    │ • 日志文件   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 2. 模块详解

### 2.1 输入处理模块 (input_processor.py)

**功能：**
- 视频语音转文本（Whisper）
- 文本清洗和预处理
- 营养成分数据提取
- 营养声明识别
- PDF检测报告解析

**核心类：**
```python
class InputProcessor:
    - transcribe_video()      # 视频转录
    - clean_text()            # 文本清洗
    - extract_nutrition_data() # 营养数据提取
    - extract_nutrition_claims() # 营养声明提取
    - parse_pdf_report()      # PDF解析
    - process_input()         # 统一处理入口
```

### 2.2 合规分析模块 (compliance_checker.py)

**功能：**
- 广告法合规检查
- GB 28050营养标签审核
- 检测报告一致性验证
- AI语义分析

**核心类：**
```python
class ComplianceChecker:
    - check_absolute_words()    # 绝对化用语检测
    - check_false_advertising()  # 虚假宣传检测
    - check_medical_terms()      # 医疗术语检测
    - check_negative_content()   # 负面内容检测
    - check_nutrition_claims()   # 营养声明审核
    - check_report_consistency() # 报告一致性检查
    - ai_semantic_analysis()     # AI语义分析
    - check_compliance()         # 综合合规检查
```

### 2.3 报告生成模块 (report_generator.py)

**功能：**
- 多格式报告生成（JSON/TXT/HTML）
- 违规详情展示
- 修改建议生成
- 可视化报告界面

**核心类：**
```python
class ReportGenerator:
    - generate_report()       # 生成报告对象
    - save_json_report()      # 保存JSON报告
    - save_text_report()      # 保存TXT报告
    - save_html_report()      # 保存HTML报告
    - generate_all_formats() # 生成所有格式
```

## 3. 数据流

```
用户输入
   │
   ├─► 视频文件 (MP4/AVI等)
   ├─► 笔记文本
   └─► 检测报告 (PDF)
        │
        ▼
   输入处理模块
        │
        ├─► Whisper转录 → 文本
        ├─► 文本清洗 → 清洁文本
        ├─► 正则提取 → 营养数据
        └─► PDF解析 → 报告数据
             │
             ▼
      合规分析模块
             │
             ├─► 规则匹配 → 违规项
             ├─► 阈值验证 → 营养违规
             ├─► 数据比对 → 报告不匹配
             └─► AI分析 → 语义违规
                  │
                  ▼
           报告生成模块
                  │
                  ├─► JSON报告
                  ├─► TXT报告
                  └─► HTML报告
                       │
                       ▼
                    输出目录
```

## 4. 规则库结构

```
rules.json
├── 广告法
│   ├── 绝对化用语 (数组)
│   ├── 虚假宣传关键词 (数组)
│   ├── 医疗相关禁用词 (数组)
│   ├── 负面清单 (数组)
│   ├── 条款说明 (对象)
│   └── 证据要求 (字符串)
├── GB28050
│   ├── 强制标示 (数组)
│   ├── 营养声称阈值 (对象)
│   │   ├── 低糖
│   │   ├── 无糖
│   │   ├── 低脂
│   │   └── ...
│   ├── NRV参考值 (对象)
│   ├── 允许误差 (对象)
│   └── 豁免情况 (数组)
└── 检测报告
    ├── 匹配检查 (对象)
    ├── 报告要求 (数组)
    └── 必检项目 (数组)
```

## 5. 合规等级体系

| 等级 | 分数范围 | 颜色 | 处理建议 |
|------|----------|------|----------|
| 通过 | 0-25 | 绿色 | 通过审核 |
| 建议优化 | 26-50 | 黄色 | 建议优化 |
| 一般违规 | 51-75 | 橙色 | 限期修改 |
| 严重违规 | 76+ | 红色 | 立即下架整改 |

## 6. 技术栈

### 核心技术
- **Python 3.8+**: 主要编程语言
- **Transformers**: Hugging Face NLP库
- **PyTorch**: 深度学习框架

### NLP处理
- **BERT-base-chinese**: 中文预训练模型
- **Spacy**: 自然语言处理
- **NLTK**: 自然语言工具包
- **Jieba**: 中文分词

### 音视频处理
- **OpenAI Whisper**: 语音转文本

### 文档处理
- **PyMuPDF**: PDF解析

### 数据处理
- **Pandas**: 数据分析
- **NumPy**: 数值计算

## 7. 扩展功能

### 7.1 数据库集成
```python
# SQLite数据库存储历史审核记录
DATABASE_CONFIG = {
    "type": "sqlite",
    "path": DATA_DIR / "compliance.db"
}
```

### 7.2 Web界面
```python
# 可集成Streamlit或Flask
# Streamlit示例
import streamlit as st

st.title("合规审核Agent")
text_input = st.text_area("输入审核文本")
if st.button("开始审核"):
    result = agent.check_text_only(text_input)
    st.json(result)
```

### 7.3 批量处理
```python
# 批量审核多个文件
def batch_check(file_list):
    results = []
    for file in file_list:
        result = agent.check_video_note(video_path=file)
        results.append(result)
    return results
```

### 7.4 API服务
```python
# 可封装为RESTful API
from fastapi import FastAPI

app = FastAPI()
agent = ComplianceAgent()

@app.post("/check")
async def check_compliance(text: str):
    return agent.check_text_only(text)
```

## 8. 部署方案

### 8.1 本地部署
```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py --text "审核文本"
```

### 8.2 Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### 8.3 云服务部署
- 阿里云ECS + OSS
- 腾讯云CVM + COS
- AWS EC2 + S3

## 9. 安全与合规

### 9.1 数据隐私
- 本地模型处理，数据不出境
- 用户数据匿名化
- 遵守《个人信息保护法》

### 9.2 模型安全
- 定期更新规则库
- 人工复核机制
- 算法备案

### 9.3 审计追踪
- 完整日志记录
- 历史审核记录存储
- 操作可追溯

## 10. 性能优化

### 10.1 缓存机制
- 模型加载缓存
- 规则库缓存
- 结果缓存

### 10.2 并发处理
- 异步IO处理
- 多进程审核
- 批量处理优化

### 10.3 资源管理
- GPU加速（可选）
- 内存优化
- 模型量化

## 11. 维护与更新

### 11.1 规则更新
- 定期更新法规规则
- 监控新法规发布
- 用户反馈收集

### 11.2 模型优化
- 收集标注数据
- 模型微调
- 性能评估

### 11.3 版本管理
- 语义化版本号
- 变更日志
- 回滚机制
