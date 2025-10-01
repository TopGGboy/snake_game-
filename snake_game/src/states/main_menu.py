"""
简化的主菜单
"""
import pygame
from src.configs.config import Config
from src.configs.skin_config import get_snake_colors
from src.configs.game_balance import GameBalance
from src.utils.font_manager import get_font_manager
from src.utils.image_manager import get_image_manager


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

        # 获取图片管理器
        self.image_manager = get_image_manager()

        # 菜单选项
        self.menu_options = ["无尽模式", "选择皮肤", "退出"]
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
            elif self.selected_option == 1:  # 选择皮肤
                self.finished = True
                self.next = "skin_selection"
            elif self.selected_option == 2:  # 退出
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

        # 绘制当前蛇形象预览
        self._draw_snake_preview(surface)

        # 调试信息：显示当前皮肤ID
        debug_text = self.font_manager.render_text(f"调试: 皮肤ID={self.config.get_skin_id()}", 'small',
                                                   (255, 100, 100))
        debug_rect = debug_text.get_rect(center=(self.config.SCREEN_W // 2, 550))
        surface.blit(debug_text, debug_rect)

        # 绘制控制提示
        help_text = self.font_manager.render_text("使用方向键选择，回车确认", 'help', (150, 150, 150))
        help_rect = help_text.get_rect(center=(self.config.SCREEN_W // 2, 500))
        surface.blit(help_text, help_rect)

    def _draw_snake_preview(self, surface):
        """绘制当前选中的蛇形象预览（使用真实图片）"""
        # 获取当前皮肤ID
        current_skin_id = self.config.get_skin_id()

        # 预览区域位置和大小
        preview_x = self.config.SCREEN_W - 200
        preview_y = 200
        preview_width = 180
        preview_height = 120

        # 绘制预览背景
        pygame.draw.rect(surface, (40, 40, 60), (preview_x, preview_y, preview_width, preview_height), border_radius=10)
        pygame.draw.rect(surface, (80, 80, 100), (preview_x, preview_y, preview_width, preview_height), 2,
                         border_radius=10)

        # 绘制标题
        preview_title = self.font_manager.render_text("当前蛇形象", 'small', (200, 200, 200))
        title_rect = preview_title.get_rect(center=(preview_x + preview_width // 2, preview_y + 20))
        surface.blit(preview_title, title_rect)

        # 使用图片管理器获取蛇形象贴图
        head_image = self.image_manager.get_snake_image(current_skin_id, "head")
        body_image = self.image_manager.get_snake_image(current_skin_id, "body0")

        # 预览中心位置
        preview_center_x = preview_x + preview_width // 2
        preview_center_y = preview_y + 70

        # 缩放蛇头图片为合适大小并水平翻转（让蛇头朝向右边）
        head_size = (GameBalance.SNAKE_HEAD_SIZE, GameBalance.SNAKE_HEAD_SIZE)
        scaled_head = pygame.transform.scale(head_image, head_size)
        flipped_head = pygame.transform.flip(scaled_head, True, False)

        # 绘制蛇头（蛇头一定存在）
        head_rect = flipped_head.get_rect(center=(preview_center_x, preview_center_y))
        surface.blit(flipped_head, head_rect)

        # 如果有蛇身图片，则使用蛇身图片
        if body_image:
            # 缩放蛇身图片为合适大小
            body_size = (GameBalance.SNAKE_BODY_SIZE, GameBalance.SNAKE_BODY_SIZE)
            scaled_body = pygame.transform.scale(body_image, body_size)

            # 绘制蛇身段（2个身体段）
            for i in range(2):
                body_x = preview_center_x - (i + 1) * (GameBalance.SNAKE_BODY_SIZE + 5)
                body_rect = scaled_body.get_rect(center=(body_x, preview_center_y))
                surface.blit(scaled_body, body_rect)
        else:
            # 没有蛇身图片时使用默认圆点绘制蛇身
            colors = get_snake_colors(current_skin_id, is_boosting=False)
            body_radius = GameBalance.SNAKE_BODY_SIZE // 2
            for i in range(3):
                body_x = preview_center_x - (i + 1) * (GameBalance.SNAKE_BODY_SIZE)
                body_color = colors['body_fill']
                pygame.draw.circle(surface, body_color, (body_x, preview_center_y), body_radius)
                pygame.draw.circle(surface, colors['body_border'], (body_x, preview_center_y), body_radius, 1)

        # 绘制皮肤ID信息
        skin_info = self.font_manager.render_text(f"皮肤 {current_skin_id}", 'small', (200, 200, 200))
        info_rect = skin_info.get_rect(center=(preview_center_x, preview_y + preview_height - 20))
        surface.blit(skin_info, info_rect)
