"""
文件路径诊断工具
用于诊断视频文件路径问题
"""

import sys
from pathlib import Path

def check_file_path(file_path):
    """检查文件路径"""
    print("=" * 60)
    print("文件路径诊断")
    print("=" * 60)
    
    if not file_path:
        print("❌ 未提供文件路径")
        return False
    
    print(f"\n检查路径: {file_path}")
    
    path_obj = Path(file_path)
    
    print(f"\n1. 检查路径格式:")
    print(f"   - 原始路径: {file_path}")
    print(f"   - Path对象: {path_obj}")
    print(f"   - 是否绝对路径: {path_obj.is_absolute()}")
    print(f"   - 驱动器: {path_obj.drive}")
    print(f"   - 根目录: {path_obj.anchor}")
    print(f"   - 父目录: {path_obj.parent}")
    print(f"   - 文件名: {path_obj.name}")
    
    print(f"\n2. 检查文件存在性:")
    exists = path_obj.exists()
    print(f"   - 文件存在: {'✅ 是' if exists else '❌ 否'}")
    
    if exists:
        print(f"\n3. 检查文件类型:")
        print(f"   - 是文件: {'✅ 是' if path_obj.is_file() else '❌ 否'}")
        print(f"   - 是目录: {'✅ 是' if path_obj.is_dir() else '❌ 否'}")
        
        if path_obj.is_file():
            print(f"\n4. 检查文件属性:")
            try:
                stat = path_obj.stat()
                print(f"   - 文件大小: {stat.st_size / (1024*1024):.2f} MB")
                print(f"   - 修改时间: {stat.st_mtime}")
                print(f"   - 文件扩展名: {path_obj.suffix}")
            except Exception as e:
                print(f"   - 无法获取属性: {e}")
            
            print(f"\n5. 检查文件可读性:")
            try:
                with open(path_obj, 'rb') as f:
                    f.read(1)
                print("   - ✅ 文件可读")
            except PermissionError:
                print("   - ❌ 权限不足")
            except Exception as e:
                print(f"   - ❌ 读取失败: {e}")
    
    print(f"\n6. 检查路径编码:")
    try:
        encoded_path = file_path.encode('utf-8')
        print(f"   - UTF-8 编码: ✅")
        print(f"   - 编码后: {encoded_path}")
    except Exception as e:
        print(f"   - 编码失败: {e}")
    
    print(f"\n7. 建议的解决方案:")
    
    if not exists:
        print("   1. 检查文件是否真的存在")
        print("   2. 尝试使用相对路径")
        print("   3. 检查文件名是否正确")
    else:
        print("   1. 文件存在，但可能无法访问")
        print("   2. 检查文件权限")
        print("   3. 尝试复制文件到简单路径")
        print("   4. 使用英文或简短文件名")
    
    return exists

def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "文件路径诊断工具" + " " * 28 + "║")
    print("╚" + "═" * 58 + "╝")
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        check_file_path(file_path)
    else:
        print("\n使用方法:")
        print("  python diagnose_file_path.py [视频文件路径]")
        print("\n示例:")
        print("  python diagnose_file_path.py \"C:/Users/admin/Pictures/video.mp4\"")

if __name__ == "__main__":
    main()
