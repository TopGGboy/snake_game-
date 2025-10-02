"""
音频文件测试脚本
测试音频文件是否能被pygame正确播放
"""
import pygame
import os
import sys

def test_audio_file(file_path):
    """测试音频文件是否能被pygame播放"""
    print(f"测试音频文件: {file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 检查文件大小
    file_size = os.path.getsize(file_path)
    print(f"📊 文件大小: {file_size} 字节 ({file_size/1024/1024:.2f} MB)")
    
    # 初始化pygame mixer
    try:
        pygame.mixer.init()
        print("✅ pygame.mixer初始化成功")
    except Exception as e:
        print(f"❌ pygame.mixer初始化失败: {e}")
        return False
    
    # 尝试加载音频文件
    try:
        pygame.mixer.music.load(file_path)
        print("✅ 音频文件加载成功")
    except Exception as e:
        print(f"❌ 音频文件加载失败: {e}")
        return False
    
    # 尝试播放音频
    try:
        pygame.mixer.music.play()
        print("✅ 音频开始播放")
        
        # 等待播放几秒钟
        import time
        time.sleep(3)
        
        # 停止播放
        pygame.mixer.music.stop()
        print("✅ 音频播放测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 音频播放失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎵 音频文件测试开始")
    
    # 测试主音乐文件
    audio_files = [
        "assets/sound/main.mp3",
        "assets/sound/fallback.wav"
    ]
    
    for audio_file in audio_files:
        print(f"\n{'='*50}")
        success = test_audio_file(audio_file)
        if success:
            print(f"🎉 {audio_file} 测试通过！")
        else:
            print(f"⚠️ {audio_file} 测试失败")
        
        print(f"{'='*50}")
    
    print("\n测试完成")
    pygame.quit()

if __name__ == "__main__":
    main()