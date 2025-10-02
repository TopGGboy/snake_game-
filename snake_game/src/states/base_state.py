"""
游戏状态基类
"""
import pygame


class BaseState:
    """
    所有游戏状态的基类
    """
    
    def __init__(self):
        """
        初始化状态
        """
        self.finished = False
        self.next = None
        self.persist = {}
    
    def startup(self, persistent):
        """
        状态启动时调用
        :param persistent: 持久化数据
        """
        self.persist = persistent
        self.finished = False
        self.next = None
    
    def get_event(self, event):
        """
        处理事件
        :param event: pygame事件
        """
        pass
    
    def update(self, surface, keys):
        """
        更新状态
        :param surface: 绘制表面
        :param keys: 按键状态
        """
        pass
    
    def draw(self, surface):
        """
        绘制状态
        :param surface: 绘制表面
        """
        pass
    
    def cleanup(self):
        """
        状态清理时调用
        :return: 持久化数据
        """
        return self.persist