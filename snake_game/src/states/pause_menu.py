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

        # 创建半透明覆盖层
        overlay = pygame.Surface((self.config.SCREEN_W, self.config.SCREEN_H))
        overlay.set_alpha(self.fade_alpha)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # 绘制暂停标题（左上角）
        title_text = self.font_manager.render_text("游戏暂停", 'large', (255, 255, 255))
        title_rect = title_text.get_rect(topleft=(50, 50))
        surface.blit(title_text, title_rect)

        # 绘制游戏统计信息（右上角）
        if self.game_state:
            self._draw_game_stats(surface, 50, 50)

        # 绘制菜单选项（左侧垂直布局）
        menu_start_x = 100
        menu_start_y = 150
        for i, option in enumerate(self.menu_options):
            option_y = menu_start_y + i * 80  # 增加间距到80像素
            
            # 选中项高亮显示
            if i == self.selected_option:
                color = (255, 220, 50)  # 金色高亮
                # 绘制选中背景（带圆角）
                option_bg = pygame.Surface((250, 50), pygame.SRCALPHA)
                pygame.draw.rect(option_bg, (255, 220, 50, 80), (0, 0, 250, 50), border_radius=8)
                bg_rect = option_bg.get_rect(topleft=(menu_start_x - 10, option_y - 5))
                surface.blit(option_bg, bg_rect)
                
                # 绘制选中指示器
                indicator_size = 8
                indicator_points = [
                    (menu_start_x - 20, option_y + 10),
                    (menu_start_x - 5, option_y + 2),
                    (menu_start_x - 5, option_y + 18)
                ]
                pygame.draw.polygon(surface, (255, 220, 50), indicator_points)
            else:
                color = (220, 220, 220)  # 普通白色

            option_text = self.font_manager.render_text(option, 'menu', color)
            option_rect = option_text.get_rect(topleft=(menu_start_x, option_y))
            surface.blit(option_text, option_rect)

        # 绘制控制提示（右下角）
        self._draw_controls_help(surface, self.config.SCREEN_W - 300, self.config.SCREEN_H - 120)

    def _draw_game_stats(self, surface, start_x, start_y):
        """
        绘制游戏统计信息
        :param surface: 绘制表面
        :param start_x: 起始X坐标
        :param start_y: 起始Y坐标
        """
        stats_color = (200, 200, 220)  # 更亮的统计信息颜色
        spacing = 35  # 增加行间距

        # 绘制统计信息背景面板
        stats_bg = pygame.Surface((250, 120), pygame.SRCALPHA)
        stats_bg.fill((30, 30, 40, 180))  # 半透明背景
        stats_bg_rect = stats_bg.get_rect(topright=(self.config.SCREEN_W - start_x, start_y))
        surface.blit(stats_bg, stats_bg_rect)

        # 绘制边框
        pygame.draw.rect(surface, (80, 80, 120), stats_bg_rect, 2, border_radius=5)

        # 获取游戏统计信息
        current_y = start_y + 20
        if hasattr(self.game_state, 'score'):
            score_text = self.font_manager.render_text(f"得分: {self.game_state.score}", 'medium', stats_color)
            score_rect = score_text.get_rect(topright=(self.config.SCREEN_W - start_x - 20, current_y))
            surface.blit(score_text, score_rect)
            current_y += spacing

        if hasattr(self.game_state, 'snake') and hasattr(self.game_state.snake, 'get_length'):
            length_text = self.font_manager.render_text(f"长度: {self.game_state.snake.get_length()}", 'medium', stats_color)
            length_rect = length_text.get_rect(topright=(self.config.SCREEN_W - start_x - 20, current_y))
            surface.blit(length_text, length_rect)
            current_y += spacing

        if hasattr(self.game_state, 'difficulty_config'):
            difficulty_name = self.game_state.difficulty_config.get('name', '未知')
            difficulty_text = self.font_manager.render_text(f"难度: {difficulty_name}", 'medium', stats_color)
            difficulty_rect = difficulty_text.get_rect(topright=(self.config.SCREEN_W - start_x - 20, current_y))
            surface.blit(difficulty_text, difficulty_rect)

    def _draw_controls_help(self, surface, start_x, start_y):
        """
        绘制控制提示
        :param surface: 绘制表面
        :param start_x: 起始X坐标
        :param start_y: 起始Y坐标
        """
        help_color = (180, 180, 200)  # 更亮的帮助文本颜色
        spacing = 25  # 增加行间距

        help_texts = [
            "↑↓ 或 W/S: 选择选项",
            "回车 或 空格: 确认选择",
            "ESC: 直接继续游戏"
        ]

        # 绘制帮助文本背景
        help_bg = pygame.Surface((280, len(help_texts) * spacing + 15), pygame.SRCALPHA)
        help_bg.fill((30, 30, 40, 150))  # 深色半透明背景
        help_bg_rect = help_bg.get_rect(bottomright=(start_x + 280, start_y + len(help_texts) * spacing))
        surface.blit(help_bg, help_bg_rect)

        # 绘制边框
        pygame.draw.rect(surface, (80, 80, 120), help_bg_rect, 2, border_radius=5)

        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'help', help_color)
            help_rect = help_surface.get_rect(bottomright=(start_x + 260, start_y + i * spacing))
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
