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
        # 检查是否有按键按下
        if any(keys):
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
        level_rect = level_text.get_rect(center=(self.config.SCREEN_W // 2, 200))
        surface.blit(level_text, level_rect)
        
        # 绘制关卡进度信息
        progress_text = self.font_manager.render_text(f"{self.current_level}/{self.total_levels}", 'large', (200, 200, 200))
        progress_rect = progress_text.get_rect(center=(self.config.SCREEN_W // 2, 260))
        surface.blit(progress_text, progress_rect)
        
        # 绘制难度提示
        if self.current_level <= 3:
            difficulty_text = "难度: 简单"
            color = (100, 255, 100)
        elif self.current_level <= 6:
            difficulty_text = "难度: 中等"
            color = (255, 255, 100)
        else:
            difficulty_text = "难度: 困难"
            color = (255, 100, 100)
        
        difficulty_surface = self.font_manager.render_text(difficulty_text, 'medium', color)
        difficulty_rect = difficulty_surface.get_rect(center=(self.config.SCREEN_W // 2, 300))
        surface.blit(difficulty_surface, difficulty_rect)
        
        # 绘制按键提示
        key_text = self.font_manager.render_text("按任意键继续", 'large', (150, 200, 255))
        key_rect = key_text.get_rect(center=(self.config.SCREEN_W // 2, 360))
        surface.blit(key_text, key_rect)

    def _draw_level_hints(self, surface):
        """
        绘制关卡提示信息（简化版）
        :param surface: 绘制表面
        """
        # 简化为只显示一句鼓励语
        encouragement = "准备迎接挑战！"
        hint_text = self.font_manager.render_text(encouragement, 'medium', (150, 200, 255))
        hint_rect = hint_text.get_rect(center=(self.config.SCREEN_W // 2, 320))
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
        处理事件 - 允许用户按任意键继续
        :param event: pygame事件
        """
        if event.type == pygame.KEYDOWN:
            # 按任意键继续
            self.finished = True

    def reset(self):
        """重置加载界面"""
        self.progress = 0
        self.finished = False
        self.animation_time = 0
        self.dots_count = 0
        self.dot_timer = 0