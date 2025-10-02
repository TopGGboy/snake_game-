"""
关卡加载界面
"""
import pygame
from ..configs.config import Config
from ..utils.font_manager import get_font_manager


class LevelLoadingScreen:
    def __init__(self, current_level=1, total_levels=10):
        """
        初始化关卡加载界面
        :param current_level: 当前关卡
        :param total_levels: 总关卡数
        """
        self.config = Config.get_instance()
        self.font_manager = get_font_manager()
        
        self.current_level = current_level
        self.total_levels = total_levels
        
        # 加载进度
        self.progress = 0
        self.loading_speed = 2  # 加载速度
        self.finished = False
        
        # 动画效果
        self.animation_time = 0
        self.dots_count = 0
        self.dot_timer = 0

    def update(self, surface, keys):
        """
        更新加载界面
        :param surface: 绘制表面
        :param keys: 键盘按键状态
        """
        # 更新加载进度
        if self.progress < 100:
            self.progress = min(100, self.progress + self.loading_speed)
        else:
            self.finished = True
        
        # 更新动画
        self.animation_time += 0.016  # 假设60FPS
        self.dot_timer += 0.016
        if self.dot_timer >= 0.3:
            self.dots_count = (self.dots_count + 1) % 4
            self.dot_timer = 0
        
        # 绘制界面
        self.draw(surface)

    def draw(self, surface):
        """
        绘制加载界面
        :param surface: 绘制表面
        """
        # 清屏
        surface.fill((0, 0, 0))
        
        # 绘制关卡标题
        level_text = self.font_manager.render_text(f"第 {self.current_level} 关", 'title', (255, 255, 255))
        level_rect = level_text.get_rect(center=(self.config.SCREEN_W // 2, 150))
        surface.blit(level_text, level_rect)
        
        # 绘制进度条背景
        bar_width = 400
        bar_height = 20
        bar_x = (self.config.SCREEN_W - bar_width) // 2
        bar_y = 250
        
        # 进度条背景
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # 进度条前景
        progress_width = int(bar_width * self.progress / 100)
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, progress_width, bar_height))
        
        # 进度条边框
        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # 进度百分比
        percent_text = self.font_manager.render_text(f"{self.progress}%", 'medium', (200, 200, 200))
        percent_rect = percent_text.get_rect(center=(self.config.SCREEN_W // 2, bar_y + 35))
        surface.blit(percent_text, percent_rect)
        
        # 加载提示文本
        dots = "." * self.dots_count
        loading_text = self.font_manager.render_text(f"加载中{dots}", 'large', (150, 150, 150))
        loading_rect = loading_text.get_rect(center=(self.config.SCREEN_W // 2, 320))
        surface.blit(loading_text, loading_rect)
        
        # 绘制关卡提示
        self._draw_level_hints(surface)

    def _draw_level_hints(self, surface):
        """
        绘制关卡提示信息
        :param surface: 绘制表面
        """
        hints_y = 380
        
        # 根据关卡显示不同的提示
        hints = [
            f"关卡进度: {self.current_level}/{self.total_levels}",
            "准备迎接新的挑战！"
        ]
        
        # 根据关卡难度添加特定提示
        if self.current_level <= 3:
            hints.append("难度: 简单 - 熟悉操作")
        elif self.current_level <= 6:
            hints.append("难度: 中等 - 提升反应")
        else:
            hints.append("难度: 困难 - 考验技巧")
        
        for i, hint in enumerate(hints):
            hint_text = self.font_manager.render_text(hint, 'medium', (100, 150, 200))
            hint_rect = hint_text.get_rect(center=(self.config.SCREEN_W // 2, hints_y + i * 30))
            surface.blit(hint_text, hint_rect)

    def is_finished(self):
        """
        检查加载是否完成
        :return: bool
        """
        return self.finished

    def set_level(self, level, total_levels):
        """
        设置关卡信息
        :param level: 当前关卡
        :param total_levels: 总关卡数
        """
        self.current_level = level
        self.total_levels = total_levels
        self.progress = 0
        self.finished = False

    def handle_event(self, event):
        """
        处理事件 - 允许用户按任意键跳过加载界面
        :param event: pygame事件
        """
        if event.type == pygame.KEYDOWN:
            # 按任意键跳过加载
            self.progress = 100
            self.finished = True

    def reset(self):
        """重置加载界面"""
        self.progress = 0
        self.finished = False
        self.animation_time = 0
        self.dots_count = 0
        self.dot_timer = 0