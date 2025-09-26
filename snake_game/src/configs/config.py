"""
游戏配置类
"""
import pygame


class Config:
    _instance = None  # 单例实例

    SCREEN_W, SCREEN_H = 800, 600
    SCREEN_SIZE = (SCREEN_W, SCREEN_H)

    # 游戏帧率
    FPS = 60

    def __init__(self):
        # 是否在游戏主界面
        self.MAIN_MENU_FLAG = True

    @classmethod
    def get_instance(cls):
        """
        获取Config单例实例
        :return: Config实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance