"""
演示JSON配置系统的使用
"""
import pygame
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.configs.difficulty_loader import get_difficulty_loader
from src.components.wall import WallManager
from src.configs.config import Config

def demo_wall_generation():
    """演示墙体生成"""
    print("=== 演示JSON配置墙体生成 ===")
    
    # 初始化pygame
    pygame.init()
    config = Config.get_instance()
    screen = pygame.display.set_mode(config.SCREEN_SIZE)
    pygame.display.set_caption("贪吃蛇 - JSON配置演示")
    clock = pygame.time.Clock()
    
    # 获取配置加载器
    loader = get_difficulty_loader()
    difficulties = loader.get_available_difficulties()
    
    current_difficulty_index = 0
    wall_manager = WallManager()
    
    # 加载第一个难度的墙体
    if difficulties:
        config_data = loader.load_difficulty_config(difficulties[current_difficulty_index])
        if config_data:
            wall_manager.load_from_difficulty_config(config_data)
    
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and difficulties:
                    # 切换到下一个难度
                    current_difficulty_index = (current_difficulty_index + 1) % len(difficulties)
                    config_data = loader.load_difficulty_config(difficulties[current_difficulty_index])
                    if config_data:
                        wall_manager.load_from_difficulty_config(config_data)
                        print(f"切换到难度: {config_data['name']}")
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清屏
        screen.fill((20, 20, 30))
        
        # 绘制墙体
        wall_manager.draw(screen, debug_collision=True)
        
        # 绘制UI信息
        if difficulties and current_difficulty_index < len(difficulties):
            current_config = loader.load_difficulty_config(difficulties[current_difficulty_index])
            if current_config:
                # 显示当前难度信息
                title_text = font.render(f"当前难度: {current_config['name']}", True, (255, 255, 255))
                screen.blit(title_text, (10, 10))
                
                desc_text = small_font.render(f"描述: {current_config['description']}", True, (200, 200, 200))
                screen.blit(desc_text, (10, 50))
                
                wall_count_text = small_font.render(f"墙体数量: {wall_manager.get_wall_count()}", True, (200, 200, 200))
                screen.blit(wall_count_text, (10, 80))
                
                speed_text = small_font.render(f"蛇速度: {current_config['snake']['speed']}", True, (200, 200, 200))
                screen.blit(speed_text, (10, 110))
                
                multiplier_text = small_font.render(f"分数倍率: {current_config['game_settings']['score_multiplier']}x", True, (200, 200, 200))
                screen.blit(multiplier_text, (10, 140))
        
        # 显示控制提示
        help_text = small_font.render("空格键: 切换难度  ESC: 退出", True, (150, 150, 150))
        screen.blit(help_text, (10, config.SCREEN_H - 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    demo_wall_generation()