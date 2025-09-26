"""
网格工具类 - 提供网格对齐和位置计算功能
"""
from typing import Tuple, List


class GridUtils:
    """网格工具类"""
    
    GRID_SIZE = 20  # 标准网格大小，与蛇的移动步长一致
    
    @classmethod
    def align_to_grid(cls, x: int, y: int) -> Tuple[int, int]:
        """
        将坐标对齐到网格
        :param x: x坐标
        :param y: y坐标
        :return: 对齐后的坐标
        """
        aligned_x = (x // cls.GRID_SIZE) * cls.GRID_SIZE
        aligned_y = (y // cls.GRID_SIZE) * cls.GRID_SIZE
        return (aligned_x, aligned_y)
    
    @classmethod
    def get_grid_center(cls, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """
        获取网格中心点坐标
        :param grid_x: 网格x索引
        :param grid_y: 网格y索引
        :return: 中心点坐标
        """
        center_x = grid_x * cls.GRID_SIZE + cls.GRID_SIZE // 2
        center_y = grid_y * cls.GRID_SIZE + cls.GRID_SIZE // 2
        return (center_x, center_y)
    
    @classmethod
    def get_valid_grid_range(cls, screen_width: int, screen_height: int, margin: int = 1) -> Tuple[int, int, int, int]:
        """
        获取有效的网格范围
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        :param margin: 边缘留白网格数
        :return: (min_grid_x, max_grid_x, min_grid_y, max_grid_y)
        """
        min_grid_x = margin
        max_grid_x = (screen_width // cls.GRID_SIZE) - margin
        min_grid_y = margin
        max_grid_y = (screen_height // cls.GRID_SIZE) - margin
        return (min_grid_x, max_grid_x, min_grid_y, max_grid_y)
    
    @classmethod
    def is_position_in_bounds(cls, x: int, y: int, screen_width: int, screen_height: int) -> bool:
        """
        检查位置是否在屏幕边界内
        :param x: x坐标
        :param y: y坐标
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        :return: 是否在边界内
        """
        return (cls.GRID_SIZE <= x <= screen_width - cls.GRID_SIZE and 
                cls.GRID_SIZE <= y <= screen_height - cls.GRID_SIZE)
    
    @classmethod
    def calculate_distance(cls, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        计算两点间距离
        :param pos1: 位置1
        :param pos2: 位置2
        :return: 距离
        """
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return (dx * dx + dy * dy) ** 0.5
    
    @classmethod
    def get_adjacent_positions(cls, x: int, y: int) -> List[Tuple[int, int]]:
        """
        获取相邻的网格位置（上下左右）
        :param x: x坐标
        :param y: y坐标
        :return: 相邻位置列表
        """
        return [
            (x, y - cls.GRID_SIZE),  # 上
            (x, y + cls.GRID_SIZE),  # 下
            (x - cls.GRID_SIZE, y),  # 左
            (x + cls.GRID_SIZE, y)   # 右
        ]