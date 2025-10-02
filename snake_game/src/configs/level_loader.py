"""
关卡配置加载器
用于加载和管理关卡配置文件
"""
import json
import os
from typing import Dict, Any, Optional, List
from .difficulty_loader import get_difficulty_loader


class LevelLoader:
    """关卡配置加载器"""

    def __init__(self):
        self.config_dir = '../configs/level'
        self.loaded_levels = {}

    def load_level_config(self, level_name: str) -> Optional[Dict[str, Any]]:
        """
        加载指定关卡的配置文件
        :param level_name: 关卡名称 (level_01, level_02, etc.)
        :return: 配置字典或None
        """
        if level_name in self.loaded_levels:
            return self.loaded_levels[level_name]

        config_file = os.path.join(level_name)

        if not os.path.exists(config_file):
            print(f"警告: 关卡配置文件 {config_file} 不存在")
            return None

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证配置格式
            if self._validate_config(config):
                self.loaded_levels[level_name] = config
                print(f"成功加载关卡配置: {config['name']}")
                return config
            else:
                print(f"错误: 关卡配置文件 {config_file} 格式无效")
                return None

        except json.JSONDecodeError as e:
            print(f"错误: 解析关卡配置文件 {config_file} 失败: {e}")
            return None
        except Exception as e:
            print(f"错误: 加载关卡配置文件 {config_file} 失败: {e}")
            return None

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证关卡配置文件格式
        :param config: 配置字典
        :return: 是否有效
        """
        required_keys = ['name', 'description', 'target_score', 'difficulty', 'map']

        for key in required_keys:
            if key not in config:
                print(f"关卡配置验证失败: 缺少必需字段 '{key}'")
                return False

        # 验证目标分数是正整数
        if not isinstance(config['target_score'], int) or config['target_score'] <= 0:
            print(f"关卡配置验证失败: target_score 必须是正整数")
            return False

        return True

    def get_available_levels(self) -> List[str]:
        """
        获取所有可用的关卡配置
        :return: 关卡名称列表
        """
        levels = []
        if os.path.exists(self.config_dir):
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    level_name = filename[:-5]  # 移除 .json 扩展名
                    levels.append(level_name)
        return sorted(levels)

    def get_level_difficulty_config(self, level_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取关卡对应的难度配置
        :param level_config: 关卡配置
        :return: 难度配置字典
        """
        difficulty_name = level_config['difficulty']
        difficulty_loader = get_difficulty_loader()
        return difficulty_loader.load_difficulty_config(difficulty_name)

    def get_level_info(self, level_name: str) -> Optional[Dict[str, Any]]:
        """
        获取关卡的基本信息（不加载完整配置）
        :param level_name: 关卡名称
        :return: 关卡信息字典
        """
        config = self.load_level_config(level_name)
        if not config:
            return None

        return {
            'name': config['name'],
            'description': config['description'],
            'target_score': config['target_score'],
            'difficulty': config['difficulty'],
            'completed': False  # 默认未完成
        }

    def get_all_levels_info(self) -> List[Dict[str, Any]]:
        """
        获取所有关卡的基本信息
        :return: 关卡信息列表
        """
        levels_info = []
        available_levels = self.get_available_levels()
        
        for level_name in available_levels:
            level_info = self.get_level_info(level_name)
            if level_info:
                levels_info.append(level_info)
        
        return levels_info


# 全局实例
_level_loader = None


def get_level_loader() -> LevelLoader:
    """获取关卡配置加载器的全局实例"""
    global _level_loader
    if _level_loader is None:
        _level_loader = LevelLoader()
    return _level_loader