"""
关卡模式暂停界面
"""
import pygame
from src.configs.config import Config
from src.utils.font_manager import get_font_manager


class LevelPauseMenu:
    def __init__(self, screen_width=None, screen_height=None, game_state=None, current_level=1, total_levels=10,
                 is_victory=False, level_selection_callback=None):
        """
        初始化关卡暂停界面
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        :param game_state: 当前游戏状态
        :param current_level: 当前关卡
        :param total_levels: 总关卡数
        :param is_victory: 是否为胜利界面
        """
        self.config = Config.get_instance()
        self.font_manager = get_font_manager()

        # 设置屏幕尺寸
        self.screen_width = screen_width or self.config.SCREEN_W
        self.screen_height = screen_height or self.config.SCREEN_H

        # 关卡信息
        self.current_level = current_level
        self.total_levels = total_levels

        # 游戏状态
        self.game_state = game_state

        # 界面类型（暂停/胜利）
        self.is_victory = is_victory

        # 菜单选项
        self.menu_options = [
            "继续游戏",
            "重新开始本关",
            "上一关",
            "下一关",
            "选择关卡",
            "返回主菜单",
            "退出游戏"
        ]
        self.selected_option = 0

        # 界面状态
        self.action = None  # 'resume', 'restart', 'previous_level', 'next_level', 'level_select', 'main_menu', 'quit'
        self.finished = False
        
        # 关卡选择回调函数
        self.level_selection_callback = level_selection_callback

        # 动画效果
        self.fade_alpha = 0
        self.fade_speed = 8
        self.max_fade = 180

        # 按键防抖
        self.key_delay = 0
        self.key_delay_time = 150

    def handle_event(self, event):
        """
        处理事件
        :param event: pygame事件
        """
        if event.type == pygame.KEYDOWN:
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
                # ESC键继续游戏
                self.action = 'resume'
                self.finished = True
                self.key_delay = current_time

            elif event.key == pygame.K_p and self.current_level > 1:
                # P键快速上一关
                self.action = 'previous_level'
                self.finished = True
                self.key_delay = current_time

            elif event.key == pygame.K_n and self.current_level < self.total_levels:
                # N键快速下一关
                self.action = 'next_level'
                self.finished = True
                self.key_delay = current_time

    def _execute_selected_option(self):
        """执行选中的菜单选项"""
        option_text = self.menu_options[self.selected_option]

        if option_text == "继续游戏":
            self.action = 'resume'
            self.finished = True
        elif option_text == "重新开始本关":
            self.action = 'restart'
            self.finished = True
        elif option_text == "上一关":
            self.action = 'previous_level'
            self.finished = True
        elif option_text == "下一关":
            self.action = 'next_level'
            self.finished = True
        elif option_text == "选择关卡":
            # 设置动作为关卡选择，让游戏主循环处理状态切换
            self.action = 'level_selection'
            self.finished = True
        elif option_text == "返回主菜单":
            self.action = 'main_menu'
            self.finished = True
        elif option_text == "退出游戏":
            self.action = 'quit'
            self.finished = True

    def update(self, surface, keys):
        """
        更新界面
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
        绘制界面 - 采用分散布局避免重叠
        :param surface: 绘制表面
        """
        # 创建半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(self.fade_alpha)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # 分散布局：标题在左上角
        title = "游戏胜利" if self.is_victory else "游戏暂停"
        title_text = self.font_manager.render_text(title, 'large', (255, 255, 255))
        title_rect = title_text.get_rect(topleft=(50, 50))
        surface.blit(title_text, title_rect)

        # 关卡信息面板在右上角
        self._draw_level_info_panel(surface)

        # 游戏统计信息在右上角下方
        if self.game_state:
            self._draw_game_stats_panel(surface)

        # 菜单选项在左侧垂直布局
        self._draw_menu_options_panel(surface)

        # 控制提示在右下角
        self._draw_controls_help_panel(surface)

    def _draw_level_info_panel(self, surface):
        """绘制关卡信息面板 - 右上角"""
        panel_width = 250
        panel_height = 100
        panel_x = self.screen_width - panel_width - 50
        panel_y = 50

        # 绘制背景面板
        panel = pygame.Surface((panel_width, panel_height))
        panel.set_alpha(150)
        panel.fill((50, 50, 80))
        pygame.draw.rect(panel, (100, 100, 150), panel.get_rect(), 2)
        surface.blit(panel, (panel_x, panel_y))

        # 当前关卡
        level_text = f"第 {self.current_level} 关"
        level_surface = self.font_manager.render_text(level_text, 'large', (200, 200, 255))
        level_rect = level_surface.get_rect(topleft=(panel_x + 20, panel_y + 15))
        surface.blit(level_surface, level_rect)

        # 关卡进度
        progress_text = f"进度: {self.current_level}/{self.total_levels}"
        progress_surface = self.font_manager.render_text(progress_text, 'medium', (150, 150, 200))
        progress_rect = progress_surface.get_rect(topleft=(panel_x + 20, panel_y + 55))
        surface.blit(progress_surface, progress_rect)

    def _draw_game_stats_panel(self, surface):
        """绘制游戏统计信息面板 - 右上角下方"""
        panel_width = 250
        panel_height = 80
        panel_x = self.screen_width - panel_width - 50
        panel_y = 170

        # 绘制背景面板
        panel = pygame.Surface((panel_width, panel_height))
        panel.set_alpha(150)
        panel.fill((50, 80, 50))
        pygame.draw.rect(panel, (100, 150, 100), panel.get_rect(), 2)
        surface.blit(panel, (panel_x, panel_y))

        stats_y = panel_y + 15

        if hasattr(self.game_state, 'score'):
            score_text = f"得分: {self.game_state.score}"
            score_surface = self.font_manager.render_text(score_text, 'medium', (255, 255, 100))
            score_rect = score_surface.get_rect(topleft=(panel_x + 20, stats_y))
            surface.blit(score_surface, score_rect)

        if hasattr(self.game_state, 'snake') and hasattr(self.game_state.snake, 'get_length'):
            length_text = f"蛇长: {self.game_state.snake.get_length()}"
            length_surface = self.font_manager.render_text(length_text, 'medium', (180, 180, 180))
            length_rect = length_surface.get_rect(topleft=(panel_x + 20, stats_y + 35))
            surface.blit(length_surface, length_rect)

    def _draw_menu_options_panel(self, surface):
        """绘制菜单选项面板 - 左侧垂直布局"""
        panel_width = 300
        panel_height = 400
        panel_x = 50
        panel_y = 150

        # 绘制背景面板
        panel = pygame.Surface((panel_width, panel_height))
        panel.set_alpha(150)
        panel.fill((80, 50, 50))
        pygame.draw.rect(panel, (150, 100, 100), panel.get_rect(), 2)
        surface.blit(panel, (panel_x, panel_y))

        menu_start_y = panel_y + 20

        for i, option in enumerate(self.menu_options):
            # 检查选项是否可用
            is_available = True
            if option == "上一关" and self.current_level <= 1:
                is_available = False
            elif option == "下一关" and self.current_level >= self.total_levels:
                is_available = False

            # 统一行高和位置计算
            line_height = 45
            option_y = menu_start_y + i * line_height

            # 选中项高亮
            if i == self.selected_option:
                color = (255, 255, 100) if is_available else (150, 150, 150)
                # 绘制选中背景 - 与文本对齐
                option_bg = pygame.Surface((panel_width - 40, 35))
                option_bg.set_alpha(100)
                option_bg.fill((255, 255, 100))
                bg_rect = option_bg.get_rect(topleft=(panel_x + 20, option_y + 20))
                if is_available:
                    surface.blit(option_bg, bg_rect)
            else:
                color = (200, 200, 200) if is_available else (100, 100, 100)

            # 不可用选项添加特殊标记
            option_text = option
            if not is_available:
                option_text = f"{option} (不可用)"

            # 文本位置与选中框对齐
            option_surface = self.font_manager.render_text(option_text, 'menu', color)
            option_rect = option_surface.get_rect(topleft=(panel_x + 25, option_y + 10))
            surface.blit(option_surface, option_rect)

    def _draw_controls_help_panel(self, surface):
        """绘制控制提示面板 - 右下角"""
        panel_width = 300
        panel_height = 120
        panel_x = self.screen_width - panel_width - 50
        panel_y = self.screen_height - panel_height - 50

        # 绘制背景面板
        panel = pygame.Surface((panel_width, panel_height))
        panel.set_alpha(150)
        panel.fill((50, 50, 50))
        pygame.draw.rect(panel, (100, 100, 100), panel.get_rect(), 2)
        surface.blit(panel, (panel_x, panel_y))

        help_color = (180, 180, 180)
        help_texts = [
            "↑↓ 或 W/S: 选择选项",
            "回车 或 空格: 确认选择",
            "ESC: 直接继续游戏"
        ]

        # 添加快捷键提示
        if self.current_level > 1:
            help_texts.append("P: 快速上一关")
        if self.current_level < self.total_levels:
            help_texts.append("N: 快速下一关")

        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'help', help_color)
            help_rect = help_surface.get_rect(topleft=(panel_x + 20, panel_y + 15 + i * 20))
            surface.blit(help_surface, help_rect)

    def get_action(self):
        """获取用户选择的动作"""
        return self.action

    def is_finished(self):
        """检查界面是否完成"""
        return self.finished

    def set_level_info(self, current_level, total_levels):
        """设置关卡信息"""
        self.current_level = current_level
        self.total_levels = total_levels
        
    def set_level_selection_callback(self, callback):
        """设置关卡选择回调函数"""
        self.level_selection_callback = callback

    def set_victory_mode(self, is_victory=True):
        """设置是否为胜利模式"""
        self.is_victory = is_victory

    def reset(self):
        """重置界面状态"""
        self.action = None
        self.finished = False
        self.selected_option = 0
        self.fade_alpha = 0
        self.key_delay = 0
