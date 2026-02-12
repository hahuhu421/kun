# Whisper 问题快速解决指南

## 🎯 问题诊断

根据测试结果，你的系统状态：

| 检查项 | 状态 | 说明 |
|--------|------|------|
| Whisper 安装 | ✅ 成功 | 版本 20250625 |
| PyTorch | ✅ 成功 | 版本 2.7.1+cpu |
| CUDA | ❌ 不可用 | 使用 CPU 模式 |
| 系统内存 | ✅ 充足 | 总 15.64GB，可用 2.04GB |
| 模型加载 | ❌ 失败 | 网络连接问题 |

## ❌ 问题原因

**Whisper 模型加载失败** 是由于：
- 网络连接问题（SSL 错误）
- 首次下载模型文件时连接中断

## ✅ 解决方案

### 方案1：手动下载模型（推荐）

```bash
cd compliance_agent
python download_whisper_model.py
```

选择操作 1，系统会：
- 自动下载 Whisper base 模型
- 缓存到本地
- 下载成功后可正常使用

### 方案2：使用更小的模型

如果网络不稳定，可以使用 tiny 模型（更快，更小）：

```bash
# 修改配置文件
# 在 src/config.py 中修改：
WHISPER_CONFIG = {
    "model_size": "tiny",  # 改为 tiny
    "language": "zh",
    "task": "transcribe"
}

# 或者在代码中直接使用
python -c "import whisper; whisper.load_model('tiny')"
```

### 方案3：使用离线模型

如果网络完全无法使用：

1. 在有网络的机器上下载模型
2. 复制模型文件到目标机器
3. 模型文件位置：
   - Windows: `C:\Users\[用户名]\.cache\whisper\base.pt`
   - Linux/Mac: `~/.cache/whisper/base.pt`

### 方案4：暂时禁用视频转录

如果暂时无法解决，可以先使用文本审核功能：

1. 在"笔记文本"框中手动输入文案
2. 不选择视频文件
3. 直接进行合规审核

## 🔧 详细步骤

### 步骤1：尝试手动下载

```bash
cd compliance_agent
python download_whisper_model.py
```

选择 **1**，等待下载完成。

### 步骤2：验证模型下载

```bash
python -c "import whisper; model = whisper.load_model('base'); print('模型加载成功')"
```

如果显示"模型加载成功"，说明问题已解决。

### 步骤3：启动应用

```bash
# 标准界面
python app_tkinter.py

# 或现代化界面
python app.py
```

### 步骤4：测试视频转录

1. 选择一个包含中文语音的视频文件
2. 点击"开始审核"
3. 查看"视频转录文本"框
4. 确认是否显示转录内容

## 💡 优化建议

### 1. 使用代理（如果需要）

```bash
# 设置环境变量
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080

# 然后运行
python download_whisper_model.py
```

### 2. 增加超时时间

```python
# 在 src/config.py 中添加：
WHISPER_CONFIG = {
    "model_size": "base",
    "language": "zh",
    "task": "transcribe",
    "timeout": 300  # 增加超时时间
}
```

### 3. 使用国内镜像

Whisper 模型下载使用的是 GitHub，可能需要代理。

## 📋 故障排除清单

- [ ] 运行了 `python download_whisper_model.py`？
- [ ] 模型下载成功？
- [ ] 验证模型可以加载？
- [ ] 启动应用后可以转录视频？
- [ ] "视频转录文本"框显示内容？

## 🆘 如果问题仍然存在

### 检查日志

查看详细错误信息：
```bash
# Windows
type logs\compliance_agent.log

# Linux/Mac
cat logs/compliance_agent.log
```

### 重新安装

如果模型文件损坏：

```bash
# 1. 清理缓存
python download_whisper_model.py
# 选择操作 2

# 2. 重新下载
python download_whisper_model.py
# 选择操作 1
```

### 联系支持

如果以上方法都无法解决，可能需要：
- 检查防火墙设置
- 检查网络代理配置
- 尝试使用其他网络连接

## 📝 总结

| 问题 | 状态 | 解决方案 |
|------|------|----------|
| Whisper 未安装 | ✅ 已解决 | 已安装 openai-whisper |
| PyTorch | ✅ 正常 | 版本 2.7.1 |
| 内存 | ✅ 充足 | 可用 2.04GB |
| CUDA | ⚠️ 不可用 | 使用 CPU 模式 |
| 模型加载 | ❌ 失败 | 运行 download_whisper_model.py |

**下一步：** 运行 `python download_whisper_model.py` 手动下载模型
