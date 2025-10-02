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
        # 皮肤设置
        self.skin_id = 0  # 当前选择的皮肤ID（整数）

    @classmethod
    def get_instance(cls):
        """
        获取Config单例实例
        :return: Config实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_skin_id(self, skin_id: int):
        """设置当前皮肤ID"""
        self.skin_id = skin_id

    def get_skin_id(self) -> int:
        """获取当前皮肤ID"""
        return self.skin_id
        
    def set_selected_level(self, level_info):
        """设置选中的关卡信息"""
        self.selected_level = level_info
        
    def get_selected_level(self):
        """获取选中的关卡信息"""
        return getattr(self, 'selected_level', None)