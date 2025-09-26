# 主菜单文件
import pygame
from src.utils.resource_managers import ResourceManager
from src.configs.config import Config


class MainMenu:
    def __init__(self):
        """
        初始化主菜单状态
        """
        self.resource_manager = ResourceManager()
        self.config = Config.get_instance()  # 使用单例模式

        self.setup_background()  # 初始化背景

        self.finished = False  # 状态机
        self.next = "load_screen"

    def update_cursor(self, event_key):
        """
        更新光标位置（处理键盘输入）
        :param event_key:  按下的键盘按键
        """
        area = []
        if event_key == pygame.K_w:  # 向上移动光标
            print("w")
        elif event_key == pygame.K_s:  # 向下移动光标
            print("s")
        elif event_key == pygame.K_RETURN:  # 确认选择
            print(1)
            self.finished = True
            self.config.MAIN_MENU_FLAG = False  # 设置不在主菜单状态

    def update(self, surface, keys):
        """
        更新主菜单界面
        :param surface:  绘制表面
        :param keys:  键盘按键状态
        :return:
        """

        surface.blit(self.background, self.viewport)  # 绘制背景

    # 初始化背景
    def setup_background(self):
        """
        设置主菜单背景图片
        """
        self.background = self.resource_manager.GRAPHIC["background"]  # 获取背景图片
        self.background_rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, self.config.SCREEN_SIZE)

        self.viewport = self.background.get_rect()  # 获取屏幕矩形区域