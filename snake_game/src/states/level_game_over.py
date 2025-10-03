"""
关卡模式游戏结束界面
"""
import pygame
from src.configs.config import Config
from src.utils.font_manager import get_font_manager


class LevelGameOverMenu:
    def __init__(self, game_state=None, current_level=1, total_levels=10, level_completed=False):
        """
        初始化关卡游戏结束界面
        :param game_state: 当前游戏状态
        :param current_level: 当前关卡
        :param total_levels: 总关卡数
        :param level_completed: 是否完成关卡
        """
        self.config = Config.get_instance()
        self.font_manager = get_font_manager()
        
        # 关卡信息
        self.current_level = current_level
        self.total_levels = total_levels
        self.level_completed = level_completed
        
        # 游戏状态信息
        self.game_state = game_state
        
        # 菜单选项（根据是否完成关卡显示不同选项）
        if level_completed:
            self.menu_options = [
                "下一关",
                "重新开始本关",
                "选择关卡",
                "返回主菜单",
                "退出游戏"
            ]
        else:
            self.menu_options = [
                "重新开始本关",
                "上一关",
                "下一关",
                "选择关卡",
                "返回主菜单",
                "退出游戏"
            ]
        
        self.selected_option = 0
        
        # 界面状态
        self.action = None  # 'next_level', 'previous_level', 'restart', 'level_select', 'main_menu', 'quit'
        self.finished = False
        
        # 动画效果
        self.fade_alpha = 0
        self.fade_speed = 6
        self.max_fade = 200
        
        # 按键防抖
        self.key_delay = 0
        self.key_delay_time = 150
        
        # 脉动动画
        self.pulse_time = 0
        self.pulse_speed = 2.0

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
                
            elif event.key == pygame.K_r:
                # R键快速重新开始
                self.action = 'restart'
                self.finished = True
                self.key_delay = current_time
                
            elif event.key == pygame.K_n and self.current_level < self.total_levels:
                # N键快速下一关
                self.action = 'next_level'
                self.finished = True
                self.key_delay = current_time
                
            elif event.key == pygame.K_p and self.current_level > 1:
                # P键快速上一关
                self.action = 'previous_level'
                self.finished = True
                self.key_delay = current_time

    def _execute_selected_option(self):
        """执行选中的菜单选项"""
        option_text = self.menu_options[self.selected_option]
        
        if option_text == "下一关":
            self.action = 'next_level'
            self.finished = True
        elif option_text == "上一关":
            self.action = 'previous_level'
            self.finished = True
        elif option_text == "重新开始本关":
            self.action = 'restart'
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
        
        # 更新脉动动画
        self.pulse_time += 0.016
        
        # 绘制界面
        self.draw(surface)

    def draw(self, surface):
        """
        绘制界面
        :param surface: 绘制表面
        """
        # 创建半透明覆盖层
        overlay = pygame.Surface((self.config.SCREEN_W, self.config.SCREEN_H))
        overlay.set_alpha(self.fade_alpha)
        
        if self.level_completed:
            overlay.fill((0, 20, 0))  # 深绿色（通关）
        else:
            overlay.fill((20, 0, 0))  # 深红色（失败）
            
        surface.blit(overlay, (0, 0))
        
        # 绘制标题
        if self.level_completed:
            title_color = (100, 255, 100)
            title_text = "关卡完成！"
        else:
            title_color = (255, 100, 100)
            title_text = "游戏结束"
            
        # 脉动效果
        pulse_intensity = 0.1 * abs(pygame.math.Vector2(0, 1).rotate(self.pulse_time * self.pulse_speed * 180).y)
        title_color = (
            min(255, int(title_color[0] * (1 + pulse_intensity))),
            min(255, int(title_color[1] * (1 + pulse_intensity))),
            min(255, int(title_color[2] * (1 + pulse_intensity)))
        )
        
        title_surface = self.font_manager.render_text(title_text, 'title', title_color)
        title_rect = title_surface.get_rect(center=(self.config.SCREEN_W // 2, 100))
        surface.blit(title_surface, title_rect)
        
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
        level_y = 160
        
        # 关卡进度
        level_text = f"第 {self.current_level} 关 ({self.current_level}/{self.total_levels})"
        level_surface = self.font_manager.render_text(level_text, 'large', (200, 200, 200))
        level_rect = level_surface.get_rect(center=(self.config.SCREEN_W // 2, level_y))
        surface.blit(level_surface, level_rect)
        
        # 状态提示
        status_y = level_y + 40
        if self.level_completed:
            status_text = "恭喜你成功通关！"
            status_color = (100, 255, 100)
        else:
            status_text = "再接再厉！"
            status_color = (255, 200, 100)
            
        status_surface = self.font_manager.render_text(status_text, 'medium', status_color)
        status_rect = status_surface.get_rect(center=(self.config.SCREEN_W // 2, status_y))
        surface.blit(status_surface, status_rect)

    def _draw_game_stats(self, surface):
        """绘制游戏统计信息"""
        stats_y = 220
        stats_color = (200, 200, 200)
        
        if hasattr(self.game_state, 'score'):
            score_text = f"得分: {self.game_state.score}"
            score_surface = self.font_manager.render_text(score_text, 'large', (255, 255, 100))
            score_rect = score_surface.get_rect(center=(self.config.SCREEN_W // 2, stats_y))
            surface.blit(score_surface, score_rect)
        
        if hasattr(self.game_state, 'snake') and hasattr(self.game_state.snake, 'get_length'):
            length_text = f"蛇身长度: {self.game_state.snake.get_length()}"
            length_surface = self.font_manager.render_text(length_text, 'medium', stats_color)
            length_rect = length_surface.get_rect(center=(self.config.SCREEN_W // 2, stats_y + 35))
            surface.blit(length_surface, length_rect)

    def _draw_menu_options(self, surface):
        """绘制菜单选项"""
        menu_start_y = 300
        
        for i, option in enumerate(self.menu_options):
            # 检查选项是否可用
            is_available = True
            if option == "下一关" and self.current_level >= self.total_levels:
                is_available = False
            elif option == "上一关" and self.current_level <= 1:
                is_available = False
            
            # 选中项高亮
            if i == self.selected_option:
                color = (255, 255, 100) if is_available else (150, 150, 150)
                # 绘制选中背景
                option_bg = pygame.Surface((300, 45))
                option_bg.set_alpha(100)
                if self.level_completed:
                    option_bg.fill((100, 255, 100))
                else:
                    option_bg.fill((255, 100, 100))
                bg_rect = option_bg.get_rect(center=(self.config.SCREEN_W // 2, menu_start_y + i * 50))
                if is_available:
                    surface.blit(option_bg, bg_rect)
            else:
                color = (200, 200, 200) if is_available else (100, 100, 100)
            
            # 不可用选项添加特殊标记
            option_text = option
            if not is_available:
                option_text = f"{option} (不可用)"
            
            option_surface = self.font_manager.render_text(option_text, 'menu', color)
            option_rect = option_surface.get_rect(center=(self.config.SCREEN_W // 2, menu_start_y + i * 50))
            surface.blit(option_surface, option_rect)

    def _draw_controls_help(self, surface):
        """绘制控制提示"""
        help_y = 550
        help_color = (150, 150, 150)
        
        help_texts = [
            "↑↓ 或 W/S: 选择选项",
            "回车 或 空格: 确认选择",
            "R: 快速重新开始"
        ]
        
        # 添加快捷键提示
        if self.current_level < self.total_levels:
            help_texts.append("N: 快速下一关")
        if self.current_level > 1:
            help_texts.append("P: 快速上一关")
        
        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'help', help_color)
            help_rect = help_surface.get_rect(center=(self.config.SCREEN_W // 2, help_y + i * 25))
            surface.blit(help_surface, help_rect)

    def get_action(self):
        """获取用户选择的动作"""
        return self.action

    def is_finished(self):
        """检查界面是否完成"""
        return self.finished

    def set_level_info(self, current_level, total_levels, level_completed):
        """设置关卡信息"""
        self.current_level = current_level
        self.total_levels = total_levels
        self.level_completed = level_completed
        
        # 重新设置菜单选项
        if level_completed:
            self.menu_options = [
                "下一关",
                "重新开始本关",
                "选择关卡",
                "返回主菜单",
                "退出游戏"
            ]
        else:
            self.menu_options = [
                "重新开始本关",
                "上一关",
                "下一关",
                "选择关卡",
                "返回主菜单",
                "退出游戏"
            ]
        
        # 重置选择
        self.selected_option = 0

    def reset(self):
        """重置界面状态"""
        self.action = None
        self.finished = False
        self.selected_option = 0
        self.fade_alpha = 0
        self.key_delay = 0
        self.pulse_time = 0