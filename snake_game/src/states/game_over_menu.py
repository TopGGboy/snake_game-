"""
游戏结束界面
"""
import pygame
from src.configs.config import Config
from src.utils.font_manager import get_font_manager


class GameOverMenu:
    def __init__(self, game_state=None):
        """
        初始化游戏结束界面
        :param game_state: 当前游戏状态（用于显示统计信息）
        """
        self.config = Config.get_instance()
        self.font_manager = get_font_manager()
        
        # 游戏结束菜单选项
        self.menu_options = [
            "重新开始",
            "返回主菜单",
            "退出游戏"
        ]
        self.selected_option = 0  # 当前选中的选项
        
        # 游戏状态信息（用于显示统计）
        self.game_state = game_state
        
        # 游戏结束菜单的返回值
        self.action = None  # 'restart', 'main_menu', 'quit'
        self.finished = False
        
        # 界面动画效果
        self.fade_alpha = 0
        self.fade_speed = 6
        self.max_fade = 200
        
        # 按键防抖
        self.key_delay = 0
        self.key_delay_time = 150  # 毫秒
        
        # 动画效果
        self.pulse_time = 0
        self.pulse_speed = 2.0

    def handle_event(self, event):
        """
        处理事件
        :param event: pygame事件
        """
        if event.type == pygame.KEYDOWN:
            # 检查按键防抖
            current_time = pygame.time.get_ticks()
            if current_time - self.key_delay < self.key_delay_time:
                return
            
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                self.key_delay = current_time
                
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                self.key_delay = current_time
                
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._execute_selected_option()
                self.key_delay = current_time
                
            elif event.key == pygame.K_r:
                # R键快捷重新开始
                self.action = 'restart'
                self.finished = True
                self.key_delay = current_time

    def _execute_selected_option(self):
        """执行选中的菜单选项"""
        if self.selected_option == 0:  # 重新开始
            self.action = 'restart'
            self.finished = True
        elif self.selected_option == 1:  # 返回主菜单
            self.action = 'main_menu'
            self.finished = True
        elif self.selected_option == 2:  # 退出游戏
            self.action = 'quit'
            self.finished = True

    def update(self, surface, keys):
        """
        更新游戏结束界面
        :param surface: 绘制表面
        :param keys: 键盘按键状态
        """
        # 更新淡入效果
        if self.fade_alpha < self.max_fade:
            self.fade_alpha = min(self.max_fade, self.fade_alpha + self.fade_speed)
        
        # 更新脉动动画
        self.pulse_time += 0.016  # 假设60FPS
        
        # 绘制界面
        self.draw(surface)

    def draw(self, surface):
        """
        绘制游戏结束界面
        :param surface: 绘制表面
        """
        # 创建半透明覆盖层
        overlay = pygame.Surface((self.config.SCREEN_W, self.config.SCREEN_H))
        overlay.set_alpha(self.fade_alpha)
        overlay.fill((20, 0, 0))  # 深红色覆盖层
        surface.blit(overlay, (0, 0))
        
        # 绘制游戏结束标题（带脉动效果）
        pulse_scale = 1.0 + 0.1 * abs(pygame.math.Vector2(0, 1).rotate(self.pulse_time * self.pulse_speed * 180).y)
        title_color_intensity = int(200 + 55 * abs(pygame.math.Vector2(0, 1).rotate(self.pulse_time * self.pulse_speed * 180).y))
        title_color = (255, title_color_intensity, title_color_intensity)
        
        title_text = self.font_manager.render_text("游戏结束", 'title', title_color)
        # 简单的缩放效果（通过调整位置模拟）
        title_rect = title_text.get_rect(center=(self.config.SCREEN_W // 2, 100))
        surface.blit(title_text, title_rect)
        
        # 绘制游戏统计信息
        if self.game_state:
            self._draw_game_stats(surface)
        
        # 绘制菜单选项
        menu_start_y = 320
        for i, option in enumerate(self.menu_options):
            # 选中项高亮显示
            if i == self.selected_option:
                color = (255, 255, 100)  # 黄色高亮
                # 绘制选中背景
                option_bg = pygame.Surface((280, 45))
                option_bg.set_alpha(120)
                option_bg.fill((255, 100, 100))  # 红色背景
                bg_rect = option_bg.get_rect(center=(self.config.SCREEN_W // 2, menu_start_y + i * 55))
                surface.blit(option_bg, bg_rect)
            else:
                color = (220, 220, 220)  # 普通白色
            
            option_text = self.font_manager.render_text(option, 'menu', color)
            option_rect = option_text.get_rect(center=(self.config.SCREEN_W // 2, menu_start_y + i * 55))
            surface.blit(option_text, option_rect)
        
        # 绘制控制提示
        self._draw_controls_help(surface)

    def _draw_game_stats(self, surface):
        """
        绘制游戏统计信息
        :param surface: 绘制表面
        """
        stats_y = 180
        stats_color = (255, 200, 200)  # 淡红色
        
        # 最终得分（突出显示）
        if hasattr(self.game_state, 'score'):
            final_score_text = self.font_manager.render_text(f"最终得分: {self.game_state.score}", 'xlarge', (255, 255, 100))
            score_rect = final_score_text.get_rect(center=(self.config.SCREEN_W // 2, stats_y))
            surface.blit(final_score_text, score_rect)
        
        # 其他统计信息
        stats_y += 50
        if hasattr(self.game_state, 'high_score'):
            high_score_text = self.font_manager.render_text(f"历史最高: {self.game_state.high_score}", 'large', stats_color)
            high_score_rect = high_score_text.get_rect(center=(self.config.SCREEN_W // 2, stats_y))
            surface.blit(high_score_text, high_score_rect)
        
        stats_y += 35
        if hasattr(self.game_state, 'snake') and hasattr(self.game_state.snake, 'get_length'):
            length_text = self.font_manager.render_text(f"蛇身长度: {self.game_state.snake.get_length()}", 'medium', stats_color)
            length_rect = length_text.get_rect(center=(self.config.SCREEN_W // 2, stats_y))
            surface.blit(length_text, length_rect)
        
        stats_y += 30
        if hasattr(self.game_state, 'difficulty_config'):
            difficulty_name = self.game_state.difficulty_config.get('name', '未知')
            difficulty_text = self.font_manager.render_text(f"难度: {difficulty_name}", 'medium', stats_color)
            difficulty_rect = difficulty_text.get_rect(center=(self.config.SCREEN_W // 2, stats_y))
            surface.blit(difficulty_text, difficulty_rect)

    def _draw_controls_help(self, surface):
        """
        绘制控制提示
        :param surface: 绘制表面
        """
        help_y = 500
        help_color = (180, 180, 180)
        
        help_texts = [
            "↑↓ 或 W/S: 选择选项",
            "回车 或 空格: 确认选择",
            "R: 快速重新开始"
        ]
        
        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'help', help_color)
            help_rect = help_surface.get_rect(center=(self.config.SCREEN_W // 2, help_y + i * 25))
            surface.blit(help_surface, help_rect)

    def get_action(self):
        """
        获取用户选择的动作
        :return: 'restart', 'main_menu', 'quit' 或 None
        """
        return self.action

    def is_finished(self):
        """
        检查游戏结束菜单是否已完成
        :return: bool
        """
        return self.finished

    def reset(self):
        """重置游戏结束菜单状态"""
        self.action = None
        self.finished = False
        self.selected_option = 0
        self.fade_alpha = 0
        self.key_delay = 0
        self.pulse_time = 0