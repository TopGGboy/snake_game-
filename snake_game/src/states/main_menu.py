"""
简化的主菜单
"""
import pygame
from src.configs.config import Config
from src.utils.font_manager import get_font_manager


class MainMenu:
    def __init__(self):
        """
        初始化主菜单状态
        """
        self.config = Config.get_instance()
        self.finished = False
        self.next = "difficulty_selection"  # 先进入难度选择界面

        # 获取字体管理器
        self.font_manager = get_font_manager()

        # 菜单选项
        self.menu_options = ["无尽模式", "退出"]
        self.selected_option = 0  # 当前选中的选项

    def update_cursor(self, event_key):
        """
        处理菜单导航
        """
        if event_key == pygame.K_UP or event_key == pygame.K_w:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif event_key == pygame.K_DOWN or event_key == pygame.K_s:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif event_key == pygame.K_RETURN or event_key == pygame.K_SPACE:
            if self.selected_option == 0:  # 开始游戏
                self.finished = True
                self.config.MAIN_MENU_FLAG = False
            elif self.selected_option == 1:  # 退出
                pygame.quit()
                quit()

    def update(self, surface, keys):
        """
        更新主菜单界面
        """
        self.draw(surface)

    def draw(self, surface):
        """
        绘制主菜单
        """
        surface.fill((20, 20, 40))  # 深蓝色背景

        # 绘制标题
        title_text = self.font_manager.render_text("贪吃蛇游戏", 'title', (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.config.SCREEN_W // 2, 150))
        surface.blit(title_text, title_rect)

        # 绘制菜单选项
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 100) if i == self.selected_option else (200, 200, 200)
            option_text = self.font_manager.render_text(option, 'menu', color)
            option_rect = option_text.get_rect(center=(self.config.SCREEN_W // 2, 300 + i * 60))
            surface.blit(option_text, option_rect)

        # 绘制控制提示
        help_text = self.font_manager.render_text("使用方向键选择，回车确认", 'help', (150, 150, 150))
        help_rect = help_text.get_rect(center=(self.config.SCREEN_W // 2, 500))
        surface.blit(help_text, help_rect)
