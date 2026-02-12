# 合规审核Agent

基于中国广告法、GB 28050（预包装食品营养标签通则）以及产品检测报告的智能合规审核系统，用于专业审核视频笔记内容（如小红书式的视频+文本笔记）的合规性。

## 项目结构

```
compliance_agent/
├── data/
│   └── rules.json              # 合规规则库配置文件
├── src/
│   ├── __init__.py
│   ├── config.py               # 配置文件
│   └── modules/
│       ├── __init__.py
│       ├── input_processor.py  # 输入处理模块
│       ├── compliance_checker.py  # 合规分析模块
│       └── report_generator.py    # 报告生成模块
├── output/                     # 输出报告目录
├── logs/                       # 日志目录
├── tests/                      # 测试目录
├── main.py                     # 命令行主程序入口
├── app.py                      # CustomTkinter桌面应用入口
├── app_tkinter.py              # 标准Tkinter桌面应用入口
├── run_app.py                 # 桌面应用启动器
└── requirements.txt            # 依赖文件
```

## 功能特性

### 1. 输入处理模块 (input_processor.py)
- 视频转录：使用Whisper将视频转换为文本
- 文本清洗：去除噪声和无关内容
- 营养数据提取：从文本中提取营养成分数据
- 营养声明提取：识别营养声称（如低糖、无脂等）
- PDF报告解析：解析检测报告PDF文件

### 2. 合规分析模块 (compliance_checker.py)
- **广告法审核**：
  - 绝对化用语检测（最佳、顶级、第一等）
  - 虚假宣传关键词检测（永不过敏、治愈一切等）
  - 医疗相关禁用词检测
  - 负面内容检测
- **GB 28050审核**：
  - 营养声称合规性检查（低糖、无糖、低脂等阈值验证）
  - 强制标示营养成分检查
  - NRV计算验证
- **检测报告比对**：
  - 声明值与报告值一致性检查
  - 误差阈值验证（默认20%）
- **AI语义分析**：
  - 基于BERT模型的语义违规检测

### 3. 报告生成模块 (report_generator.py)
- 多格式报告输出：JSON、TXT、HTML
- 详细的违规分析和修改建议
- 可视化的HTML报告界面

## 安装依赖

```bash
pip install -r requirements.txt
```

### 依赖说明
- `customtkinter`: 现代化桌面GUI框架（可选）
- `openai-whisper`: OpenAI Whisper 语音识别库（视频转录）
- `transformers`: 用于加载BERT模型
- `torch`: PyTorch深度学习框架
- `PyMuPDF`: PDF文件解析
- `spacy`: 自然语言处理
- `nltk`: 自然语言工具包
- `jieba`: 中文分词
- `pandas` / `numpy`: 数据处理

**注意：** Whisper 已安装，视频转录功能已可用！

## 使用方法

### 桌面应用（推荐）

#### 方式一：使用标准Tkinter界面（无需额外依赖）

```bash
# 启动桌面应用
python app_tkinter.py

# 或使用启动器
python run_app.py
```

#### 方式二：使用CustomTkinter现代化界面（需要安装customtkinter）

```bash
# 先安装customtkinter
pip install customtkinter

# 启动桌面应用
python app.py
```

桌面应用提供友好的图形界面，支持：
- 📁 视频文件选择
- 📄 检测报告上传
- ✍️ 文本内容输入
- 📊 实时审核进度
- 📑 一键打开HTML报告

**界面功能：**
1. **视频文件**：点击"选择视频"按钮上传视频文件（支持MP4、AVI、MOV等格式）
2. **检测报告**：点击"选择报告"按钮上传PDF检测报告
3. **笔记文本**：在文本框中输入或粘贴笔记内容
4. **开始审核**：点击"开始审核"按钮进行合规性检查
5. **查看结果**：审核完成后，结果会显示在下方文本框中
6. **打开报告**：点击"打开报告"按钮在浏览器中查看详细的HTML报告
7. **清空**：点击"清空"按钮重置所有输入

### 命令行使用

```bash
# 演示模式（无参数）
python main.py

# 审核文本内容
python main.py --text "这款产品是最佳的，低糖无负担"

# 从文件读取文本
python main.py --text-file input.txt

# 审核视频笔记
python main.py --video sample.mp4 --text "产品描述文本"

# 结合检测报告审核
python main.py --text "产品描述" --report test_report.pdf

# 指定输出格式
python main.py --text "产品描述" --output-format json
```

### Python API使用

```python
from main import ComplianceAgent

agent = ComplianceAgent()

# 审核文本
result = agent.check_text_only("这款产品是最佳的，低糖无负担")

# 审核视频笔记
result = agent.check_video_note(
    video_path="sample.mp4",
    note_text="产品描述文本",
    report_path="test_report.pdf"
)

# 查看结果
print(f"合规等级: {result['compliance_level']}")
print(f"违规数量: {result['issue_count']}")
for issue in result['issues']:
    print(f"- {issue['type']}: {issue['description']}")
```

## 合规等级说明

| 等级 | 描述 | 处理建议 |
|------|------|----------|
| 通过 | 符合相关法规要求 | 通过审核 |
| 建议优化 | 表述不够严谨 | 建议优化 |
| 一般违规 | 存在合规风险 | 限期修改 |
| 严重违规 | 涉及法律法规明确禁止的内容 | 立即下架整改 |

## 规则库配置

规则库位于 `data/rules.json`，包含：

1. **广告法规则**：绝对化用语、虚假宣传关键词、医疗相关禁用词等
2. **GB 28050规则**：强制标示营养成分、营养声称阈值、NRV参考值等
3. **检测报告规则**：匹配检查要求、报告要求等

可根据实际需求更新规则库。

## 输出报告

审核完成后，会在 `output/` 目录生成以下格式的报告：

- `compliance_report_YYYYMMDD_HHMMSS.json` - JSON格式报告
- `compliance_report_YYYYMMDD_HHMMSS.txt` - 文本格式报告
- `compliance_report_YYYYMMDD_HHMMSS.html` - HTML格式报告（推荐）

## 注意事项

1. **数据合规**：处理视频笔记时，遵守《个人信息保护法》，对用户数据进行匿名化处理
2. **模型选择**：建议使用本地模型（如bert-base-chinese）确保数据不出境
3. **准确性**：AI分析可能存在"幻觉"，建议人工复核重要内容
4. **规则更新**：法规标准（如GB28050）会定期更新，需及时更新规则库

## 技术架构

```
输入层: 视频/文本/PDF报告
    ↓
处理层: 文本清洗、数据提取、转录
    ↓
分析层: 规则匹配 + AI语义分析
    ↓
输出层: 多格式合规报告
```

## 扩展功能

- 集成数据库存储历史审核记录
- 支持批量处理
- Web界面（Streamlit/Flask）
- 自定义模型微调
- 第三方API集成（如阿里云通义千问）

## 许可证

本项目仅供学习和研究使用。
