"""
皮肤选择界面
"""
import pygame
from src.configs.config import Config
from src.utils.font_manager import get_font_manager


class SkinSelection:
    def __init__(self):
        """
        初始化皮肤选择状态
        """
        self.config = Config.get_instance()
        self.finished = False
        self.next = "main_menu"  # 选择皮肤后返回主菜单
        self.selected_skin = None  # 选中的皮肤

        # 获取字体管理器
        self.font_manager = get_font_manager()

        # 预设皮肤配置
        self.skin_options = self._load_skin_options()

        self.selected_option = 0  # 当前选中的选项
        self.back_option = len(self.skin_options)  # 返回选项的索引

        # 动画效果
        self.animation_time = 0
        self.pulse_speed = 2.0

    def _load_skin_options(self):
        """
        加载预设皮肤选项
        """
        return [
            {
                'name': '经典绿色',
                'key': 'classic_green',
                'description': '传统的绿色贪吃蛇',
                'head_color': (0, 255, 0),
                'body_color': (0, 200, 0),
                'border_color': (0, 150, 0),
                'highlight_color': (150, 255, 150)
            },
            {
                'name': '火焰红色',
                'key': 'fire_red',
                'description': '炽热的红色贪吃蛇',
                'head_color': (255, 0, 0),
                'body_color': (200, 0, 0),
                'border_color': (150, 0, 0),
                'highlight_color': (255, 150, 150)
            },
            {
                'name': '海洋蓝色',
                'key': 'ocean_blue',
                'description': '清新的蓝色贪吃蛇',
                'head_color': (0, 100, 255),
                'body_color': (0, 80, 200),
                'border_color': (0, 60, 150),
                'highlight_color': (150, 200, 255)
            },
            {
                'name': '黄金黄色',
                'key': 'golden_yellow',
                'description': '华丽的黄色贪吃蛇',
                'head_color': (255, 215, 0),
                'body_color': (218, 165, 32),
                'border_color': (184, 134, 11),
                'highlight_color': (255, 255, 224)
            },
            {
                'name': '神秘紫色',
                'key': 'mystic_purple',
                'description': '神秘的紫色贪吃蛇',
                'head_color': (128, 0, 128),
                'body_color': (102, 0, 102),
                'border_color': (75, 0, 130),
                'highlight_color': (216, 191, 216)
            },
            {
                'name': '冰雪白色',
                'key': 'ice_white',
                'description': '纯净的白色贪吃蛇',
                'head_color': (255, 255, 255),
                'body_color': (240, 240, 240),
                'border_color': (200, 200, 200),
                'highlight_color': (255, 255, 255)
            }
        ]

    def update_cursor(self, event_key):
        """
        处理菜单导航
        """
        total_options = len(self.skin_options) + 1  # 包括返回选项

        if event_key == pygame.K_UP or event_key == pygame.K_w:
            self.selected_option = (self.selected_option - 1) % total_options
        elif event_key == pygame.K_DOWN or event_key == pygame.K_s:
            self.selected_option = (self.selected_option + 1) % total_options
        elif event_key == pygame.K_RETURN or event_key == pygame.K_SPACE:
            if self.selected_option < len(self.skin_options):
                # 选择了某个皮肤
                self.selected_skin = self.skin_options[self.selected_option]
                self.finished = True
                print(f"选择了皮肤: {self.selected_skin['name']}")
            else:
                # 选择了返回
                self.finished = True
        elif event_key == pygame.K_ESCAPE:
            # ESC键返回
            self.finished = True

    def update(self, surface, keys):
        """
        更新皮肤选择界面
        """
        # 更新动画时间
        self.animation_time += 1 / 60

        self.draw(surface)

    def draw(self, surface):
        """
        绘制皮肤选择界面
        """
        # 渐变背景
        self._draw_gradient_background(surface)

        # 绘制标题
        title_text = self.font_manager.render_text("选择皮肤", 'title', (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.config.SCREEN_W // 2, 60))
        surface.blit(title_text, title_rect)

        # 绘制皮肤选项
        start_y = 120
        option_height = 80

        for i, skin in enumerate(self.skin_options):
            y_pos = start_y + i * option_height
            is_selected = (i == self.selected_option)

            self._draw_skin_option(surface, skin, y_pos, is_selected)

        # 绘制返回选项
        back_y = start_y + len(self.skin_options) * option_height + 20
        is_back_selected = (self.selected_option == self.back_option)
        self._draw_back_option(surface, back_y, is_back_selected)

        # 绘制控制提示
        self._draw_controls_help(surface)

    def _draw_gradient_background(self, surface):
        """绘制渐变背景"""
        for y in range(self.config.SCREEN_H):
            # 从深紫到黑色的渐变
            ratio = y / self.config.SCREEN_H
            color_value = int(40 * (1 - ratio))
            color = (color_value + 20, color_value, color_value + 40)
            pygame.draw.line(surface, color, (0, y), (self.config.SCREEN_W, y))

    def _draw_skin_option(self, surface, skin, y_pos, is_selected):
        """绘制单个皮肤选项"""
        # 计算选项区域
        option_width = 600
        option_height = 70
        option_x = (self.config.SCREEN_W - option_width) // 2
        option_rect = pygame.Rect(option_x, y_pos, option_width, option_height)

        # 选中效果
        if is_selected:
            # 脉动效果
            pulse = 1.0 + 0.1 * pygame.math.Vector2(1, 0).rotate(self.animation_time * self.pulse_speed * 360).x
            glow_color = tuple(int(c * 0.3) for c in skin['head_color'])

            # 绘制发光边框
            glow_rect = option_rect.inflate(10, 10)
            pygame.draw.rect(surface, glow_color, glow_rect, 3)

            # 背景高亮
            bg_color = tuple(int(c * 0.2) for c in skin['head_color'])
            pygame.draw.rect(surface, bg_color, option_rect)
        else:
            # 普通背景
            pygame.draw.rect(surface, (30, 30, 30), option_rect)

        # 边框
        border_color = skin['head_color'] if is_selected else (100, 100, 100)
        pygame.draw.rect(surface, border_color, option_rect, 2)

        # 皮肤名称
        name_color = skin['head_color'] if is_selected else (200, 200, 200)
        name_text = self.font_manager.render_text(skin['name'], 'large', name_color)
        name_rect = name_text.get_rect(left=option_x + 20, top=y_pos + 10)
        surface.blit(name_text, name_rect)

        # 描述
        desc_text = self.font_manager.render_text(skin['description'], 'medium', (180, 180, 180))
        desc_rect = desc_text.get_rect(left=option_x + 20, top=y_pos + 40)
        surface.blit(desc_text, desc_rect)

        # 绘制皮肤预览
        self._draw_skin_preview(surface, skin, option_x + 450, y_pos + 35)

    def _draw_skin_preview(self, surface, skin, x, y):
        """绘制皮肤预览"""
        # 绘制蛇头
        head_radius = 15
        pygame.draw.circle(surface, skin['head_color'], (x, y), head_radius)
        pygame.draw.circle(surface, skin['border_color'], (x, y), head_radius, 2)

        # 绘制蛇身段
        body_radius = 10
        for i in range(3):
            body_x = x - (i + 1) * 25
            pygame.draw.circle(surface, skin['body_color'], (body_x, y), body_radius)
            pygame.draw.circle(surface, skin['border_color'], (body_x, y), body_radius, 1)

    def _draw_back_option(self, surface, y_pos, is_selected):
        """绘制返回选项"""
        color = (255, 255, 100) if is_selected else (200, 200, 200)

        if is_selected:
            # 选中时的背景
            back_rect = pygame.Rect(self.config.SCREEN_W // 2 - 100, y_pos - 5, 200, 40)
            pygame.draw.rect(surface, (50, 50, 0), back_rect)
            pygame.draw.rect(surface, color, back_rect, 2)

        back_text = self.font_manager.render_text("← 返回主菜单", 'large', color)
        back_rect = back_text.get_rect(center=(self.config.SCREEN_W // 2, y_pos + 15))
        surface.blit(back_text, back_rect)

    def _draw_controls_help(self, surface):
        """绘制控制提示"""
        help_texts = [
            "↑↓ 选择皮肤    回车 确认    ESC 返回"
        ]

        for i, text in enumerate(help_texts):
            help_text = self.font_manager.render_text(text, 'help', (120, 120, 120))
            help_rect = help_text.get_rect(center=(self.config.SCREEN_W // 2,
                                                   self.config.SCREEN_H - 30 - i * 25))
            surface.blit(help_text, help_rect)

    def get_selected_skin(self):
        """获取选中的皮肤配置"""
        return self.selected_skin
