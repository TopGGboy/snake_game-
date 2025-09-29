"""
难度配置加载器
用于加载和管理不同难度的JSON配置文件
"""
import json
import os
from typing import Dict, Any, Optional
from ..utils.grid_utils import GridUtils


class DifficultyLoader:
    """难度配置加载器"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), 'difficulty')
        self.loaded_configs = {}
    
    def load_difficulty_config(self, difficulty_name: str) -> Optional[Dict[str, Any]]:
        """
        加载指定难度的配置文件
        :param difficulty_name: 难度名称 (easy, hard, hell)
        :return: 配置字典或None
        """
        if difficulty_name in self.loaded_configs:
            return self.loaded_configs[difficulty_name]
        
        config_file = os.path.join(self.config_dir, f"{difficulty_name}.json")
        
        if not os.path.exists(config_file):
            print(f"警告: 配置文件 {config_file} 不存在")
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置格式
            if self._validate_config(config):
                self.loaded_configs[difficulty_name] = config
                print(f"成功加载难度配置: {config['name']}")
                return config
            else:
                print(f"错误: 配置文件 {config_file} 格式无效")
                return None
                
        except json.JSONDecodeError as e:
            print(f"错误: 解析配置文件 {config_file} 失败: {e}")
            return None
        except Exception as e:
            print(f"错误: 加载配置文件 {config_file} 失败: {e}")
            return None
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置文件格式
        :param config: 配置字典
        :return: 是否有效
        """
        required_keys = ['name', 'grid_size', 'map', 'snake', 'food', 'game_settings']
        
        for key in required_keys:
            if key not in config:
                print(f"配置验证失败: 缺少必需字段 '{key}'")
                return False
        
        # 验证网格尺寸
        grid_size = config['grid_size']
        if 'width' not in grid_size or 'height' not in grid_size:
            print("配置验证失败: grid_size 缺少 width 或 height")
            return False
        
        # 验证地图数据
        map_data = config['map']
        if not isinstance(map_data, list) or len(map_data) != grid_size['height']:
            print("配置验证失败: 地图高度与 grid_size.height 不匹配")
            return False
        
        for row in map_data:
            if not isinstance(row, list) or len(row) != grid_size['width']:
                print("配置验证失败: 地图宽度与 grid_size.width 不匹配")
                return False
        
        return True
    
    def get_available_difficulties(self) -> list:
        """
        获取所有可用的难度配置
        :return: 难度名称列表
        """
        difficulties = []
        if os.path.exists(self.config_dir):
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    difficulty_name = filename[:-5]  # 移除 .json 扩展名
                    difficulties.append(difficulty_name)
        return sorted(difficulties)
    
    def convert_map_to_walls(self, config: Dict[str, Any], cell_size: int = 30) -> list:
        """
        将地图数据转换为墙体位置列表
        :param config: 难度配置
        :param cell_size: 网格单元大小
        :return: 墙体位置列表 [(x, y), ...]
        """
        wall_positions = []
        map_data = config['map']
        grid_size = config['grid_size']
        
        # 计算起始偏移，使地图居中
        from ..configs.config import Config
        game_config = Config.get_instance()
        
        start_x = (game_config.SCREEN_W - grid_size['width'] * cell_size) // 2
        start_y = (game_config.SCREEN_H - grid_size['height'] * cell_size) // 2
        
        for row_idx, row in enumerate(map_data):
            for col_idx, cell in enumerate(row):
                if cell == 1:  # 1 表示墙壁
                    x = start_x + col_idx * cell_size + cell_size // 2
                    y = start_y + row_idx * cell_size + cell_size // 2
                    wall_positions.append((x, y))
        
        return wall_positions
    
    def get_snake_initial_position(self, config: Dict[str, Any], cell_size: int = 30) -> tuple:
        """
        获取蛇的初始位置
        :param config: 难度配置
        :param cell_size: 网格单元大小
        :return: (x, y) 坐标
        """
        snake_config = config['snake']
        initial_pos = snake_config['initial_position']
        
        # 计算起始偏移
        from ..configs.config import Config
        game_config = Config.get_instance()
        grid_size = config['grid_size']
        
        start_x = (game_config.SCREEN_W - grid_size['width'] * cell_size) // 2
        start_y = (game_config.SCREEN_H - grid_size['height'] * cell_size) // 2
        
        x = start_x + initial_pos[0] * cell_size + cell_size // 2
        y = start_y + initial_pos[1] * cell_size + cell_size // 2
        
        return (x, y)


# 全局实例
_difficulty_loader = None

def get_difficulty_loader() -> DifficultyLoader:
    """获取难度配置加载器的全局实例"""
    global _difficulty_loader
    if _difficulty_loader is None:
        _difficulty_loader = DifficultyLoader()
    return _difficulty_loader