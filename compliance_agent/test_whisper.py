"""
Whisper 诊断测试脚本
用于诊断 Whisper 安装和模型加载问题
"""

import sys
import os

def test_whisper_import():
    """测试 Whisper 是否可以导入"""
    print("=" * 60)
    print("测试 1: Whisper 导入")
    print("=" * 60)
    
    try:
        import whisper
        print("✅ Whisper 导入成功")
        print(f"   版本: {whisper.__version__ if hasattr(whisper, '__version__') else '未知'}")
        return True
    except ImportError as e:
        print(f"❌ Whisper 导入失败: {e}")
        print("\n解决方案:")
        print("   pip install openai-whisper")
        return False

def test_torch():
    """测试 PyTorch 是否可用"""
    print("\n" + "=" * 60)
    print("测试 2: PyTorch 检查")
    print("=" * 60)
    
    try:
        import torch
        print(f"✅ PyTorch 导入成功")
        print(f"   版本: {torch.__version__}")
        print(f"   CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA 版本: {torch.version.cuda}")
            print(f"   GPU 数量: {torch.cuda.device_count()}")
        return True
    except ImportError as e:
        print(f"❌ PyTorch 导入失败: {e}")
        print("\n解决方案:")
        print("   pip install torch")
        return False

def test_system_memory():
    """检查系统内存"""
    print("\n" + "=" * 60)
    print("测试 3: 系统资源检查")
    print("=" * 60)
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        print(f"✅ 总内存: {total_gb:.2f} GB")
        print(f"✅ 可用内存: {available_gb:.2f} GB")
        
        if available_gb < 2:
            print("⚠️  警告: 可用内存不足 2GB，可能无法加载 Whisper 模型")
            print("   建议: 关闭其他程序或使用更小的模型（tiny）")
        else:
            print("✅ 内存充足，可以加载 Whisper 模型")
        
        return True
    except ImportError:
        print("⚠️  psutil 未安装，跳过内存检查")
        print("   安装: pip install psutil")
        return None

def test_whisper_model_loading():
    """测试 Whisper 模型加载"""
    print("\n" + "=" * 60)
    print("测试 4: Whisper 模型加载")
    print("=" * 60)
    
    try:
        import whisper
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   使用设备: {device}")
        
        print("\n   正在加载 Whisper 模型（base）...")
        print("   首次加载会下载模型文件，请耐心等待...")
        
        model = whisper.load_model("base", device=device)
        
        print("✅ Whisper 模型加载成功！")
        print(f"   模型类型: base")
        print(f"   设备: {device}")
        
        del model
        return True
        
    except MemoryError as e:
        print(f"❌ 内存不足: {e}")
        print("\n解决方案:")
        print("   1. 关闭其他程序释放内存")
        print("   2. 使用更小的模型（tiny）")
        print("   3. 重启电脑")
        return False
        
    except Exception as e:
        print(f"❌ 模型加载失败: {type(e).__name__}")
        print(f"   错误详情: {e}")
        print("\n可能原因:")
        print("   1. 网络连接问题（首次下载模型）")
        print("   2. 磁盘空间不足")
        print("   3. 模型文件损坏")
        print("\n解决方案:")
        print("   1. 检查网络连接")
        print("   2. 清理磁盘空间")
        print("   3. 删除 ~/.cache/whisper/ 目录并重试")
        return False

def test_video_file(video_path):
    """测试视频文件"""
    print("\n" + "=" * 60)
    print("测试 5: 视频文件检查")
    print("=" * 60)
    
    from pathlib import Path
    
    if not video_path:
        print("⚠️  未提供视频文件路径")
        return False
    
    path = Path(video_path)
    
    if not path.exists():
        print(f"❌ 文件不存在: {video_path}")
        return False
    
    print(f"✅ 文件存在: {video_path}")
    print(f"   文件大小: {path.stat().st_size / (1024*1024):.2f} MB")
    print(f"   文件格式: {path.suffix}")
    
    return True

def main():
    """主测试函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Whisper 诊断测试工具" + " " * 28 + "║")
    print("╚" + "═" * 58 + "╝")
    
    results = []
    
    results.append(test_whisper_import())
    results.append(test_torch())
    results.append(test_system_memory())
    results.append(test_whisper_model_loading())
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("\n✅ 所有测试通过！Whisper 应该可以正常工作。")
        print("\n下一步:")
        print("   1. 启动应用: python app.py 或 python app_tkinter.py")
        print("   2. 选择视频文件进行转录测试")
    else:
        print("\n❌ 部分测试失败，请根据上述提示解决问题。")
        print("\n常见解决方案:")
        print("   1. 安装依赖: pip install -r requirements.txt")
        print("   2. 重启应用")
        print("   3. 查看日志: logs/compliance_agent.log")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        test_video_file(video_path)
    else:
        main()
