"""
关卡选择界面
"""
import pygame
import os
import math
from ..configs.config import Config
from ..utils.font_manager import get_font_manager
from ..utils.image_manager import get_image_manager
from .base_state import BaseState


class LevelSelection(BaseState):
    def __init__(self):
        """
        初始化关卡选择界面
        """
        print("初始化关卡选择界面...")
        self.config = Config.get_instance()
        self.finished = False
        self.next = None
        self.selected_level = None

        # 获取字体管理器
        self.font_manager = get_font_manager()

        # 获取图片管理器
        self.image_manager = get_image_manager()

        # 加载关卡列表
        self.levels = self._load_levels()
        print(f"加载了 {len(self.levels)} 个关卡")
        self.selected_index = 0  # 当前选中的关卡索引
        
        # 动画相关变量
        self.animation_time = 0
        self.selection_animation = 0
        self.scroll_offset = 0
        self.target_scroll_offset = 0
        
        # 背景相关
        self.background_surface = None
        self._create_background()
        
        # 粒子效果
        self.particles = []
        self._init_particles()

    def _create_background(self):
        """创建渐变背景"""
        self.background_surface = pygame.Surface((self.config.SCREEN_W, self.config.SCREEN_H))
        
        # 创建渐变效果
        for y in range(self.config.SCREEN_H):
            # 从深蓝到深紫的渐变
            r = int(20 + 10 * math.sin(y * 0.01))
            g = int(20 + 5 * math.sin(y * 0.015))
            b = int(40 + 20 * math.sin(y * 0.02))
            pygame.draw.line(self.background_surface, (r, g, b), (0, y), (self.config.SCREEN_W, y))
            
    def _init_particles(self):
        """初始化粒子效果"""
        for _ in range(50):
            self.particles.append({
                'x': pygame.time.get_ticks() % self.config.SCREEN_W,
                'y': pygame.time.get_ticks() % self.config.SCREEN_H,
                'speed': 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.001),
                'size': 1 + 2 * math.sin(pygame.time.get_ticks() * 0.002),
                'color': (255, 255, 255, 50 + int(50 * math.sin(pygame.time.get_ticks() * 0.003)))
            })
            
    def _draw_particles(self, surface):
        """绘制粒子效果"""
        for particle in self.particles:
            # 更新粒子位置
            particle['x'] += particle['speed'] * math.sin(pygame.time.get_ticks() * 0.001)
            particle['y'] += particle['speed'] * math.cos(pygame.time.get_ticks() * 0.001)
            
            # 边界检查
            if particle['x'] < 0:
                particle['x'] = self.config.SCREEN_W
            if particle['x'] > self.config.SCREEN_W:
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = self.config.SCREEN_H
            if particle['y'] > self.config.SCREEN_H:
                particle['y'] = 0
                
            # 绘制粒子
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             int(particle['size']))

    def _load_levels(self):
        """加载关卡列表"""
        import os

        level_path = "./src/configs/level"

        print(f"检查路径: {level_path}")
        if os.path.exists(level_path):
            levels_dir = level_path
            print(f"找到关卡目录: {levels_dir}")
        else:
            print(f"未找到关卡目录: {level_path}")

        levels = []

        # 遍历关卡目录下的所有JSON文件
        for filename in os.listdir(levels_dir):
            if filename.startswith("level_") and filename.endswith(".json"):
                level_path = os.path.join(levels_dir, filename)
                try:
                    import json
                    with open(level_path, 'r', encoding='utf-8') as f:
                        level_data = json.load(f)

                    # 提取关卡信息
                    level_info = {
                        'name': level_data.get('name', '未知关卡'),
                        'description': level_data.get('description', ''),
                        'target_score': level_data.get('target_score', 100),
                        'file_path': level_path,
                        'file_name': filename
                    }
                    levels.append(level_info)
                except Exception as e:
                    print(f"加载关卡文件失败 {filename}: {e}")

        # 按文件名排序
        levels.sort(key=lambda x: x['file_name'])

        print(f"加载了 {len(levels)} 个关卡")
        return levels

    def handle_event(self, event):
        """
        处理pygame事件
        :param event: pygame事件
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # 返回主菜单
                self.finished = True
                self.next = "main_menu"
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.levels)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.levels)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.levels:
                    # 选择当前关卡，直接跳转到关卡模式
                    self.selected_level = self.levels[self.selected_index]
                    self.finished = True
                    self.next = f"level_mode:{self.selected_level['file_name'].replace('.json', '')}"

                    # 保存关卡信息到全局配置
                    self.config.set_selected_level(self.selected_level)
                    print(f"选择了关卡: {self.selected_level['name']}, 文件: {self.selected_level['file_path']}")
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                # 快速切换到上一个关卡
                self.selected_index = (self.selected_index - 1) % len(self.levels)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                # 快速切换到下一个关卡
                self.selected_index = (self.selected_index + 1) % len(self.levels)

    def update(self, surface, keys):
        """
        更新关卡选择界面
        """
        # 更新动画时间
        self.animation_time += 0.05
        self.selection_animation = (math.sin(self.animation_time * 2) + 1) * 0.5
        
        # 平滑滚动效果
        if abs(self.scroll_offset - self.target_scroll_offset) > 0.1:
            self.scroll_offset += (self.target_scroll_offset - self.scroll_offset) * 0.2
        else:
            self.scroll_offset = self.target_scroll_offset
            
        self.draw(surface)

    def draw(self, surface):
        """
        绘制关卡选择界面
        """
        # 绘制渐变背景
        surface.blit(self.background_surface, (0, 0))
        
        # 添加动态粒子效果
        self._draw_particles(surface)

        # 绘制标题（带阴影效果）
        title_color = (255, 215, 0)  # 金色
        shadow_color = (180, 150, 0)
        
        # 阴影
        shadow_text = self.font_manager.render_text("选择关卡", 'title', shadow_color)
        shadow_rect = shadow_text.get_rect(center=(self.config.SCREEN_W // 2 + 3, 83))
        surface.blit(shadow_text, shadow_rect)
        
        # 主标题
        title_text = self.font_manager.render_text("选择关卡", 'title', title_color)
        title_rect = title_text.get_rect(center=(self.config.SCREEN_W // 2, 80))
        surface.blit(title_text, title_rect)

        if not self.levels:
            # 没有关卡的情况
            no_levels_text = self.font_manager.render_text("没有找到关卡文件", 'large', (255, 100, 100))
            no_levels_rect = no_levels_text.get_rect(center=(self.config.SCREEN_W // 2, 200))
            surface.blit(no_levels_text, no_levels_rect)

            hint_text = self.font_manager.render_text("请检查关卡配置文件是否存在", 'medium', (200, 200, 200))
            hint_rect = hint_text.get_rect(center=(self.config.SCREEN_W // 2, 250))
            surface.blit(hint_text, hint_rect)

            back_text = self.font_manager.render_text("按ESC返回主菜单", 'help', (150, 150, 150))
            back_rect = back_text.get_rect(center=(self.config.SCREEN_W // 2, 300))
            surface.blit(back_text, back_rect)
            return

        # 绘制关卡列表
        start_y = 150
        item_height = 80
        visible_count = 5  # 可见的关卡数量

        # 计算显示范围
        start_index = max(0, self.selected_index - visible_count // 2)
        end_index = min(len(self.levels), start_index + visible_count)
        start_index = max(0, end_index - visible_count)

        for i in range(start_index, end_index):
            level = self.levels[i]
            is_selected = (i == self.selected_index)

            # 计算位置（向左偏移50像素）
            y_pos = start_y + (i - start_index) * item_height

            # 绘制关卡项
            self._draw_level_item(surface, level, y_pos, is_selected, offset_x=-130)

        # 绘制选中指示器（动画效果）
        indicator_y = start_y + (self.selected_index - start_index) * item_height
        indicator_size = 20 + int(5 * math.sin(self.animation_time * 3))
        indicator_color = (255, 215, 0)  # 金色
        
        # 绘制指示器三角形（向左偏移100像素，与关卡选项对齐）
        points = [
            (self.config.SCREEN_W // 2 - 380, indicator_y + item_height // 2),
            (self.config.SCREEN_W // 2 - 360, indicator_y + item_height // 2 - indicator_size // 2),
            (self.config.SCREEN_W // 2 - 360, indicator_y + item_height // 2 + indicator_size // 2)
        ]
        pygame.draw.polygon(surface, indicator_color, points)
        
        # 绘制指示器光晕
        glow_surface = pygame.Surface((indicator_size * 2, indicator_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 215, 0, 50), 
                         (indicator_size, indicator_size), indicator_size)
        surface.blit(glow_surface, 
                   (self.config.SCREEN_W // 2 - 365 - indicator_size,
                    indicator_y + item_height // 2 - indicator_size))

        # 绘制滚动条
        if len(self.levels) > visible_count:
            scrollbar_width = 8
            scrollbar_x = self.config.SCREEN_W // 2 + 90
            scrollbar_height = visible_count * item_height
            scrollbar_y = start_y
            
            # 滚动条背景
            pygame.draw.rect(surface, (60, 60, 80), 
                           (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), 
                           border_radius=4)
            
            # 滚动条滑块
            scroll_ratio = self.selected_index / len(self.levels)
            slider_height = max(30, scrollbar_height * visible_count / len(self.levels))
            slider_y = scrollbar_y + (scrollbar_height - slider_height) * scroll_ratio
            
            pygame.draw.rect(surface, (100, 150, 255), 
                           (scrollbar_x, slider_y, scrollbar_width, slider_height), 
                           border_radius=4)

        # 绘制控制提示（带背景框）
        help_bg_width = 180
        help_bg_height = 100
        help_bg_x = self.config.SCREEN_W - help_bg_width - 20
        help_bg_y = 400
        
        # 绘制提示背景
        help_bg_surface = pygame.Surface((help_bg_width, help_bg_height), pygame.SRCALPHA)
        pygame.draw.rect(help_bg_surface, (40, 40, 60, 180), 
                       (0, 0, help_bg_width, help_bg_height), border_radius=8)
        surface.blit(help_bg_surface, (help_bg_x, help_bg_y))
        
        help_texts = [
            "方向键: 选择关卡",
            "回车: 开始游戏",
            "ESC: 返回主菜单"
        ]

        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'small', (180, 180, 200))
            help_rect = help_surface.get_rect(midleft=(help_bg_x + 15, help_bg_y + 25 + i * 25))
            surface.blit(help_surface, help_rect)

        # 绘制当前选中关卡的详细信息
        if self.levels:
            selected_level = self.levels[self.selected_index]
            self._draw_level_details(surface, selected_level)

    def _draw_level_item(self, surface, level, y_pos, is_selected, offset_x=0):
        """绘制单个关卡项"""
        # 计算动画效果
        scale_factor = 1.0 + (0.05 if is_selected else 0.0) * self.selection_animation
        glow_intensity = int(30 * self.selection_animation) if is_selected else 0
        
        # 创建卡片表面（带透明度）
        item_width = 400
        item_height = 70
        item_x = self.config.SCREEN_W // 2 - item_width // 2 + offset_x
        
        card_surface = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
        
        # 绘制卡片背景（带渐变）
        if is_selected:
            # 选中状态：金色渐变
            for i in range(item_height):
                alpha = 150 + int(50 * math.sin(i * 0.1 + self.animation_time))
                color = (255, 215, 0, alpha)  # 金色渐变
                pygame.draw.line(card_surface, color, (0, i), (item_width, i))
        else:
            # 未选中状态：蓝色渐变
            for i in range(item_height):
                alpha = 80 + int(20 * math.sin(i * 0.1))
                color = (30, 30, 60, alpha)  # 深蓝渐变
                pygame.draw.line(card_surface, color, (0, i), (item_width, i))
        
        # 绘制边框
        border_color = (255, 215, 0, 200) if is_selected else (80, 80, 120, 150)
        border_width = 3 if is_selected else 2
        pygame.draw.rect(card_surface, border_color, (0, 0, item_width, item_height), 
                       border_width, border_radius=8)
        
        # 高光效果
        if is_selected:
            highlight_surface = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, (255, 255, 255, glow_intensity), 
                           (0, 0, item_width, item_height), border_radius=8)
            card_surface.blit(highlight_surface, (0, 0))
        
        # 应用缩放效果
        scaled_width = int(item_width * scale_factor)
        scaled_height = int(item_height * scale_factor)
        scaled_card = pygame.transform.smoothscale(card_surface, (scaled_width, scaled_height))
        scaled_x = item_x + (item_width - scaled_width) // 2
        scaled_y = y_pos + (item_height - scaled_height) // 2
        
        # 绘制阴影
        shadow_surface = pygame.Surface((scaled_width + 10, scaled_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80), 
                       (5, 5, scaled_width, scaled_height), border_radius=8)
        surface.blit(shadow_surface, (scaled_x - 5, scaled_y - 5))
        
        # 绘制卡片
        surface.blit(scaled_card, (scaled_x, scaled_y))
        
        # 绘制关卡名称（带阴影效果）
        text_color = (255, 255, 100) if is_selected else (200, 200, 200)
        name_text = self.font_manager.render_text(level['name'], 'menu', text_color)
        name_shadow = self.font_manager.render_text(level['name'], 'menu', (0, 0, 0, 100))
        name_rect = name_text.get_rect(midleft=(scaled_x + 20, scaled_y + scaled_height // 2 - 10))
        surface.blit(name_shadow, (name_rect.x + 2, name_rect.y + 2))
        surface.blit(name_text, name_rect)

        # 绘制目标分数（带阴影效果）
        score_text = self.font_manager.render_text(f"目标分数: {level['target_score']}", 'small', (150, 150, 150))
        score_shadow = self.font_manager.render_text(f"目标分数: {level['target_score']}", 'small', (0, 0, 0, 100))
        score_rect = score_text.get_rect(midleft=(scaled_x + 20, scaled_y + scaled_height // 2 + 15))
        surface.blit(score_shadow, (score_rect.x + 1, score_rect.y + 1))
        surface.blit(score_text, score_rect)
            
    def _draw_difficulty_indicator(self, surface, x, y, difficulty):
        """绘制难度指示器"""
        colors = [(100, 255, 100), (255, 255, 100), (255, 100, 100)]  # 绿黄红
        difficulty = min(max(difficulty, 1), 3)  # 限制在1-3之间
        
        # 绘制难度点
        for i in range(3):
            color = colors[i] if i < difficulty else (80, 80, 80)
            radius = 4 if i < difficulty else 3
            pygame.draw.circle(surface, color, (x + i * 10, y), radius)

    def _draw_level_details(self, surface, level):
        """绘制关卡详细信息"""
        # 详细信息面板
        panel_width = 280
        panel_height = 160
        panel_x = self.config.SCREEN_W - panel_width - 10  # 向右移动10像素
        panel_y = 160

        # 创建面板表面（带透明度）
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # 绘制面板背景（带渐变）
        for i in range(panel_height):
            alpha = 180 + int(20 * math.sin(i * 0.05))
            color = (40, 40, 60, alpha)
            pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))
        
        # 绘制边框
        pygame.draw.rect(panel_surface, (80, 80, 100, 200), 
                       (0, 0, panel_width, panel_height), 2, border_radius=12)
        
        # 绘制高光效果
        highlight_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for i in range(10):  # 顶部高光
            alpha = 30 - i * 3
            pygame.draw.line(highlight_surface, (255, 255, 255, alpha), (0, i), (panel_width, i))
        panel_surface.blit(highlight_surface, (0, 0))
        
        # 绘制到主表面
        surface.blit(panel_surface, (panel_x, panel_y))

        # 绘制标题（带阴影效果）
        detail_title = self.font_manager.render_text("关卡详情", 'small', (255, 255, 255))
        detail_shadow = self.font_manager.render_text("关卡详情", 'small', (0, 0, 0, 100))
        detail_rect = detail_title.get_rect(center=(panel_x + panel_width // 2, panel_y + 25))
        surface.blit(detail_shadow, (detail_rect.x + 2, detail_rect.y + 2))
        surface.blit(detail_title, detail_rect)

        # 绘制分隔线
        pygame.draw.line(surface, (80, 80, 100), 
                       (panel_x + 15, panel_y + 45), 
                       (panel_x + panel_width - 15, panel_y + 45), 1)

        # 绘制关卡信息
        info_y = panel_y + 55
        info_spacing = 22

        # 关卡名称
        name_text = self.font_manager.render_text(f"名称: {level['name']}", 'small', (220, 220, 220))
        name_shadow = self.font_manager.render_text(f"名称: {level['name']}", 'small', (0, 0, 0, 100))
        name_rect = name_text.get_rect(midleft=(panel_x + 15, info_y))
        surface.blit(name_shadow, (name_rect.x + 1, name_rect.y + 1))
        surface.blit(name_text, name_rect)

        # 目标分数
        target_text = self.font_manager.render_text(f"目标分数: {level['target_score']}", 'small', (200, 200, 200))
        target_shadow = self.font_manager.render_text(f"目标分数: {level['target_score']}", 'small', (0, 0, 0, 100))
        target_rect = target_text.get_rect(midleft=(panel_x + 15, info_y + info_spacing))
        surface.blit(target_shadow, (target_rect.x + 1, target_rect.y + 1))
        surface.blit(target_text, target_rect)

        # 难度显示
        difficulty = level.get('difficulty', 1)
        diff_text = self.font_manager.render_text(f"难度: ", 'small', (200, 200, 200))
        diff_rect = diff_text.get_rect(midleft=(panel_x + 15, info_y + info_spacing * 2))
        surface.blit(diff_text, diff_rect)
        self._draw_difficulty_indicator(surface, panel_x + 65, info_y + info_spacing * 2, difficulty)

        # 关卡描述
        description = level.get('description', '暂无描述')
        desc_text = self.font_manager.render_text(f"描述: {description}", 'small', (180, 180, 180))
        desc_rect = desc_text.get_rect(midleft=(panel_x + 15, info_y + info_spacing * 3))
        surface.blit(desc_text, desc_rect)

        # 开始游戏提示
        start_text = self.font_manager.render_text("按回车开始", 'small', (100, 255, 100))
        start_rect = start_text.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 20))
        surface.blit(start_text, start_rect)

    def get_selected_level(self):
        """获取选中的关卡信息"""
        return self.selected_level

    def update_cursor(self, key):
        """
        更新光标位置（兼容游戏主循环的接口）
        :param key: 按键
        """
        # 模拟KEYDOWN事件来处理按键
        event = pygame.event.Event(pygame.KEYDOWN, {'key': key})
        self.handle_event(event)
