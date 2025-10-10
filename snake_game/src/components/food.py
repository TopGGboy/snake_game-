"""
食物类定义 - 针对顺滑移动优化

版权所有 © 2025 "果香蛇踪"游戏开发团队
联系方式：3085678256@qq.com

本程序受版权法保护，未经授权禁止复制、修改、分发或用于商业用途。
"""
import os
import random
import pygame
import math
from typing import Tuple, List, Optional
from ..utils import tools
from ..configs.config import Config
from ..configs.game_balance import GameBalance
from ..utils.image_manager import get_image_manager


class Food(pygame.sprite.Sprite):
    """食物类 - 针对顺滑移动优化"""

    # 类级别的调试开关
    DEBUG_COLLISION = False

    def __init__(self, food_name: str = None, size: int = None, wall_manager=None):
        pygame.sprite.Sprite.__init__(self)

        # 随机选择食物类型或使用指定的类型
        self.food_name = food_name if food_name else GameBalance.get_random_food_type()

        # 获取食物配置
        food_config = GameBalance.get_food_config(self.food_name)

        self.size = size if size is not None else food_config["size"]
        self.config = Config.get_instance()
        self.wall_manager = wall_manager  # 墙壁管理器实例

        # 食物属性（需要在位置生成前设置）
        self.score_value = food_config["score_value"]
        self.display_name = food_config["name"]
        self.is_eaten = False

        # 碰撞检测半径（圆形碰撞，更适合顺滑移动）
        # 使用稍微大一点的碰撞半径，提高碰撞检测的容错性
        self.collision_radius = self.size * 0.5  # 比图片半径稍大

        # 加载食物图片
        self._load_image()

        # 初始化位置
        self.rect = self.image.get_rect()
        self.position = [0.0, 0.0]  # 使用浮点坐标支持顺滑移动
        self.randomize_position()

        print(
            f"食物 {self.display_name}({self.food_name}) 创建完成，尺寸: {self.image.get_size()}，分数: {self.score_value}")

    def _load_image(self) -> None:
        """加载并处理食物图片"""
        manager = get_image_manager()
        # 从管理器获取食物图片（图片应该已经在游戏初始化时预加载了）
        self.image = manager.get_food_image(self.food_name, self.size)

    def randomize_position(self, avoid_positions: Optional[List[Tuple[float, float]]] = None) -> None:
        """
        随机生成食物位置 - 适配顺滑移动，不再依赖网格
        :param avoid_positions: 要避免的位置列表（蛇的身体位置和墙壁位置）
        """
        if avoid_positions is None:
            avoid_positions = []

        max_attempts = 100
        margin = GameBalance.FOOD_GENERATION_PIXEL

        # 计算有效生成区域（考虑食物大小和边距）
        min_x = margin + self.collision_radius
        max_x = self.config.SCREEN_W - margin - self.collision_radius
        min_y = margin + self.collision_radius
        max_y = self.config.SCREEN_H - margin - self.collision_radius

        for _ in range(max_attempts):
            # 随机生成浮点坐标位置
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            position = (x, y)

            # 检查是否与避免位置冲突（包括蛇身体和墙壁）
            if not self._is_position_occupied(position, avoid_positions):
                self.position = [x, y]
                self.rect.center = (int(x), int(y))
                print(f"食物生成在位置: ({x:.1f}, {y:.1f}) - 安全位置")
                return

        # 如果找不到合适位置，使用屏幕中心（确保中心位置安全）
        center_x = self.config.SCREEN_W / 2
        center_y = self.config.SCREEN_H / 2
        if self._is_position_away_from_walls((center_x, center_y)):
            self.position = [center_x, center_y]
            self.rect.center = (int(center_x), int(center_y))
            print(f"警告: 无法找到合适的食物位置，使用屏幕中心: ({center_x}, {center_y})")
        else:
            # 如果中心也不安全，强制使用安全位置
            safe_x = max(min_x, min(max_x, center_x))
            safe_y = max(min_y, min(max_y, center_y))
            self.position = [safe_x, safe_y]
            self.rect.center = (int(safe_x), int(safe_y))
            print(f"警告: 强制使用安全位置: ({safe_x:.1f}, {safe_y:.1f})")

    def _is_position_occupied(self, position: Tuple[float, float], avoid_positions: List[Tuple[float, float]]) -> bool:
        """
        检查位置是否被占用 - 使用圆形碰撞检测
        :param position: 要检查的位置
        :param avoid_positions: 要避免的位置列表（包含蛇身体和墙壁位置）
        :return: 是否被占用
        """
        # 使用更合理的安全距离，确保食物不会生成在蛇身上或墙壁上
        safe_distance = GameBalance.SMOOTH_COLLISION_RADIUS + self.collision_radius + 10

        # 检查避免位置列表（蛇身体和传入的墙壁位置）
        for avoid_pos in avoid_positions:
            distance = self._calculate_distance(position, avoid_pos)
            if distance < safe_distance:
                return True
        
        # 额外检查墙壁管理器中的墙壁位置
        if self.wall_manager:
            wall_positions = self.wall_manager.get_wall_positions()
            for wall_pos in wall_positions:
                distance = self._calculate_distance(position, wall_pos)
                if distance < safe_distance:
                    return True
        
        # 检查四周墙壁距离
        return not self._is_position_away_from_walls(position)

    def _is_position_away_from_walls(self, position: Tuple[float, float]) -> bool:
        """
        检查位置是否离墙壁足够远
        :param position: 要检查的位置
        :return: 是否离墙壁安全距离
        """
        x, y = position
        margin = GameBalance.FOOD_GENERATION_PIXEL
        
        # 检查距离四个墙壁的距离
        distance_to_left = x
        distance_to_right = self.config.SCREEN_W - x
        distance_to_top = y
        distance_to_bottom = self.config.SCREEN_H - y
        
        # 确保距离所有墙壁都大于边距
        min_distance = min(distance_to_left, distance_to_right, distance_to_top, distance_to_bottom)
        
        # 返回是否满足最小安全距离要求
        return min_distance >= margin

    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """计算两点之间的距离"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx * dx + dy * dy)

    def check_collision(self, snake_head_pos: Tuple[float, float], snake_head_radius: float = None) -> bool:
        """
        检查是否与蛇头发生碰撞 - 使用圆形碰撞检测
        :param snake_head_pos: 蛇头的中心位置
        :param snake_head_radius: 蛇头的碰撞半径
        :return: 是否发生碰撞
        """
        if snake_head_radius is None:
            snake_head_radius = GameBalance.SMOOTH_COLLISION_RADIUS

        distance = self._calculate_distance(self.position, snake_head_pos)
        collision_threshold = self.collision_radius + snake_head_radius

        # 调试信息
        is_collision = distance <= collision_threshold
        if Food.DEBUG_COLLISION:
            if is_collision:
                print(f"✅ 碰撞检测成功: 距离={distance:.2f}, 阈值={collision_threshold:.2f}")
                print(
                    f"   食物位置=({self.position[0]:.1f}, {self.position[1]:.1f}), 蛇头位置=({snake_head_pos[0]:.1f}, {snake_head_pos[1]:.1f})")
            else:
                # 只在距离很近但没有碰撞时输出调试信息
                if distance < collision_threshold * 1.5:
                    print(f"⚠️  接近但未碰撞: 距离={distance:.2f}, 阈值={collision_threshold:.2f}")

        return is_collision

    def get_eaten(self) -> int:
        """
        食物被吃掉
        :return: 获得的分数
        """
        self.is_eaten = True
        return self.score_value

    def reset(self, avoid_positions: Optional[List[Tuple[int, int]]] = None) -> None:
        """
        重置食物状态，包括重新随机选择食物类型
        :param avoid_positions: 要避免的位置列表
        """
        # 重新随机选择食物类型
        self.food_name = GameBalance.get_random_food_type()
        food_config = GameBalance.get_food_config(self.food_name)

        # 更新食物属性
        self.size = food_config["size"]
        self.score_value = food_config["score_value"]
        self.display_name = food_config["name"]

        # 重新加载图片
        self._load_image()

        # 重置状态和位置
        self.is_eaten = False
        self.collision_radius = self.size * 0.5
        self.rect = self.image.get_rect()
        self.randomize_position(avoid_positions)

        print(
            f"食物重置为 {self.display_name}({self.food_name})，尺寸: {self.image.get_size()}，分数: {self.score_value}")

    def set_wall_manager(self, wall_manager) -> None:
        """
        设置墙壁管理器实例
        :param wall_manager: 墙壁管理器实例
        """
        self.wall_manager = wall_manager

    def get_position(self) -> Tuple[float, float]:
        """获取食物中心位置（浮点坐标）"""
        return (self.position[0], self.position[1])

    def get_position_int(self) -> Tuple[int, int]:
        """获取食物中心位置（整数坐标，用于绘制）"""
        return (int(self.position[0]), int(self.position[1]))

    def draw(self, surface: pygame.Surface, debug_collision: bool = False) -> None:
        """
        绘制食物
        :param surface: 绘制表面
        :param debug_collision: 是否绘制碰撞区域调试信息
        """
        if not self.is_eaten:
            surface.blit(self.image, self.rect)

            # 调试：绘制食物碰撞圆圈
            if debug_collision:
                pygame.draw.circle(surface, (0, 255, 0),
                                   (int(self.position[0]), int(self.position[1])),
                                   int(self.collision_radius), 2)

    def update(self, dt: int) -> None:
        """
        更新食物状态（可以添加动画效果）
        :param dt: 时间增量
        """
        # 这里可以添加食物的动画效果，比如闪烁、旋转等
        pass


class FoodManager:
    """食物管理器 - 管理多个食物"""

    def __init__(self, max_food_count: int = 1, wall_manager=None):
        self.max_food_count = max_food_count
        self.foods: List[Food] = []
        self.score = 0
        self.wall_manager = wall_manager

        # 创建初始食物
        for _ in range(self.max_food_count):
            food = Food(wall_manager=self.wall_manager)
            self.foods.append(food)

    def update(self, dt: int, snake_head_pos: Tuple[float, float], snake_body_positions: List[Tuple[float, float]],
               snake_head_rect: pygame.Rect = None) -> int:
        """
        更新所有食物 - 支持顺滑移动
        :param dt: 时间增量
        :param snake_head_pos: 蛇头位置（浮点坐标）
        :param snake_body_positions: 蛇身体位置列表（浮点坐标）
        :param snake_head_rect: 蛇头矩形（向后兼容）
        :return: 本次更新获得的分数
        """
        score_gained = 0

        for food in self.foods:
            if food.is_eaten:  # 跳过已经被吃掉的食物
                continue

            food.update(dt)

            # 使用圆形碰撞检测（更精确）
            collision_detected = False
            if snake_head_pos:
                collision_detected = food.check_collision(snake_head_pos)

            if collision_detected and not food.is_eaten:  # 确保食物没有被重复吃掉
                score_gained += food.get_eaten()
                self.score += score_gained

                # 重新生成食物位置，避开蛇的所有部分
                avoid_positions = snake_body_positions.copy()
                if snake_head_pos:
                    avoid_positions.append(snake_head_pos)
                food.reset(avoid_positions)

                print(f"吃到{food.display_name}！获得 {food.score_value} 分，总分: {self.score}")

        return score_gained

    def draw(self, surface: pygame.Surface, debug_collision: bool = False) -> None:
        """绘制所有食物"""
        for food in self.foods:
            food.draw(surface, debug_collision)

    def get_food_positions(self) -> List[Tuple[float, float]]:
        """获取所有食物的位置（浮点坐标）"""
        return [food.get_position() for food in self.foods if not food.is_eaten]

    def get_food_positions_int(self) -> List[Tuple[int, int]]:
        """获取所有食物的位置（整数坐标，用于向后兼容）"""
        return [food.get_position_int() for food in self.foods if not food.is_eaten]

    def reset(self) -> None:
        """重置所有食物"""
        self.score = 0
        for food in self.foods:
            food.reset()

    def set_wall_manager(self, wall_manager) -> None:
        """
        设置墙壁管理器实例
        :param wall_manager: 墙壁管理器实例
        """
        self.wall_manager = wall_manager
        for food in self.foods:
            food.set_wall_manager(wall_manager)
