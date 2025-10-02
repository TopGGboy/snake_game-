"""
关卡选择界面
"""
import pygame
import os
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
        self.draw(surface)

    def draw(self, surface):
        """
        绘制关卡选择界面
        """
        surface.fill((20, 20, 40))  # 深蓝色背景

        # 绘制标题
        title_text = self.font_manager.render_text("选择关卡", 'title', (255, 255, 255))
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

            # 计算位置
            y_pos = start_y + (i - start_index) * item_height

            # 绘制关卡项
            self._draw_level_item(surface, level, y_pos, is_selected)

        # 绘制选中指示器
        indicator_y = start_y + (self.selected_index - start_index) * item_height
        indicator_text = self.font_manager.render_text("▶", 'large', (255, 255, 0))
        indicator_rect = indicator_text.get_rect(
            center=(self.config.SCREEN_W // 2 - 200, indicator_y + item_height // 2))
        surface.blit(indicator_text, indicator_rect)

        # 绘制控制提示
        help_texts = [
            "方向键: 选择关卡",
            "回车: 开始游戏",
            "ESC: 返回主菜单"
        ]

        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'small', (150, 150, 150))
            surface.blit(help_surface, (self.config.SCREEN_W - 200, 400 + i * 25))

        # 绘制当前选中关卡的详细信息
        if self.levels:
            selected_level = self.levels[self.selected_index]
            self._draw_level_details(surface, selected_level)

    def _draw_level_item(self, surface, level, y_pos, is_selected):
        """绘制单个关卡项"""
        # 背景颜色
        bg_color = (40, 40, 80) if is_selected else (30, 30, 60)
        text_color = (255, 255, 100) if is_selected else (200, 200, 200)

        # 绘制背景
        item_width = 400
        item_height = 70
        item_x = self.config.SCREEN_W // 2 - item_width // 2

        pygame.draw.rect(surface, bg_color, (item_x, y_pos, item_width, item_height), border_radius=8)
        pygame.draw.rect(surface, (80, 80, 120), (item_x, y_pos, item_width, item_height), 2, border_radius=8)

        # 绘制关卡名称
        name_text = self.font_manager.render_text(level['name'], 'menu', text_color)
        name_rect = name_text.get_rect(midleft=(item_x + 20, y_pos + item_height // 2 - 10))
        surface.blit(name_text, name_rect)

        # 绘制目标分数
        score_text = self.font_manager.render_text(f"目标分数: {level['target_score']}", 'small', (150, 150, 150))
        score_rect = score_text.get_rect(midleft=(item_x + 20, y_pos + item_height // 2 + 15))
        surface.blit(score_text, score_rect)

    def _draw_level_details(self, surface, level):
        """绘制关卡详细信息"""
        # 详细信息面板
        panel_width = 350
        panel_height = 200
        panel_x = self.config.SCREEN_W - panel_width - 20
        panel_y = 150

        # 绘制面板背景
        pygame.draw.rect(surface, (40, 40, 60), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(surface, (80, 80, 100), (panel_x, panel_y, panel_width, panel_height), 2, border_radius=10)

        # 绘制标题
        detail_title = self.font_manager.render_text("关卡详情", 'medium', (255, 255, 255))
        detail_rect = detail_title.get_rect(center=(panel_x + panel_width // 2, panel_y + 25))
        surface.blit(detail_title, detail_rect)

        # 绘制关卡信息
        info_y = panel_y + 60
        info_spacing = 25

        # 关卡名称
        name_text = self.font_manager.render_text(f"名称: {level['name']}", 'small', (200, 200, 200))
        name_rect = name_text.get_rect(midleft=(panel_x + 20, info_y))
        surface.blit(name_text, name_rect)

        # 目标分数
        target_text = self.font_manager.render_text(f"目标分数: {level['target_score']}", 'small', (200, 200, 200))
        target_rect = target_text.get_rect(midleft=(panel_x + 20, info_y + info_spacing))
        surface.blit(target_text, target_rect)

        # 关卡描述
        description = level.get('description', '暂无描述')
        desc_text = self.font_manager.render_text(f"描述: {description}", 'small', (150, 150, 150))
        desc_rect = desc_text.get_rect(midleft=(panel_x + 20, info_y + info_spacing * 2))
        surface.blit(desc_text, desc_rect)

        # 文件信息
        file_text = self.font_manager.render_text(f"文件: {level['file_name']}", 'small', (100, 100, 100))
        file_rect = file_text.get_rect(midleft=(panel_x + 20, info_y + info_spacing * 3))
        surface.blit(file_text, file_rect)

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
