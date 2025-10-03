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
        self.grid_size = size  # 墙块大小
        self.collision_radius = size * 0.4  # 碰撞半径，稍小于视觉大小

        # 创建墙块图像
        self._create_image()

        # 设置rect
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.position[0]), int(self.position[1]))

        # 墙块颜色配置（用于阴影和发光效果）
        self.colors = {
            'shadow': (20, 30, 50, 120),     # 半透明深蓝阴影
            'glow': (80, 100, 140, 60),      # 半透明蓝光效果
            'highlight': (140, 160, 180, 80) # 高光效果
        }

    def _create_image(self) -> None:
        """创建墙块图像"""
        self.image = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA)
        
        # 现代配色方案 - 深蓝灰色系
        brick_color = (70, 80, 100)        # 主砖块颜色 - 深蓝灰
        mortar_color = (50, 60, 80)        # 砖缝颜色 - 更深蓝灰
        highlight_color = (120, 140, 160)   # 高光颜色 - 浅蓝灰
        shadow_color = (30, 40, 60)        # 阴影颜色 - 深蓝黑
        
        # 创建渐变背景效果
        for y in range(self.grid_size):
            # 从顶部到底部的渐变
            factor = y / self.grid_size
            r = int(brick_color[0] * (1 - factor * 0.3))
            g = int(brick_color[1] * (1 - factor * 0.3))
            b = int(brick_color[2] * (1 - factor * 0.3))
            pygame.draw.line(self.image, (r, g, b), (0, y), (self.grid_size, y))
        
        # 添加砖块纹理效果
        # 水平分割线
        pygame.draw.line(self.image, mortar_color, (0, self.grid_size//2), 
                         (self.grid_size, self.grid_size//2), 2)
        
        # 垂直分割线（交错排列，更自然的砖墙效果）
        if self.grid_size >= 30:
            # 第一行砖块
            pygame.draw.line(self.image, mortar_color, (self.grid_size//3, 0), 
                             (self.grid_size//3, self.grid_size//2), 2)
            pygame.draw.line(self.image, mortar_color, (2*self.grid_size//3, 0), 
                             (2*self.grid_size//3, self.grid_size//2), 2)
            
            # 第二行砖块（交错排列）
            pygame.draw.line(self.image, mortar_color, (self.grid_size//6, self.grid_size//2), 
                             (self.grid_size//6, self.grid_size), 2)
            pygame.draw.line(self.image, mortar_color, (self.grid_size//2, self.grid_size//2), 
                             (self.grid_size//2, self.grid_size), 2)
            pygame.draw.line(self.image, mortar_color, (5*self.grid_size//6, self.grid_size//2), 
                             (5*self.grid_size//6, self.grid_size), 2)
        
        # 增强3D立体效果
        # 左上角高光（更柔和）
        for i in range(3):
            alpha = 100 - i * 30
            highlight = (highlight_color[0], highlight_color[1], highlight_color[2], alpha)
            pygame.draw.line(self.image, highlight, (i, i), (self.grid_size-i, i), 1)
            pygame.draw.line(self.image, highlight, (i, i), (i, self.grid_size-i), 1)
        
        # 右下角阴影（更柔和）
        for i in range(3):
            alpha = 100 - i * 30
            shadow = (shadow_color[0], shadow_color[1], shadow_color[2], alpha)
            pygame.draw.line(self.image, shadow, (self.grid_size-1-i, i), 
                             (self.grid_size-1-i, self.grid_size-i), 1)
            pygame.draw.line(self.image, shadow, (i, self.grid_size-1-i), 
                             (self.grid_size-i, self.grid_size-1-i), 1)

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
        # 绘制柔和阴影效果
        shadow_surface = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA)
        shadow_color = self.colors['shadow']
        pygame.draw.rect(shadow_surface, shadow_color, 
                         (0, 0, self.grid_size, self.grid_size), border_radius=3)
        
        shadow_pos = (int(self.position[0] - self.grid_size // 2 + 3),
                      int(self.position[1] - self.grid_size // 2 + 3))
        surface.blit(shadow_surface, shadow_pos)

        # 绘制主体墙块
        surface.blit(self.image, self.rect)

        # 添加多层发光边框效果
        # 外层发光（柔和蓝色光晕）
        outer_glow = pygame.Surface((self.grid_size + 8, self.grid_size + 8), pygame.SRCALPHA)
        pygame.draw.rect(outer_glow, self.colors['glow'], 
                         (0, 0, self.grid_size + 8, self.grid_size + 8), 
                         border_radius=7, width=3)
        
        outer_pos = (int(self.position[0] - (self.grid_size + 8) // 2),
                     int(self.position[1] - (self.grid_size + 8) // 2))
        surface.blit(outer_glow, outer_pos)
        
        # 内层高光（精致边框）
        inner_highlight = pygame.Surface((self.grid_size + 2, self.grid_size + 2), pygame.SRCALPHA)
        pygame.draw.rect(inner_highlight, self.colors['highlight'], 
                         (0, 0, self.grid_size + 2, self.grid_size + 2), 
                         border_radius=4, width=1)
        
        inner_pos = (int(self.position[0] - (self.grid_size + 2) // 2),
                     int(self.position[1] - (self.grid_size + 2) // 2))
        surface.blit(inner_highlight, inner_pos)

        # 调试：绘制碰撞圆圈
        if debug_collision:
            pygame.draw.circle(surface, (255, 0, 255),
                               (int(self.position[0]), int(self.position[1])),
                               int(self.collision_radius), 2)


class WallManager:
    """墙管理器 - 管理所有墙块"""

    def __init__(self):
        self.wall_size = GameBalance.GRID_SIZE
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
        wall_positions = loader.convert_map_to_walls(difficulty_config)

        self.load_from_positions(wall_positions)
        print(f"加载墙体配置: 网格大小={self.wall_size}px, 墙体数量={len(wall_positions)}")

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
