import sys
import subprocess
from pathlib import Path

def check_dependencies():
    required_packages = [
        "transformers",
        "torch",
        "openai-whisper",
        "PyMuPDF",
        "spacy",
        "nltk",
        "jieba",
        "pandas",
        "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "openai-whisper":
                __import__("whisper")
            elif package == "PyMuPDF":
                __import__("fitz")
            else:
                __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("=" * 60)
        print("缺少必要的依赖包")
        print("=" * 60)
        print("\n请运行以下命令安装依赖：")
        print(f"pip install -r requirements.txt")
        print("\n缺少的包：")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\n安装完成后，请重新运行此脚本")
        return False
    
    return True

def main():
    print("=" * 60)
    print("合规审核Agent - 桌面应用启动器")
    print("=" * 60)
    
    if not check_dependencies():
        input("\n按回车键退出...")
        sys.exit(1)
    
    print("\n正在启动桌面应用...")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "app_tkinter.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n应用已关闭")
    except Exception as e:
        print(f"\n启动失败: {e}")
        input("\n按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()
