#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试视频文件路径修复
"""

import sys
from src.modules.input_processor import InputProcessor

def test_video_transcription():
    """测试视频转录功能"""
    print("\n" + "="*60)
    print("测试视频文件路径修复")
    print("="*60 + "\n")
    
    # 创建输入处理器实例
    processor = InputProcessor()
    
    # 测试不同格式的路径
    test_paths = [
        "C:\\Users\\admin\\Pictures\\video.mp4",  # 原始反斜杠路径
        "C:/Users/admin/Pictures/video.mp4",      # 正斜杠路径
    ]
    
    for path in test_paths:
        print(f"\n测试路径: {path}")
        print("-" * 40)
        
        try:
            result = processor.transcribe_video(path)
            print(f"结果: {result[:100]}..." if len(result) > 100 else f"结果: {result}")
            
            if "[错误]" in result:
                print("❌ 失败")
            else:
                print("✅ 成功")
                
        except Exception as e:
            print(f"❌ 执行错误: {type(e).__name__}: {str(e)}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    test_video_transcription()
