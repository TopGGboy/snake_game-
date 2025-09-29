"""
墙类 - 贪吃蛇游戏障碍物
"""
import pygame
import math
import json
import os
from typing import List, Tuple, Optional, Dict, Any
from ..configs.config import Config
from ..configs.game_balance import GameBalance


class Wall(pygame.sprite.Sprite):
    """墙类 - 单个墙块"""

    def __init__(self, position: Tuple[float, float], size: int = 30):
        pygame.sprite.Sprite.__init__(self)
        self.position = [float(position[0]), float(position[1])]  # 使用浮点坐标
        self.size = size
        self.collision_radius = size * 0.4  # 碰撞半径，稍小于视觉大小

        # 创建墙块图像
        self._create_image()

        # 设置rect
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.position[0]), int(self.position[1]))

        # 墙块颜色配置
        self.colors = {
            'fill': (100, 100, 100),  # 灰色填充
            'border': (60, 60, 60),  # 深灰色边框
            'highlight': (150, 150, 150),  # 浅灰色高光
            'shadow': (40, 40, 40)  # 阴影色
        }

    def _create_image(self) -> None:
        """创建墙块图像"""
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((100, 100, 100))  # 灰色填充

        # 添加边框
        pygame.draw.rect(self.image, (60, 60, 60), self.image.get_rect(), 2)

        # 添加高光效果（左上角）
        highlight_rect = pygame.Rect(2, 2, self.size // 3, self.size // 3)
        pygame.draw.rect(self.image, (150, 150, 150), highlight_rect)

    def check_collision(self, position: Tuple[float, float], radius: float) -> bool:
        """
        检查是否与指定位置和半径发生碰撞
        :param position: 检查的位置
        :param radius: 检查的半径
        :return: 是否发生碰撞
        """
        distance = self._calculate_distance(self.position, position)
        return distance < (self.collision_radius + radius)

    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """计算两点之间的距离"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx * dx + dy * dy)

    def get_position(self) -> Tuple[float, float]:
        """获取墙块位置"""
        return (self.position[0], self.position[1])

    def draw(self, surface: pygame.Surface, debug_collision: bool = False) -> None:
        """
        绘制墙块
        :param surface: 绘制表面
        :param debug_collision: 是否绘制碰撞区域调试信息
        """
        # 绘制阴影效果
        shadow_pos = (int(self.position[0] - self.size // 2 + 2),
                      int(self.position[1] - self.size // 2 + 2))
        shadow_rect = pygame.Rect(shadow_pos[0], shadow_pos[1], self.size, self.size)
        pygame.draw.rect(surface, self.colors['shadow'], shadow_rect)

        # 绘制主体墙块
        surface.blit(self.image, self.rect)

        # 调试：绘制碰撞圆圈
        if debug_collision:
            pygame.draw.circle(surface, (255, 0, 255),
                               (int(self.position[0]), int(self.position[1])),
                               int(self.collision_radius), 2)


class WallManager:
    """墙管理器 - 管理所有墙块"""

    def __init__(self, wall_size: int = 30):
        self.wall_size = wall_size
        self.walls: List[Wall] = []
        self.config = Config.get_instance()

    def add_wall(self, position: Tuple[float, float]) -> None:
        """
        添加单个墙块
        :param position: 墙块位置
        """
        wall = Wall(position, self.wall_size)
        self.walls.append(wall)

    def load_from_positions(self, positions: List[Tuple[float, float]]) -> None:
        """
        从位置列表加载墙块
        :param positions: 墙块位置列表
        """
        self.clear_walls()
        for position in positions:
            self.add_wall(position)
        print(f"加载了 {len(positions)} 个墙块")

    def load_from_difficulty_config(self, difficulty_config: Dict[str, Any]) -> None:
        """
        从难度配置加载墙块
        :param difficulty_config: 难度配置字典
        """
        from ..configs.difficulty_loader import get_difficulty_loader
        
        loader = get_difficulty_loader()
        wall_positions = loader.convert_map_to_walls(difficulty_config, self.wall_size)
        self.load_from_positions(wall_positions)

    def create_border_walls(self, margin: int = 30) -> None:
        """
        创建边界墙壁
        :param margin: 边界距离屏幕边缘的距离
        """
        self.clear_walls()
        
        # 顶部边界
        for x in range(margin, self.config.SCREEN_W - margin + 1, self.wall_size):
            self.add_wall((x, margin))
        
        # 底部边界
        for x in range(margin, self.config.SCREEN_W - margin + 1, self.wall_size):
            self.add_wall((x, self.config.SCREEN_H - margin))
        
        # 左侧边界
        for y in range(margin, self.config.SCREEN_H - margin + 1, self.wall_size):
            self.add_wall((margin, y))
        
        # 右侧边界
        for y in range(margin, self.config.SCREEN_H - margin + 1, self.wall_size):
            self.add_wall((self.config.SCREEN_W - margin, y))

    def create_maze_pattern(self) -> None:
        """
        创建迷宫图案（在边界墙壁基础上添加内部障碍）
        """
        # 添加一些内部墙壁形成迷宫
        center_x = self.config.SCREEN_W // 2
        center_y = self.config.SCREEN_H // 2
        
        # 中央十字形障碍
        for i in range(-3, 4):
            if i != 0:  # 留出中央通道
                self.add_wall((center_x + i * self.wall_size, center_y))
                self.add_wall((center_x, center_y + i * self.wall_size))
        
        # 四个角落的L形障碍
        corner_offset = 120
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            corner_x = center_x + dx * corner_offset
            corner_y = center_y + dy * corner_offset
            
            # L形障碍
            for i in range(3):
                self.add_wall((corner_x + dx * i * self.wall_size, corner_y))
                self.add_wall((corner_x, corner_y + dy * i * self.wall_size))

    def check_collision(self, position: Tuple[float, float], radius: float) -> bool:
        """
        检查指定位置是否与任何墙块碰撞
        :param position: 检查的位置
        :param radius: 检查的半径
        :return: 是否发生碰撞
        """
        for wall in self.walls:
            if wall.check_collision(position, radius):
                return True
        return False

    def get_wall_positions(self) -> List[Tuple[float, float]]:
        """获取所有墙块的位置"""
        return [wall.get_position() for wall in self.walls]

    def clear_walls(self) -> None:
        """清除所有墙块"""
        self.walls.clear()

    def get_wall_count(self) -> int:
        """获取墙块数量"""
        return len(self.walls)

    def draw(self, surface: pygame.Surface, debug_collision: bool = False) -> None:
        """
        绘制所有墙块
        :param surface: 绘制表面
        :param debug_collision: 是否绘制碰撞区域调试信息
        """
        for wall in self.walls:
            wall.draw(surface, debug_collision)

    def update(self, dt: int) -> None:
        """
        更新墙块状态（可以添加动画效果）
        :param dt: 时间增量
        """
        # 这里可以添加墙块的动画效果，比如闪烁、移动等
        pass



