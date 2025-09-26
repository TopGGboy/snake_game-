import pygame
from src.components.snake import Snake
from src.configs.config import Config


class InfiniteMode:
    def __init__(self):
        """
        初始化无尽模式
        """
        self.finished = False
        self.next = None
        self.snake = Snake("snake0")  # 创建蛇实例
        # 设置蛇的初始位置到屏幕中心
        self.snake.rect.center = (400, 300)

        # 获取屏幕尺寸
        self.config = Config.get_instance()
        self.screen_width = self.config.SCREEN_W
        self.screen_height = self.config.SCREEN_H

        # 时间管理
        self.last_time = pygame.time.get_ticks()

    def update(self, surface, keys):
        """
        更新游戏状态
        :param surface: 绘制表面
        :param keys: 键盘按键状态
        """
        # 计算时间增量
        current_time = pygame.time.get_ticks()
        dt = current_time - self.last_time
        self.last_time = current_time

        # 处理蛇的键盘输入（只处理方向改变，不立即移动）
        self.snake.handle_input(keys)

        # 基于时间更新蛇的位置
        self.snake.update(dt)

        # 检查碰撞
        self._check_collisions()

        # 绘制游戏元素
        self.draw(surface)

    def _check_collisions(self):
        """
        检查所有碰撞情况
        """
        # 检查是否撞到自己
        if self.snake.check_self_collision():
            self.snake.dead = True
            print("游戏结束：蛇撞到自己了！")
            return

        # 检查是否撞到边界
        if self.snake.check_boundary_collision(screen_width=self.screen_width, screen_height=self.screen_height):
            self.snake.dead = True
            print("游戏结束：蛇撞到边界了！")
            return

    def draw(self, surface):
        """
        绘制游戏画面
        :param surface: 绘制表面
        """
        surface.fill((0, 0, 0))  # 填充黑色背景
        self.snake.draw(surface)  # 绘制蛇
