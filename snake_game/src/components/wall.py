"""
墙类 - 贪吃蛇游戏障碍物
"""
import pygame
import math
from typing import List, Tuple, Optional
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

    def add_wall_line(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float],
                      spacing: float = None) -> None:
        """
        添加一条墙线
        :param start_pos: 起始位置
        :param end_pos: 结束位置
        :param spacing: 墙块间距，默认为墙块大小
        """
        if spacing is None:
            spacing = self.wall_size

        # 计算方向向量
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            self.add_wall(start_pos)
            return

        # 单位向量
        unit_x = dx / distance
        unit_y = dy / distance

        # 沿线添加墙块
        current_distance = 0
        while current_distance <= distance:
            wall_x = start_pos[0] + unit_x * current_distance
            wall_y = start_pos[1] + unit_y * current_distance
            self.add_wall((wall_x, wall_y))
            current_distance += spacing

    def add_wall_rectangle(self, top_left: Tuple[float, float],
                           bottom_right: Tuple[float, float],
                           filled: bool = False) -> None:
        """
        添加矩形墙
        :param top_left: 左上角位置
        :param bottom_right: 右下角位置
        :param filled: 是否填充内部
        """
        if filled:
            # 填充整个矩形
            spacing = self.wall_size
            y = top_left[1]
            while y <= bottom_right[1]:
                x = top_left[0]
                while x <= bottom_right[0]:
                    self.add_wall((x, y))
                    x += spacing
                y += spacing
        else:
            # 只绘制边框
            # 上边
            self.add_wall_line(top_left, (bottom_right[0], top_left[1]))
            # 下边
            self.add_wall_line((top_left[0], bottom_right[1]), bottom_right)
            # 左边
            self.add_wall_line(top_left, (top_left[0], bottom_right[1]))
            # 右边
            self.add_wall_line((bottom_right[0], top_left[1]), bottom_right)

    def create_border_walls(self, margin: int = 50) -> None:
        """
        创建屏幕边界墙
        :param margin: 距离屏幕边缘的距离
        """
        screen_w = self.config.SCREEN_W
        screen_h = self.config.SCREEN_H

        # 上边界
        self.add_wall_line((margin, margin), (screen_w - margin, margin))
        # 下边界
        self.add_wall_line((margin, screen_h - margin), (screen_w - margin, screen_h - margin))
        # 左边界
        self.add_wall_line((margin, margin), (margin, screen_h - margin))
        # 右边界
        self.add_wall_line((screen_w - margin, margin), (screen_w - margin, screen_h - margin))

    def create_maze_pattern(self) -> None:
        """创建简单的迷宫模式"""
        screen_w = self.config.SCREEN_W
        screen_h = self.config.SCREEN_H

        # 中央十字形障碍
        center_x = screen_w // 2
        center_y = screen_h // 2

        # 水平线
        self.add_wall_line((center_x - 100, center_y), (center_x + 100, center_y))
        # 垂直线
        self.add_wall_line((center_x, center_y - 80), (center_x, center_y + 80))

        # 四个角落的小障碍
        corner_size = 60
        # 左上角
        self.add_wall_rectangle((100, 100), (100 + corner_size, 100 + corner_size))
        # 右上角
        self.add_wall_rectangle((screen_w - 100 - corner_size, 100),
                                (screen_w - 100, 100 + corner_size))
        # 左下角
        self.add_wall_rectangle((100, screen_h - 100 - corner_size),
                                (100 + corner_size, screen_h - 100))
        # 右下角
        self.add_wall_rectangle((screen_w - 100 - corner_size, screen_h - 100 - corner_size),
                                (screen_w - 100, screen_h - 100))

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
