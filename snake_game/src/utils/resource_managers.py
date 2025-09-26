# 资源管理器
import pygame.font

from src.utils import tools


class ResourceManager:
    def __init__(self):
        self.GRAPHIC = tools.load_graphics('assets/graphics')

        self.LEVEL_FONT = pygame.font.Font('resources/font/font_1.ttf', 50)
        self.OTHER_FONT = pygame.font.Font('resources/font/font_1.ttf', 30)

        self.MAIN_MENU_FONT = pygame.font.Font('resources/font/font_1.ttf', 40)