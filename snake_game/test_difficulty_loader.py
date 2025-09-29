"""
测试难度配置加载器
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.configs.difficulty_loader import get_difficulty_loader

def test_difficulty_loader():
    """测试难度配置加载器"""
    print("=== 测试难度配置加载器 ===")
    
    loader = get_difficulty_loader()
    
    # 测试获取可用难度
    print("\n1. 获取可用难度:")
    difficulties = loader.get_available_difficulties()
    print(f"可用难度: {difficulties}")
    
    # 测试加载每个难度配置
    print("\n2. 加载难度配置:")
    for difficulty in difficulties:
        print(f"\n--- 加载 {difficulty} ---")
        config = loader.load_difficulty_config(difficulty)
        if config:
            print(f"名称: {config['name']}")
            print(f"描述: {config['description']}")
            print(f"网格尺寸: {config['grid_size']}")
            print(f"蛇配置: {config['snake']}")
            print(f"游戏设置: {config['game_settings']}")
            
            # 测试墙体位置转换
            wall_positions = loader.convert_map_to_walls(config)
            print(f"墙体数量: {len(wall_positions)}")
            if wall_positions:
                print(f"前5个墙体位置: {wall_positions[:5]}")
            
            # 测试蛇初始位置
            snake_pos = loader.get_snake_initial_position(config)
            print(f"蛇初始位置: {snake_pos}")
        else:
            print(f"加载失败: {difficulty}")

if __name__ == "__main__":
    test_difficulty_loader()