"""
食物类定义
"""
import random
import pygame


class Food:
    def __init__(self, config):
        self.config = config
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        """随机生成食物位置"""
        grid_width = self.config.screen_width // self.config.grid_size
        grid_height = self.config.screen_height // self.config.grid_size

        self.position = (
            random.randint(0, grid_width - 1) * self.config.grid_size,
            random.randint(0, grid_height - 1) * self.config.grid_size
        )

    def draw(self, surface):
        """绘制食物"""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (self.config.grid_size, self.config.grid_size)
        )
        pygame.draw.rect(surface, self.config.food_color, rect)
        pygame.draw.rect(surface, (100, 0, 0), rect, 1)  # 边框
