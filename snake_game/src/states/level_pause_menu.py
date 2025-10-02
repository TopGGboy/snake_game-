"""
关卡模式暂停界面
"""
import pygame
from src.configs.config import Config
from src.utils.font_manager import get_font_manager


class LevelPauseMenu:
    def __init__(self, screen_width=None, screen_height=None, game_state=None, current_level=1, total_levels=10, is_victory=False):
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
        self.action = None  # 'resume', 'restart', 'prev_level', 'next_level', 'level_select', 'main_menu', 'quit'
        self.finished = False
        
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
                self.action = 'prev_level'
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
            self.action = 'prev_level'
            self.finished = True
        elif option_text == "下一关":
            self.action = 'next_level'
            self.finished = True
        elif option_text == "选择关卡":
            self.action = 'level_select'
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
        绘制界面
        :param surface: 绘制表面
        """
        # 创建半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(self.fade_alpha)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # 绘制标题
        title = "游戏胜利" if self.is_victory else "游戏暂停"
        title_text = self.font_manager.render_text(title, 'title', (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(title_text, title_rect)
        
        # 绘制关卡信息
        self._draw_level_info(surface)
        
        # 绘制游戏统计
        if self.game_state:
            self._draw_game_stats(surface)
        
        # 绘制菜单选项
        self._draw_menu_options(surface)
        
        # 绘制控制提示
        self._draw_controls_help(surface)

    def _draw_level_info(self, surface):
        """绘制关卡信息"""
        level_y = 150
        
        # 当前关卡
        level_text = f"第 {self.current_level} 关"
        level_surface = self.font_manager.render_text(level_text, 'large', (200, 200, 255))
        level_rect = level_surface.get_rect(center=(self.screen_width // 2, level_y))
        surface.blit(level_surface, level_rect)
        
        # 关卡进度
        progress_y = level_y + 35
        progress_text = f"进度: {self.current_level}/{self.total_levels}"
        progress_surface = self.font_manager.render_text(progress_text, 'medium', (150, 150, 200))
        progress_rect = progress_surface.get_rect(center=(self.screen_width // 2, progress_y))
        surface.blit(progress_surface, progress_rect)

    def _draw_game_stats(self, surface):
        """绘制游戏统计信息"""
        stats_y = 200
        stats_color = (180, 180, 180)
        
        if hasattr(self.game_state, 'score'):
            score_text = f"当前得分: {self.game_state.score}"
            score_surface = self.font_manager.render_text(score_text, 'large', (255, 255, 100))
            score_rect = score_surface.get_rect(center=(self.screen_width // 2, stats_y))
            surface.blit(score_surface, score_rect)
        
        if hasattr(self.game_state, 'snake') and hasattr(self.game_state.snake, 'get_length'):
            length_text = f"蛇身长度: {self.game_state.snake.get_length()}"
            length_surface = self.font_manager.render_text(length_text, 'medium', stats_color)
            length_rect = length_surface.get_rect(center=(self.screen_width // 2, stats_y + 35))
            surface.blit(length_surface, length_rect)

    def _draw_menu_options(self, surface):
        """绘制菜单选项"""
        menu_start_y = 280
        
        for i, option in enumerate(self.menu_options):
            # 检查选项是否可用
            is_available = True
            if option == "上一关" and self.current_level <= 1:
                is_available = False
            elif option == "下一关" and self.current_level >= self.total_levels:
                is_available = False
            
            # 选中项高亮
            if i == self.selected_option:
                color = (255, 255, 100) if is_available else (150, 150, 150)
                # 绘制选中背景
                option_bg = pygame.Surface((300, 45))
                option_bg.set_alpha(100)
                option_bg.fill((255, 255, 100))
                bg_rect = option_bg.get_rect(center=(self.screen_width // 2, menu_start_y + i * 50))
                if is_available:
                    surface.blit(option_bg, bg_rect)
            else:
                color = (200, 200, 200) if is_available else (100, 100, 100)
            
            # 不可用选项添加特殊标记
            option_text = option
            if not is_available:
                option_text = f"{option} (不可用)"
            
            option_surface = self.font_manager.render_text(option_text, 'menu', color)
            option_rect = option_surface.get_rect(center=(self.screen_width // 2, menu_start_y + i * 50))
            surface.blit(option_surface, option_rect)

    def _draw_controls_help(self, surface):
        """绘制控制提示"""
        help_y = 620
        help_color = (150, 150, 150)
        
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
            help_rect = help_surface.get_rect(center=(self.screen_width // 2, help_y + i * 25))
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