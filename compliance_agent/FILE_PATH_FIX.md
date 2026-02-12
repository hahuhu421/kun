# 文件路径问题解决指南

## 🎯 问题描述

错误信息：
```
❌ [错误] 系统找不到指定的文件: C:\Users\admin\Pictures\video.mp4
```

## 🔍 问题分析

### 常见原因

1. **文件确实不存在**
   - 该路径下没有 `video.mp4` 文件
   - 文件被移动或删除
   - 路径拼写错误

2. **Windows 路径格式问题**
   - 反斜杠 (`\\`) 和正斜杠 (`/`) 混用
   - 路径编码错误
   - 路径大小写问题

3. **权限问题**
   - 没有访问该文件的权限
   - 文件被其他程序锁定
   - 磁盘权限设置限制

4. **文件系统问题**
   - 磁盘损坏
   - 文件系统错误
   - 路径长度超过限制

5. **路径解析问题**
   - Python 的 Path 对象无法正确解析路径
   - 环境变量问题
   - 系统路径配置问题

## ✅ 解决方案

### 方案 1：确认文件存在性（基础）

1. **打开文件资源管理器**
2. **导航到 `C:\Users\admin\Pictures\`**
3. **确认是否存在 `video.mp4` 文件**
4. **如果不存在，复制视频文件到该位置**

### 方案 2：使用项目目录（推荐）

**步骤：**
1. **复制视频文件**到 `D:\dszx\compliance_agent\` 目录
2. **重命名**为 `test_video.mp4`
3. **启动应用**，选择该文件

**命令：**
```bash
# 复制文件
copy "原文件路径.mp4" "D:\dszx\compliance_agent\test_video.mp4"
```

### 方案 3：使用诊断工具

**文件路径诊断：**
```bash
cd compliance_agent
python diagnose_file_path.py "C:\Users\admin\Pictures\video.mp4"
```

**文件路径修复：**
```bash
python fix_file_path.py "C:\Users\admin\Pictures\video.mp4"
```

### 方案 4：检查替代路径

常见的用户目录路径：
- `C:\Users\admin\Pictures\video.mp4`
- `C:/Users/admin/Pictures/video.mp4`
- `c:\Users\admin\Pictures\video.mp4`
- `c:/Users/admin/Pictures/video.mp4`

### 方案 5：重命名文件

**推荐的文件名：**
- `video.mp4`
- `test_video.mp4`
- `demo.mp4`
- `sample.mp4`

**避免的文件名：**
- 过长的中文名称（超过 20 个字符）
- 特殊字符（`、/、:、*、?、"、<、>、|`）
- 空格
- 连续的句号或逗号

## 🔧 详细故障排除

### 步骤 1：基本检查

1. **确认文件存在**
   - 在文件资源管理器中检查
   - 尝试双击打开文件

2. **检查路径格式**
   - 确认路径拼写正确
   - 检查反斜杠和正斜杠
   - 检查大小写

3. **检查文件权限**
   - 右键文件 → 属性 → 安全
   - 确认当前用户有访问权限

### 步骤 2：使用工具诊断

**运行诊断工具：**
```bash
# 诊断文件路径
python diagnose_file_path.py "C:\Users\admin\Pictures\video.mp4"

# 修复文件路径
python fix_file_path.py "C:\Users\admin\Pictures\video.mp4"
```

**查看日志：**
```bash
# Windows
type logs\compliance_agent.log

# 搜索错误
findstr /C:"系统找不到指定的文件" logs\compliance_agent.log
```

### 步骤 3：高级修复

**1. 以管理员身份运行**
- 右键应用 → 以管理员身份运行

**2. 复制到其他位置**
```bash
# 复制到桌面
copy "原文件路径.mp4" "C:\Users\admin\Desktop\video.mp4"

# 复制到文档目录
copy "原文件路径.mp4" "C:\Users\admin\Documents\video.mp4"
```

**3. 检查磁盘**
- 运行磁盘检查工具
- 修复文件系统错误

**4. 重启系统**
- 有时候重启可以解决文件锁定问题

## 💡 最佳实践

### 文件命名建议

✅ **推荐的文件名格式：**
- `video.mp4`
- `test_video.mp4`
- `demo.mp4`
- `sample_001.mp4`

❌ **避免的文件名格式：**
- 过长的中文名称（超过 20 个字符）
- 特殊字符（`、/、:、*、?、"、<、>、|`）
- 空格
- 连续的句号或逗号

### 路径建议

✅ **推荐的路径：**
- 项目目录下的相对路径
- 桌面或文档目录
- 避免深层嵌套的目录

❌ **避免的路径：**
- 过长的绝对路径
- 包含特殊字符的路径
- 网络驱动器路径（如不存在的 Z: 盘）

## 📋 快速解决步骤

### 选项1：重命名后选择（最快）

1. 在文件资源管理器中找到文件
2. 重命名为 `video.mp4`
3. 打开应用
4. 选择 `video.mp4`

### 选项2：复制到项目目录（推荐）

1. 复制文件到 `D:/dszx/compliance_agent/` 目录
2. 重命名为 `test_video.mp4`
3. 打开应用
4. 选择 `test_video.mp4`

### 选项3：创建测试视频（最简单）

如果只是测试功能，可以：

1. 下载一个简单的测试视频
2. 放在项目目录下
3. 命名为 `test_video.mp4`
4. 使用这个文件测试

## 🆘 如果问题仍然存在

### 检查以下几点

- [ ] 文件是否真的存在？
- [ ] 文件名是否包含特殊字符？
- [ ] 路径是否正确？
- [ ] 是否有权限访问该文件？

### 使用诊断工具

```bash
cd compliance_agent
python diagnose_file_path.py "文件完整路径"
```

### 查看日志

```bash
# Windows
type logs\compliance_agent.log

# 搜索文件路径错误
findstr /C:I "系统找不到指定的文件"
```

## 📝 总结

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 文件找不到 | 文件名过长/特殊字符 | 重命名为简单英文名 |
| 路径错误 | 路径格式/编码问题 | 复制到简单路径 |
| 权限问题 | 文件被占用/权限不足 | 关闭其他程序/以管理员运行 |

**推荐操作：** 将文件重命名为 `video.mp4` 后重新选择
