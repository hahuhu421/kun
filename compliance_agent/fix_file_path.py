"""
文件路径修复工具
用于自动修复常见的文件路径问题
"""

import sys
import os
from pathlib import Path

def fix_windows_path(path):
    """修复 Windows 路径格式"""
    # 统一路径分隔符
    path = path.replace('\\', '/')
    
    # 处理多余的斜杠
    path = path.replace('//', '/')
    
    # 处理空格
    path = path.strip()
    
    return path

def find_alternative_paths(path):
    """查找可能的替代路径"""
    alternatives = []
    
    # 原始路径
    alternatives.append(path)
    
    # 反斜杠替换为正斜杠
    alternatives.append(path.replace('\\', '/'))
    
    # 正斜杠替换为反斜杠
    alternatives.append(path.replace('/', '\\'))
    
    # 去除空格
    alternatives.append(path.strip())
    
    # 尝试不同的大小写
    if path.startswith('C:'):
        alternatives.append(path.replace('C:', 'c:'))
    elif path.startswith('c:'):
        alternatives.append(path.replace('c:', 'C:'))
    
    # 尝试不同的目录结构
    if 'Users' in path and 'admin' in path:
        # 常见的用户目录路径
        base_paths = [
            'C:/Users/admin/',
            'C:\\Users\\admin\\',
            'c:/Users/admin/',
            'c:\\Users\\admin\\',
        ]
        
        # 提取路径的后半部分
        if 'Pictures' in path:
            suffix = path.split('Pictures', 1)[1]
            for base in base_paths:
                alternatives.append(base + 'Pictures' + suffix)
        elif 'Desktop' in path:
            suffix = path.split('Desktop', 1)[1]
            for base in base_paths:
                alternatives.append(base + 'Desktop' + suffix)
    
    return list(set(alternatives))

def check_alternative_paths(path):
    """检查替代路径是否存在"""
    print("=" * 60)
    print("检查替代路径")
    print("=" * 60)
    
    alternatives = find_alternative_paths(path)
    existing_paths = []
    
    for alt_path in alternatives:
        try:
            path_obj = Path(alt_path)
            if path_obj.exists():
                existing_paths.append(str(path_obj.resolve()))
                print(f"✅ 找到: {alt_path}")
            else:
                print(f"❌ 不存在: {alt_path}")
        except Exception as e:
            print(f"❌ 错误: {alt_path} - {e}")
    
    if existing_paths:
        print("\n" + "=" * 60)
        print("找到的有效路径:")
        print("=" * 60)
        for i, found_path in enumerate(existing_paths, 1):
            print(f"{i}. {found_path}")
        return existing_paths
    else:
        print("\n❌ 没有找到有效路径")
        return []

def suggest_fixes(path):
    """提供路径修复建议"""
    print("\n" + "=" * 60)
    print("修复建议")
    print("=" * 60)
    
    # 常见问题和解决方案
    suggestions = [
        "1. 检查文件是否存在",
        "2. 检查路径格式是否正确",
        "3. 尝试使用项目目录下的文件",
        "4. 重命名为简单英文名",
        "5. 复制文件到桌面或文档目录",
        "6. 以管理员身份运行应用",
        "7. 检查文件权限设置",
        "8. 尝试使用绝对路径",
        "9. 检查文件是否被其他程序占用",
        "10. 重启电脑后重试"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

def main():
    print("\n" + "=" * 60)
    print("文件路径修复工具")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"\n分析路径: {file_path}")
        
        # 修复路径格式
        fixed_path = fix_windows_path(file_path)
        print(f"\n修复后路径: {fixed_path}")
        
        # 检查替代路径
        existing_paths = check_alternative_paths(fixed_path)
        
        # 提供修复建议
        if not existing_paths:
            suggest_fixes(fixed_path)
        
        print("\n" + "=" * 60)
        print("使用建议")
        print("=" * 60)
        print("1. 选择一个找到的有效路径")
        print("2. 复制文件到项目目录")
        print("3. 重命名文件为简单英文名")
        print("4. 尝试使用相对路径")
        
    else:
        print("\n使用方法:")
        print("  python fix_file_path.py [文件路径]")
        print("\n示例:")
        print("  python fix_file_path.py \"C:\\Users\\admin\\Pictures\\video.mp4\"")
        print("  python fix_file_path.py \"C:/Users/admin/Pictures/video.mp4\"")

if __name__ == "__main__":
    main()
