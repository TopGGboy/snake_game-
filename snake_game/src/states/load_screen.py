import pygame
from src.components.info import Infinite_mode_info


class LoadScreen:
    def __init__(self, next="infinite_mode"):
        """
        初始化关卡加载界面
        """
        self.finished = False  # 状态完成标志，用于状态切换
        self.next = next
        self.timer = 0  # 计时器，用于控制界面显示时间

        if next == "infinite_mode":
            self.info = Infinite_mode_info("infinite_mode")

    def update(self, surface, keys):
        """
        更新加载界面
        :param surface: 绘制表面
        :param keys: 键盘按键状态
        """
        self.draw(surface)

        # 控制界面显示时间（2秒）
        if self.timer == 0:
            # 记录开始时间
            self.timer = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.timer > 2000:
            # 2秒后标记状态完成，切换到下一状态
            print("进入 无尽模式")
            self.finished = True
            self.timer = 0  # 重置计时器

    def draw(self, surface):
        """
        绘制加载界面
        :param surface: 绘制表面
        """
        surface.fill((0, 0, 0))  # 填充黑色背景
        self.info.draw(surface)  # 绘制关卡信息（如"第1关"等文字）
