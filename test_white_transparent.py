"""
测试白色转透明优化效果
"""
import pygame
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from snake_game.src.utils.tools import extract_main_subject

def test_white_transparent():
    """测试白色转透明效果"""
    pygame.init()
    
    print("开始测试白色转透明优化效果...")
    print("=" * 50)
    
    # 测试图片列表
    test_images = [
        "snake_game/assets/graphics/food/food0.png",
        "snake_game/assets/graphics/snake/snake0/snake0_head.png", 
        "snake_game/assets/graphics/snake/snake1/snake1_head.png"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n处理图片: {image_path}")
            
            # 处理图片
            processed_image = extract_main_subject(image_path)
            
            if processed_image:
                # 计算透明像素比例
                width, height = processed_image.get_size()
                transparent_count = 0
                total_pixels = width * height
                
                for x in range(width):
                    for y in range(height):
                        pixel = processed_image.get_at((x, y))
                        if len(pixel) == 4 and pixel[3] == 0:
                            transparent_count += 1
                
                transparency_ratio = (transparent_count / total_pixels) * 100
                print(f"✓ 处理成功 - 尺寸: {width}x{height}")
                print(f"  透明像素比例: {transparency_ratio:.2f}%")
                
                # 保存测试图片
                pygame.image.save(processed_image, f"test_{os.path.basename(image_path)}")
            else:
                print(f"✗ 处理失败")
        else:
            print(f"✗ 图片不存在: {image_path}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    pygame.quit()

if __name__ == "__main__":
    test_white_transparent()