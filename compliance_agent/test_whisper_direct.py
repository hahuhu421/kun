#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试Whisper对临时文件的访问
"""

import whisper
import os
from pathlib import Path

def test_whisper_direct():
    """直接测试Whisper转录"""
    print("\n" + "="*60)
    print("直接测试Whisper文件访问")
    print("="*60 + "\n")
    
    # 加载模型
    print("加载Whisper模型...")
    model = whisper.load_model("base")
    print("模型加载成功！")
    
    # 测试不同的路径格式
    test_paths = [
        "temp/video.mp4",  # 相对路径
        "temp\\video.mp4",  # 反斜杠相对路径
        os.path.abspath("temp/video.mp4"),  # 绝对路径
        os.path.abspath("temp/video.mp4").replace('\\', '/'),  # 正斜杠绝对路径
    ]
    
    for i, path in enumerate(test_paths):
        print(f"\n测试路径 {i+1}: {path}")
        print("-" * 40)
        
        try:
            # 检查文件是否存在
            if not os.path.exists(path):
                print(f"❌ 文件不存在: {path}")
                continue
            
            print(f"✅ 文件存在: {path}")
            print(f"文件大小: {os.path.getsize(path) / (1024*1024):.2f} MB")
            
            # 尝试转录
            print("开始转录...")
            result = model.transcribe(path, language="zh")
            print(f"✅ 转录成功！")
            print(f"转录结果: {result['text'][:100]}...")
            break
            
        except Exception as e:
            print(f"❌ 错误: {type(e).__name__}: {str(e)}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    test_whisper_direct()
