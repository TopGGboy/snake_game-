"""
难度选择界面
"""
import pygame
from src.configs.config import Config
from src.configs.game_balance import GameBalance
from src.utils.font_manager import get_font_manager


class DifficultySelection:
    def __init__(self):
        """
        初始化难度选择状态
        """
        self.config = Config.get_instance()
        self.finished = False  # 是否完成
        self.next = "infinite_mode"  # 选择难度后进入无尽模式
        self.selected_difficulty = None  # 选中的难度

        # 获取字体管理器
        self.font_manager = get_font_manager()

        # 难度选项配置
        self.difficulty_options = [
            {
                'name': '娱乐模式',
                'key': 'entertainment',
                'description': '轻松愉快，适合休闲',
                'features': [
                    '• 移动速度较慢',
                    '• 无边界墙壁',
                    '• 食物分数: 5分',
                    '• 适合新手练习'
                ],
                'color': (100, 255, 100),  # 绿色
                'speed': 80.0,
                'walls': False,
                'food_score': 5
            },
            {
                'name': '困难模式',
                'key': 'hard',
                'description': '挑战你的反应速度',
                'features': [
                    '• 移动速度适中',
                    '• 有边界墙壁',
                    '• 食物分数: 10分',
                    '• 经典贪吃蛇体验'
                ],
                'color': (255, 255, 100),  # 黄色
                'speed': 120.0,
                'walls': True,
                'food_score': 10
            },
            {
                'name': '噩梦模式',
                'key': 'nightmare',
                'description': '极限挑战，勇者专属',
                'features': [
                    '• 移动速度很快',
                    '• 复杂迷宫障碍',
                    '• 食物分数: 20分',
                    '• 终极挑战体验'
                ],
                'color': (255, 100, 100),  # 红色
                'speed': 180.0,
                'walls': True,
                'maze': True,
                'food_score': 20
            }
        ]

        self.selected_option = 0  # 当前选中的选项
        self.back_option = len(self.difficulty_options)  # 返回选项的索引

        # 动画效果
        self.animation_time = 0
        self.pulse_speed = 2.0

    def update_cursor(self, event_key):
        """
        处理菜单导航
        """
        total_options = len(self.difficulty_options) + 1  # 包括返回选项

        if event_key == pygame.K_UP or event_key == pygame.K_w:
            self.selected_option = (self.selected_option - 1) % total_options
        elif event_key == pygame.K_DOWN or event_key == pygame.K_s:
            self.selected_option = (self.selected_option + 1) % total_options
        elif event_key == pygame.K_RETURN or event_key == pygame.K_SPACE:
            if self.selected_option < len(self.difficulty_options):
                # 选择了某个难度
                self.selected_difficulty = self.difficulty_options[self.selected_option]  # 选中的难度
                self.finished = True
                self.config.MAIN_MENU_FLAG = False  # 设置主菜单标志为False
                print(f"选择了难度: {self.selected_difficulty['name']}")
            else:
                # 选择了返回
                self.finished = True
                self.next = "main_menu"  # 设置下一个状态为"main_menu"
        elif event_key == pygame.K_ESCAPE:
            # ESC键返回主菜单
            self.finished = True
            self.next = "main_menu"

    def update(self, surface, keys):
        """
        更新难度选择界面
        """
        # 更新动画时间
        self.animation_time += 1 / 60

        self.draw(surface)

    def draw(self, surface):
        """
        绘制难度选择界面
        """
        # 渐变背景
        self._draw_gradient_background(surface)

        # 绘制标题
        title_text = self.font_manager.render_text("选择难度", 'title', (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.config.SCREEN_W // 2, 80))
        surface.blit(title_text, title_rect)

        # 绘制难度选项
        start_y = 150
        option_height = 140

        for i, option in enumerate(self.difficulty_options):
            y_pos = start_y + i * option_height
            is_selected = (i == self.selected_option)

            self._draw_difficulty_option(surface, option, y_pos, is_selected)

        # 绘制返回选项
        back_y = start_y + len(self.difficulty_options) * option_height + 20
        is_back_selected = (self.selected_option == self.back_option)
        self._draw_back_option(surface, back_y, is_back_selected)

        # 绘制控制提示
        self._draw_controls_help(surface)

    def _draw_gradient_background(self, surface):
        """绘制渐变背景"""
        for y in range(self.config.SCREEN_H):
            # 从深蓝到黑色的渐变
            ratio = y / self.config.SCREEN_H
            color_value = int(40 * (1 - ratio))
            color = (color_value, color_value, color_value + 20)
            pygame.draw.line(surface, color, (0, y), (self.config.SCREEN_W, y))

    def _draw_difficulty_option(self, surface, option, y_pos, is_selected):
        """绘制单个难度选项"""
        # 计算选项区域
        option_width = 700
        option_height = 120
        option_x = (self.config.SCREEN_W - option_width) // 2
        option_rect = pygame.Rect(option_x, y_pos, option_width, option_height)

        # 选中效果
        if is_selected:
            # 脉动效果
            pulse = 1.0 + 0.1 * pygame.math.Vector2(1, 0).rotate(self.animation_time * self.pulse_speed * 360).x
            glow_color = tuple(int(c * 0.3) for c in option['color'])

            # 绘制发光边框
            glow_rect = option_rect.inflate(10, 10)
            pygame.draw.rect(surface, glow_color, glow_rect, 3)

            # 背景高亮
            bg_color = tuple(int(c * 0.2) for c in option['color'])
            pygame.draw.rect(surface, bg_color, option_rect)
        else:
            # 普通背景
            pygame.draw.rect(surface, (30, 30, 30), option_rect)

        # 边框
        border_color = option['color'] if is_selected else (100, 100, 100)
        pygame.draw.rect(surface, border_color, option_rect, 2)

        # 难度名称
        name_color = option['color'] if is_selected else (200, 200, 200)
        name_text = self.font_manager.render_text(option['name'], 'large', name_color)
        name_rect = name_text.get_rect(left=option_x + 20, top=y_pos + 10)
        surface.blit(name_text, name_rect)

        # 描述
        desc_text = self.font_manager.render_text(option['description'], 'medium', (180, 180, 180))
        desc_rect = desc_text.get_rect(left=option_x + 20, top=y_pos + 45)
        surface.blit(desc_text, desc_rect)

        # 特性列表
        features_x = option_x + 350
        for j, feature in enumerate(option['features']):
            feature_color = (150, 150, 150) if not is_selected else (200, 200, 200)
            feature_text = self.font_manager.render_text(feature, 'small', feature_color)
            feature_rect = feature_text.get_rect(left=features_x, top=y_pos + 15 + j * 20)
            surface.blit(feature_text, feature_rect)

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
            "↑↓ 选择难度    回车 确认    ESC 返回"
        ]

        for i, text in enumerate(help_texts):
            help_text = self.font_manager.render_text(text, 'help', (120, 120, 120))
            help_rect = help_text.get_rect(center=(self.config.SCREEN_W // 2,
                                                   self.config.SCREEN_H - 30 - i * 25))
            surface.blit(help_text, help_rect)

    def get_selected_difficulty(self):
        """获取选中的难度配置"""
        return self.selected_difficulty
