"""
暂停界面
"""
import pygame
from src.configs.config import Config
from src.utils.font_manager import get_font_manager


class PauseMenu:
    def __init__(self, game_state=None):
        """
        初始化暂停界面
        :param game_state: 当前游戏状态（用于显示统计信息）
        """
        self.config = Config.get_instance()
        self.font_manager = get_font_manager()

        # 暂停菜单选项
        self.menu_options = [
            "继续游戏",
            "重新开始",
            "返回主菜单",
            "退出游戏"
        ]
        self.selected_option = 0  # 当前选中的选项

        # 游戏状态信息（用于显示统计）
        self.game_state = game_state

        # 暂停菜单的返回值
        self.action = None  # 'resume', 'restart', 'main_menu', 'quit'
        self.finished = False

        # 界面动画效果
        self.fade_alpha = 0
        self.fade_speed = 8
        self.max_fade = 180

        # 按键防抖
        self.key_delay = 0
        self.key_delay_time = 150  # 毫秒

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

            elif event.key == pygame.K_ESCAPE:
                # ESC键直接继续游戏
                self.action = 'resume'
                self.finished = True
                self.key_delay = current_time

    def _execute_selected_option(self):
        """执行选中的菜单选项"""
        if self.selected_option == 0:  # 继续游戏
            self.action = 'resume'
            self.finished = True
        elif self.selected_option == 1:  # 重新开始
            self.action = 'restart'
            self.finished = True
        elif self.selected_option == 2:  # 返回主菜单
            self.action = 'main_menu'
            self.finished = True
        elif self.selected_option == 3:  # 退出游戏
            self.action = 'quit'
            self.finished = True

    def update(self, surface, keys):
        """
        更新暂停界面
        :param surface: 绘制表面
        :param keys: 键盘按键状态
        """
        # 更新淡入效果
        if self.fade_alpha < self.max_fade:
            self.fade_alpha = min(self.max_fade, self.fade_alpha + self.fade_speed)

        # 绘制界面
        self.draw(surface)

    def draw(self, surface):
        """
        绘制暂停界面
        :param surface: 绘制表面
        """
        # 创建半透明覆盖层
        overlay = pygame.Surface((self.config.SCREEN_W, self.config.SCREEN_H))
        overlay.set_alpha(self.fade_alpha)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # 绘制暂停标题
        title_text = self.font_manager.render_text("游戏暂停", 'title', (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.config.SCREEN_W // 2, 120))
        surface.blit(title_text, title_rect)

        # 绘制游戏统计信息（如果有游戏状态）
        if self.game_state:
            self._draw_game_stats(surface)

        # 绘制菜单选项
        menu_start_y = 280
        for i, option in enumerate(self.menu_options):
            # 选中项高亮显示
            if i == self.selected_option:
                color = (255, 255, 100)  # 黄色高亮
                # 绘制选中背景
                option_bg = pygame.Surface((300, 50))
                option_bg.set_alpha(100)
                option_bg.fill((255, 255, 100))
                bg_rect = option_bg.get_rect(center=(self.config.SCREEN_W // 2, menu_start_y + i * 60))
                surface.blit(option_bg, bg_rect)
            else:
                color = (200, 200, 200)  # 普通白色

            option_text = self.font_manager.render_text(option, 'menu', color)
            option_rect = option_text.get_rect(center=(self.config.SCREEN_W // 2, menu_start_y + i * 60))
            surface.blit(option_text, option_rect)

        # 绘制控制提示
        self._draw_controls_help(surface)

    def _draw_game_stats(self, surface):
        """
        绘制游戏统计信息
        :param surface: 绘制表面
        """
        stats_y = 180
        stats_color = (180, 180, 180)

        # 获取游戏统计信息
        if hasattr(self.game_state, 'score'):
            score_text = self.font_manager.render_text(f"当前得分: {self.game_state.score}", 'large', stats_color)
            score_rect = score_text.get_rect(center=(self.config.SCREEN_W // 2, stats_y))
            surface.blit(score_text, score_rect)

        if hasattr(self.game_state, 'snake') and hasattr(self.game_state.snake, 'get_length'):
            length_text = self.font_manager.render_text(f"蛇身长度: {self.game_state.snake.get_length()}", 'medium',
                                                        stats_color)
            length_rect = length_text.get_rect(center=(self.config.SCREEN_W // 2, stats_y + 35))
            surface.blit(length_text, length_rect)

        if hasattr(self.game_state, 'difficulty_config'):
            difficulty_name = self.game_state.difficulty_config.get('name', '未知')
            difficulty_text = self.font_manager.render_text(f"难度: {difficulty_name}", 'medium', stats_color)
            difficulty_rect = difficulty_text.get_rect(center=(self.config.SCREEN_W // 2, stats_y + 65))
            surface.blit(difficulty_text, difficulty_rect)

    def _draw_controls_help(self, surface):
        """
        绘制控制提示
        :param surface: 绘制表面
        """
        help_y = 520
        help_color = (150, 150, 150)

        help_texts = [
            "↑↓ 或 W/S: 选择选项",
            "回车 或 空格: 确认选择",
            "ESC: 直接继续游戏"
        ]

        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'help', help_color)
            help_rect = help_surface.get_rect(center=(self.config.SCREEN_W // 2, help_y + i * 25))
            surface.blit(help_surface, help_rect)

    def get_action(self):
        """
        获取用户选择的动作
        :return: 'resume', 'restart', 'main_menu', 'quit' 或 None
        """
        return self.action

    def is_finished(self):
        """
        检查暂停菜单是否已完成
        :return: bool
        """
        return self.finished

    def reset(self):
        """重置暂停菜单状态"""
        self.action = None
        self.finished = False
        self.selected_option = 0
        self.fade_alpha = 0
        self.key_delay = 0
