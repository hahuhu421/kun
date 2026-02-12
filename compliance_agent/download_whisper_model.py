"""
Whisper 模型手动下载脚本
用于解决网络连接问题导致的模型下载失败
"""

import os
import sys
from pathlib import Path

def download_model_manually():
    """手动下载 Whisper 模型"""
    print("=" * 60)
    print("Whisper 模型手动下载工具")
    print("=" * 60)
    
    try:
        import whisper
    except ImportError:
        print("❌ Whisper 未安装，请先运行: pip install openai-whisper")
        return
    
    print("\n可用的模型:")
    print("  1. tiny   (~40MB)   - 最快，准确率较低")
    print("  2. base   (~75MB)   - 快，准确率中等  ← 推荐")
    print("  3. small  (~250MB)  - 中等，准确率较高")
    print("  4. medium (~770MB)  - 慢，准确率高")
    print("  5. large  (~1550MB) - 最慢，准确率最高")
    
    print("\n正在下载 base 模型...")
    print("提示: 首次下载需要一些时间，请耐心等待...")
    
    try:
        import whisper
        model = whisper.load_model("base")
        print("\n✅ 模型下载并加载成功！")
        print(f"   模型已缓存到: {whisper._MODELS['base']}")
        print("\n现在可以正常使用视频转录功能了！")
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        print("\n解决方案:")
        print("   1. 检查网络连接")
        print("   2. 尝试使用 VPN 或代理")
        print("   3. 使用更小的模型（tiny）")
        print("\n   使用 tiny 模型:")
        print("   python -c \"import whisper; whisper.load_model('tiny')\"")

def clear_model_cache():
    """清理 Whisper 模型缓存"""
    print("\n" + "=" * 60)
    print("清理 Whisper 模型缓存")
    print("=" * 60)
    
    import os
    
    cache_dir = os.path.expanduser("~/.cache/whisper")
    
    if os.path.exists(cache_dir):
        print(f"\n缓存目录: {cache_dir}")
        
        models = []
        for item in os.listdir(cache_dir):
            if item.endswith('.pt') or item.endswith('.safetensors'):
                models.append(item)
                print(f"  - {item}")
        
        if models:
            choice = input("\n是否删除这些模型文件？(y/n): ").strip().lower()
            if choice == 'y':
                for model in models:
                    model_path = os.path.join(cache_dir, model)
                    os.remove(model_path)
                    print(f"  已删除: {model}")
                print("\n✅ 缓存已清理")
            else:
                print("\n取消清理")
        else:
            print("\n缓存目录为空")
    else:
        print(f"\n缓存目录不存在: {cache_dir}")

def main():
    print("\n" + "=" * 60)
    print("Whisper 模型管理工具")
    print("=" * 60)
    
    print("\n可用操作:")
    print("  1. 下载/加载 Whisper 模型")
    print("  2. 清理模型缓存")
    print("  3. 退出")
    
    choice = input("\n请选择操作 (1/2/3): ").strip()
    
    if choice == '1':
        download_model_manually()
    elif choice == '2':
        clear_model_cache()
    elif choice == '3':
        print("\n退出")
    else:
        print("\n无效选择")

if __name__ == "__main__":
    main()
