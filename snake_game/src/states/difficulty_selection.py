"""
难度选择界面
"""
import pygame
from ..configs.config import Config
from ..configs.game_balance import GameBalance
from ..configs.difficulty_loader import get_difficulty_loader
from ..utils.font_manager import get_font_manager


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
        
        # 获取难度配置加载器
        self.difficulty_loader = get_difficulty_loader()

        # 从JSON文件加载难度选项配置
        self.difficulty_options = self._load_difficulty_options()

        self.selected_option = 0  # 当前选中的选项
        self.back_option = len(self.difficulty_options)  # 返回选项的索引

        # 动画效果
        self.animation_time = 0
        self.pulse_speed = 2.0

    def _load_difficulty_options(self):
        """
        从JSON配置文件加载难度选项
        """
        options = []
        
        # 定义难度映射和显示配置
        difficulty_mapping = {
            'easy': {
                'display_name': '简单模式',
                'description': '适合新手的简单地图',
                'color': (100, 255, 100),  # 绿色
                'features': [
                    '• 只有边界墙壁',
                    '• 移动速度较慢',
                    '• 食物分数倍率: 1.0x',
                    '• 适合新手练习'
                ]
            },
            'hard': {
                'display_name': '困难模式',
                'description': '有一些障碍物的中等难度',
                'color': (255, 255, 100),  # 黄色
                'features': [
                    '• 有内部障碍物',
                    '• 移动速度适中',
                    '• 食物分数倍率: 1.5x',
                    '• 经典挑战体验'
                ]
            },
            'hell': {
                'display_name': '地狱模式',
                'description': '复杂迷宫式的困难地图',
                'color': (255, 100, 100),  # 红色
                'features': [
                    '• 复杂迷宫障碍',
                    '• 移动速度很快',
                    '• 食物分数倍率: 2.0x',
                    '• 终极挑战体验'
                ]
            }
        }
        
        # 获取可用的难度配置
        available_difficulties = self.difficulty_loader.get_available_difficulties()
        
        for difficulty_key in available_difficulties:
            # 加载JSON配置
            json_config = self.difficulty_loader.load_difficulty_config(difficulty_key)
            if json_config:
                # 获取显示配置
                display_config = difficulty_mapping.get(difficulty_key, {
                    'display_name': json_config.get('name', difficulty_key),
                    'description': json_config.get('description', ''),
                    'color': (200, 200, 200),
                    'features': ['• 自定义配置']
                })
                
                # 合并配置
                option = {
                    'name': display_config['display_name'],
                    'key': difficulty_key,
                    'description': display_config['description'],
                    'features': display_config['features'],
                    'color': display_config['color'],
                    'json_config': json_config  # 保存完整的JSON配置
                }
                
                options.append(option)
        
        # 如果没有找到配置文件，使用默认配置
        if not options:
            print("警告: 未找到难度配置文件，使用默认配置")
            options = [{
                'name': '默认模式',
                'key': 'default',
                'description': '默认游戏配置',
                'features': ['• 基础游戏体验'],
                'color': (200, 200, 200),
                'json_config': None
            }]
        
        return options

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
        title_rect = title_text.get_rect(center=(self.config.SCREEN_W // 2, 60))
        surface.blit(title_text, title_rect)

        # 绘制副标题
        subtitle_text = self.font_manager.render_text("无尽模式 - 挑战你的极限", 'medium', (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.config.SCREEN_W // 2, 110))
        surface.blit(subtitle_text, subtitle_rect)

        # 绘制难度选项
        start_y = 150
        option_height = 130
        option_spacing = 15

        for i, option in enumerate(self.difficulty_options):
            y_pos = start_y + i * (option_height + option_spacing)
            is_selected = (i == self.selected_option)

            self._draw_difficulty_option(surface, option, y_pos, is_selected)

        # 绘制返回选项
        back_y = start_y + len(self.difficulty_options) * (option_height + option_spacing) + 30
        is_back_selected = (self.selected_option == self.back_option)
        self._draw_back_option(surface, back_y, is_back_selected)

        # 绘制控制提示
        self._draw_controls_help(surface)

    def _draw_gradient_background(self, surface):
        """绘制渐变背景"""
        # 从深蓝到深紫色的渐变，更加现代美观
        for y in range(self.config.SCREEN_H):
            ratio = y / self.config.SCREEN_H
            # 蓝色到紫色的渐变
            r = int(20 + 10 * ratio)        # 红色分量
            g = int(20 + 15 * ratio)        # 绿色分量  
            b = int(40 + 30 * ratio)        # 蓝色分量
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (self.config.SCREEN_W, y))
        
        # 添加星空效果
        import random
        random.seed(42)  # 固定随机种子，保证每次显示一致
        for _ in range(50):
            x = random.randint(0, self.config.SCREEN_W)
            y = random.randint(0, self.config.SCREEN_H)
            size = random.randint(1, 2)
            brightness = random.randint(100, 200)
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), size)

    def _draw_difficulty_option(self, surface, option, y_pos, is_selected):
        """绘制单个难度选项"""
        # 响应式选项区域计算
        option_width = min(720, self.config.SCREEN_W - 80)  # 最大720px，最小留边距
        option_height = 120
        option_x = (self.config.SCREEN_W - option_width) // 2
        option_rect = pygame.Rect(option_x, y_pos, option_width, option_height)

        # 选中效果
        if is_selected:
            # 增强脉动效果
            pulse_intensity = 0.15 * pygame.math.Vector2(1, 0).rotate(self.animation_time * self.pulse_speed * 360).x
            glow_intensity = 0.4 + abs(pulse_intensity) * 0.2
            glow_color = tuple(int(c * glow_intensity) for c in option['color'])

            # 绘制多层发光边框
            for i in range(3, 0, -1):
                glow_size = i * 6
                glow_rect = option_rect.inflate(glow_size, glow_size)
                alpha_color = tuple(int(c * (0.6 - i * 0.15)) for c in option['color'])
                pygame.draw.rect(surface, alpha_color, glow_rect, 2)

            # 渐变背景高亮
            for i in range(option_height):
                ratio = i / option_height
                highlight_intensity = 0.15 + 0.05 * ratio
                bg_color = tuple(int(c * highlight_intensity) for c in option['color'])
                pygame.draw.line(surface, bg_color, (option_x, y_pos + i), (option_x + option_width, y_pos + i))

            # 添加光晕效果
            corner_radius = 8
            for corner in [(option_x, y_pos), (option_x + option_width, y_pos), 
                          (option_x, y_pos + option_height), (option_x + option_width, y_pos + option_height)]:
                pygame.draw.circle(surface, glow_color, corner, corner_radius)
        else:
            # 普通渐变背景
            for i in range(option_height):
                ratio = i / option_height
                bg_value = 25 + int(10 * ratio)
                pygame.draw.line(surface, (bg_value, bg_value, bg_value), 
                                (option_x, y_pos + i), (option_x + option_width, y_pos + i))

        # 边框
        border_width = 3 if is_selected else 2
        border_color = option['color'] if is_selected else (80, 80, 80)
        pygame.draw.rect(surface, border_color, option_rect, border_width)

        # 圆角效果
        corner_radius = 6
        pygame.draw.rect(surface, border_color, option_rect, border_width, corner_radius)

        # 难度名称（左侧区域）
        name_color = option['color'] if is_selected else (220, 220, 220)
        name_text = self.font_manager.render_text(option['name'], 'xlarge', name_color)
        name_rect = name_text.get_rect(left=option_x + 25, top=y_pos + 15)
        surface.blit(name_text, name_rect)

        # 描述
        desc_text = self.font_manager.render_text(option['description'], 'medium', (180, 180, 180))
        desc_rect = desc_text.get_rect(left=option_x + 25, top=y_pos + 70)
        surface.blit(desc_text, desc_rect)

        # 特性列表（右侧区域）
        features_x = option_x + option_width // 2 + 10
        features_start_y = y_pos
        
        # 特性标题
        features_title = self.font_manager.render_text("特性:", 'medium', (160, 160, 160) if not is_selected else (200, 200, 200))
        features_title_rect = features_title.get_rect(left=features_x, top=features_start_y)
        surface.blit(features_title, features_title_rect)

        # 特性项目
        for j, feature in enumerate(option['features']):
            feature_color = (140, 140, 140) if not is_selected else (180, 180, 180)
            feature_text = self.font_manager.render_text(feature, 'small', feature_color)
            feature_rect = feature_text.get_rect(left=features_x, top=features_start_y + 30 + j * 22)
            surface.blit(feature_text, feature_rect)

        # 选中指示器
        if is_selected:
            indicator_size = 8
            indicator_x = option_x - 20
            indicator_y = y_pos + option_height // 2
            pygame.draw.circle(surface, option['color'], (indicator_x, indicator_y), indicator_size)
            pygame.draw.circle(surface, (255, 255, 255), (indicator_x, indicator_y), indicator_size - 2)

    def _draw_back_option(self, surface, y_pos, is_selected):
        """绘制返回选项"""
        color = (255, 255, 100) if is_selected else (180, 180, 180)
        back_width = 220
        back_height = 45
        back_x = (self.config.SCREEN_W - back_width) // 2
        back_rect = pygame.Rect(back_x, y_pos, back_width, back_height)

        if is_selected:
            # 增强选中效果
            # 发光边框
            for i in range(3, 0, -1):
                glow_size = i * 4
                glow_rect = back_rect.inflate(glow_size, glow_size)
                glow_color = tuple(int(c * (0.4 - i * 0.1)) for c in color)
                pygame.draw.rect(surface, glow_color, glow_rect, 2)

            # 渐变背景
            for i in range(back_height):
                ratio = i / back_height
                bg_intensity = 0.15 + 0.1 * ratio
                bg_color = tuple(int(c * bg_intensity) for c in color)
                pygame.draw.line(surface, bg_color, (back_x, y_pos + i), (back_x + back_width, y_pos + i))

            # 添加箭头动画
            arrow_pulse = 0.5 + 0.3 * pygame.math.Vector2(1, 0).rotate(self.animation_time * self.pulse_speed * 180).x
            arrow_color = tuple(int(c * arrow_pulse) for c in color)
        else:
            # 普通背景
            pygame.draw.rect(surface, (40, 40, 40), back_rect)
            arrow_color = color

        # 边框
        border_width = 3 if is_selected else 2
        pygame.draw.rect(surface, color, back_rect, border_width, 5)

        # 返回文本
        back_text = self.font_manager.render_text("← 返回主菜单", 'large', color)
        back_rect = back_text.get_rect(center=(self.config.SCREEN_W // 2, y_pos + back_height // 2))
        surface.blit(back_text, back_rect)

        # 选中指示器
        if is_selected:
            indicator_size = 6
            indicator_x = back_x - 15
            indicator_y = y_pos + back_height // 2
            pygame.draw.circle(surface, color, (indicator_x, indicator_y), indicator_size)
            pygame.draw.circle(surface, (255, 255, 255), (indicator_x, indicator_y), indicator_size - 2)

    def _draw_controls_help(self, surface):
        """绘制控制提示"""
        help_texts = [
            "↑↓ 选择难度    回车 确认    ESC 返回"
        ]

        # 控制提示背景
        help_bg_height = 40
        help_bg_rect = pygame.Rect(0, self.config.SCREEN_H - help_bg_height, 
                                  self.config.SCREEN_W, help_bg_height)
        
        # 渐变背景
        for i in range(help_bg_height):
            ratio = i / help_bg_height
            bg_value = 20 + int(15 * ratio)
            pygame.draw.line(surface, (bg_value, bg_value, bg_value), 
                            (0, self.config.SCREEN_H - help_bg_height + i), 
                            (self.config.SCREEN_W, self.config.SCREEN_H - help_bg_height + i))

        # 顶部边框
        pygame.draw.line(surface, (60, 60, 60), 
                        (0, self.config.SCREEN_H - help_bg_height),
                        (self.config.SCREEN_W, self.config.SCREEN_H - help_bg_height))

        for i, text in enumerate(help_texts):
            help_text = self.font_manager.render_text(text, 'help', (150, 150, 150))
            help_rect = help_text.get_rect(center=(self.config.SCREEN_W // 2,
                                                   self.config.SCREEN_H - help_bg_height // 2))
            surface.blit(help_text, help_rect)

    def get_selected_difficulty(self):
        """获取选中的难度配置"""
        return self.selected_difficulty
