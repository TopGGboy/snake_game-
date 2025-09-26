"""
食物类定义
"""
import os
import random
import pygame
from typing import Tuple, List, Optional
from ..utils import tools
from ..utils.grid_utils import GridUtils
from ..configs.config import Config
from ..configs.game_balance import GameBalance


class Food(pygame.sprite.Sprite):
    """食物类"""

    def __init__(self, food_name: str = "food0", size: int = None):
        pygame.sprite.Sprite.__init__(self)
        self.food_name = food_name
        self.size = size if size is not None else GameBalance.FOOD_SIZE
        self.config = Config.get_instance()

        # 加载食物图片
        self._load_image()

        # 初始化位置
        self.rect = self.image.get_rect()
        self.randomize_position()

        # 食物属性
        self.score_value = GameBalance.FOOD_SCORE_VALUE  # 使用平衡配置中的分数
        self.is_eaten = False

        print(f"食物 {self.food_name} 创建完成，尺寸: {self.image.get_size()}")

    def _load_image(self) -> None:
        """加载并处理食物图片"""
        from ..utils.image_manager import get_image_manager

        manager = get_image_manager()

        # 从管理器获取食物图片（图片应该已经在游戏初始化时预加载了）
        self.image = manager.get_food(self.food_name, self.size)

        if self.image is None:
            print(f"警告: 无法加载食物图片 {self.food_name}，使用默认图片")
            # 创建默认的红色方块作为备用
            self._create_default_image()

    def _create_default_image(self) -> None:
        """创建默认的食物图片（红色方块）"""
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.image.fill((255, 0, 0))  # 红色
        # 添加边框
        pygame.draw.rect(self.image, (150, 0, 0), self.image.get_rect(), 2)

    def randomize_position(self, avoid_positions: Optional[List[Tuple[int, int]]] = None) -> None:
        """
        随机生成食物位置，与蛇的移动网格完全对齐
        :param avoid_positions: 要避免的位置列表（如蛇的身体位置）
        """
        if avoid_positions is None:
            avoid_positions = []

        max_attempts = 100  # 最大尝试次数，避免无限循环

        # 获取有效的网格范围
        min_grid_x, max_grid_x, min_grid_y, max_grid_y = GridUtils.get_valid_grid_range(
            self.config.SCREEN_W, self.config.SCREEN_H, margin=GameBalance.FOOD_GENERATION_MARGIN
        )

        for _ in range(max_attempts):
            # 随机选择网格位置
            grid_x = random.randint(min_grid_x, max_grid_x - 1)
            grid_y = random.randint(min_grid_y, max_grid_y - 1)

            # 转换为像素坐标（网格中心）
            position = GridUtils.get_grid_center(grid_x, grid_y)

            # 检查是否与避免位置冲突
            if not self._is_position_occupied(position, avoid_positions):
                self.rect.center = position
                print(f"食物生成在网格位置: ({grid_x}, {grid_y}), 像素位置: {position}")
                return

        # 如果找不到合适位置，使用屏幕中心的网格对齐位置
        center_grid_x = (max_grid_x + min_grid_x) // 2
        center_grid_y = (max_grid_y + min_grid_y) // 2
        center_position = GridUtils.get_grid_center(center_grid_x, center_grid_y)
        self.rect.center = center_position
        print(f"警告: 无法找到合适的食物位置，使用默认网格对齐位置: {center_position}")

    def _is_position_occupied(self, position: Tuple[int, int], avoid_positions: List[Tuple[int, int]]) -> bool:
        """
        检查位置是否被占用
        :param position: 要检查的位置
        :param avoid_positions: 要避免的位置列表
        :return: 是否被占用
        """
        # 使用网格大小的一半作为碰撞检测阈值，确保精确对齐
        collision_threshold = GridUtils.GRID_SIZE // 2

        for avoid_pos in avoid_positions:
            distance = GridUtils.calculate_distance(position, avoid_pos)
            if distance < collision_threshold:
                return True
        return False

    def check_collision(self, snake_head_rect: pygame.Rect) -> bool:
        """
        检查是否与蛇头发生碰撞
        :param snake_head_rect: 蛇头的矩形
        :return: 是否发生碰撞
        """
        return self.rect.colliderect(snake_head_rect)

    def get_eaten(self) -> int:
        """
        食物被吃掉
        :return: 获得的分数
        """
        self.is_eaten = True
        return self.score_value

    def reset(self, avoid_positions: Optional[List[Tuple[int, int]]] = None) -> None:
        """
        重置食物状态
        :param avoid_positions: 要避免的位置列表
        """
        self.is_eaten = False
        self.randomize_position(avoid_positions)

    def get_position(self) -> Tuple[int, int]:
        """获取食物中心位置"""
        return self.rect.center

    def draw(self, surface: pygame.Surface) -> None:
        """
        绘制食物
        :param surface: 绘制表面
        """
        if not self.is_eaten:
            surface.blit(self.image, self.rect)

    def update(self, dt: int) -> None:
        """
        更新食物状态（可以添加动画效果）
        :param dt: 时间增量
        """
        # 这里可以添加食物的动画效果，比如闪烁、旋转等
        pass


class FoodManager:
    """食物管理器 - 管理多个食物"""

    def __init__(self, max_food_count: int = 1):
        self.max_food_count = max_food_count
        self.foods: List[Food] = []
        self.score = 0

        # 创建初始食物
        for _ in range(self.max_food_count):
            self.foods.append(Food())

    def update(self, dt: int, snake_head_rect: pygame.Rect, snake_body_positions: List[Tuple[int, int]]) -> int:
        """
        更新所有食物
        :param dt: 时间增量
        :param snake_head_rect: 蛇头矩形
        :param snake_body_positions: 蛇身体位置列表
        :return: 本次更新获得的分数
        """
        score_gained = 0

        for food in self.foods:
            food.update(dt)

            # 检查碰撞
            if food.check_collision(snake_head_rect):
                score_gained += food.get_eaten()
                self.score += score_gained

                # 重新生成食物位置
                avoid_positions = snake_body_positions + [snake_head_rect.center]
                food.reset(avoid_positions)

                print(f"吃到食物！获得 {food.score_value} 分，总分: {self.score}")

        return score_gained

    def draw(self, surface: pygame.Surface) -> None:
        """绘制所有食物"""
        for food in self.foods:
            food.draw(surface)

    def get_food_positions(self) -> List[Tuple[int, int]]:
        """获取所有食物的位置"""
        return [food.get_position() for food in self.foods if not food.is_eaten]

    def reset(self) -> None:
        """重置所有食物"""
        self.score = 0
        for food in self.foods:
            food.reset()
