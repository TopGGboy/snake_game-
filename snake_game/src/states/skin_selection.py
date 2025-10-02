"""
蛇形象选择界面 - 卡片式布局
支持选择不同的蛇形象，采用卡片式设计，便于扩展
"""
import pygame
import os
from ..configs.config import Config
from ..configs.skin_config import get_available_skins, get_skin_by_key, get_snake_colors
from ..configs.game_balance import GameBalance
from ..utils.font_manager import get_font_manager
from ..utils.image_manager import get_image_manager


class SkinSelection:
    def __init__(self, previous_state=None):
        """
        初始化皮肤选择状态 - 卡片式布局
        :param previous_state: 前一个状态，用于判断是从哪个状态进入的
        """
        self.config = Config.get_instance()
        self.finished = False
        self.next = "main_menu"
        self.selected_skin = None
        self.previous_state = previous_state  # 记录前一个状态

        # 获取字体管理器
        self.font_manager = get_font_manager()

        # 蛇形象配置
        self.skin_options = get_available_skins()
        self.selected_option = 0  # 默认选择snake0

        # 卡片布局参数
        self.card_width = 280
        self.card_height = 180
        self.card_margin = 20
        self.cards_per_row = 2

        # 计算卡片布局
        self._calculate_layout()

        # 动画效果
        self.animation_time = 0
        self.hover_animation = {}

        # 获取图片管理器
        self.image_manager = get_image_manager()

        # 按钮位置 - 只保留返回按钮，居中显示
        self.back_button_rect = pygame.Rect(
            self.config.SCREEN_W // 2 - 100,
            self.config.SCREEN_H - 80,
            200, 50
        )

    def _calculate_layout(self):
        """计算卡片布局"""
        total_cards = len(self.skin_options)
        self.cards_per_row = min(2, total_cards)  # 每行最多2个卡片
        rows_needed = (total_cards + self.cards_per_row - 1) // self.cards_per_row

        # 计算起始Y位置
        start_y = 120
        total_height = rows_needed * (self.card_height + self.card_margin)
        self.layout_start_y = (self.config.SCREEN_H - total_height) // 2

        # 计算卡片位置
        self.card_positions = []
        for i in range(total_cards):
            row = i // self.cards_per_row
            col = i % self.cards_per_row

            x = (self.config.SCREEN_W - (
                        self.cards_per_row * (self.card_width + self.card_margin) - self.card_margin)) // 2
            x += col * (self.card_width + self.card_margin)
            y = self.layout_start_y + row * (self.card_height + self.card_margin)

            self.card_positions.append((x, y))

    def update_cursor(self, event_key):
        """
        处理卡片式导航
        """
        total_options = len(self.skin_options)

        if event_key == pygame.K_LEFT or event_key == pygame.K_a:
            self.selected_option = (self.selected_option - 1) % total_options
        elif event_key == pygame.K_RIGHT or event_key == pygame.K_d:
            self.selected_option = (self.selected_option + 1) % total_options
        elif event_key == pygame.K_UP or event_key == pygame.K_w:
            # 向上移动到上一行
            if self.selected_option >= self.cards_per_row:
                self.selected_option -= self.cards_per_row
        elif event_key == pygame.K_DOWN or event_key == pygame.K_s:
            # 向下移动到下一行
            if self.selected_option + self.cards_per_row < total_options:
                self.selected_option += self.cards_per_row
        elif event_key == pygame.K_RETURN or event_key == pygame.K_SPACE:
            # 选择皮肤，但不离开当前界面
            self.selected_skin = self.skin_options[self.selected_option]
            
            # 立即保存皮肤ID到全局配置
            skin_id = self._get_skin_id_from_key(self.selected_skin['image_prefix'])
            self.config.set_skin_id(skin_id)
            print(f"选择了皮肤: {self.selected_skin['name']}, 皮肤ID: {skin_id}")
        elif event_key == pygame.K_RETURN:
            # 回车键选择皮肤，但不离开当前界面
            self.selected_skin = self.skin_options[self.selected_option]
            
            # 立即保存皮肤ID到全局配置
            skin_id = self._get_skin_id_from_key(self.selected_skin['image_prefix'])
            self.config.set_skin_id(skin_id)
            print(f"选择了皮肤: {self.selected_skin['name']}, 皮肤ID: {skin_id}")
        elif event_key == pygame.K_ESCAPE:
            # ESC键返回
            self.finished = True
        elif event_key == pygame.K_b:
            # B键返回主菜单
            self.finished = True

    def update(self, surface, keys):
        """
        更新皮肤选择界面
        """
        # 更新动画时间
        self.animation_time += 1 / 60

        # 更新悬停动画
        for i in range(len(self.skin_options)):
            if i == self.selected_option:
                if i not in self.hover_animation:
                    self.hover_animation[i] = 0
                self.hover_animation[i] = min(self.hover_animation[i] + 0.1, 1.0)
            else:
                if i in self.hover_animation:
                    self.hover_animation[i] = max(self.hover_animation[i] - 0.05, 0)

        self.draw(surface)

    def draw(self, surface):
        """
        绘制卡片式皮肤选择界面
        """
        # 绘制背景
        self._draw_background(surface)

        # 绘制标题
        title_text = self.font_manager.render_text("选择蛇形象", 'title', (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.config.SCREEN_W // 2, 60))
        surface.blit(title_text, title_rect)

        # 绘制皮肤卡片
        for i, skin in enumerate(self.skin_options):
            x, y = self.card_positions[i]
            is_selected = (i == self.selected_option)
            hover_progress = self.hover_animation.get(i, 0)

            self._draw_skin_card(surface, skin, x, y, is_selected, hover_progress)

        # 绘制按钮 - 只绘制返回按钮
        self._draw_back_button(surface)

        # 绘制控制提示
        self._draw_controls_help(surface)

    def _draw_background(self, surface):
        """绘制背景"""
        # 深色渐变背景
        for y in range(self.config.SCREEN_H):
            ratio = y / self.config.SCREEN_H
            r = int(20 * (1 - ratio))
            g = int(15 * (1 - ratio))
            b = int(30 * (1 - ratio))
            pygame.draw.line(surface, (r, g, b), (0, y), (self.config.SCREEN_W, y))

    def _draw_skin_card(self, surface, skin, x, y, is_selected, hover_progress):
        """绘制单个皮肤卡片"""
        # 获取皮肤颜色配置
        skin_id = skin['skin_id']
        colors = get_snake_colors(skin_id, is_selected)  # is_selected作为加速状态

        # 计算卡片区域
        card_rect = pygame.Rect(x, y, self.card_width, self.card_height)

        # 悬停效果
        hover_offset = int(hover_progress * 5)
        card_rect.y -= hover_offset

        # 卡片背景
        if is_selected:
            # 选中状态 - 使用皮肤主题色
            bg_color = tuple(int(c * 0.15) for c in colors['head_fill'])
            border_color = colors['highlight']
            border_width = 3
        else:
            # 普通状态
            bg_color = (40, 40, 50)
            border_color = (80, 80, 100)
            border_width = 2

        # 绘制卡片背景
        pygame.draw.rect(surface, bg_color, card_rect, border_radius=12)
        pygame.draw.rect(surface, border_color, card_rect, border_width, border_radius=12)

        # 绘制发光效果
        if is_selected:
            glow_rect = card_rect.inflate(10, 10)
            glow_color = tuple(int(c * 0.3) for c in colors['head_fill'])
            pygame.draw.rect(surface, glow_color, glow_rect, 2, border_radius=16)

        # 卡片内容区域
        content_padding = 15
        content_rect = card_rect.inflate(-content_padding * 2, -content_padding * 2)

        # 绘制皮肤名称
        name_color = colors['head_fill'] if is_selected else (220, 220, 220)
        name_text = self.font_manager.render_text(skin['name'], 'large', name_color)
        name_rect = name_text.get_rect(centerx=content_rect.centerx, top=content_rect.top + 10)
        surface.blit(name_text, name_rect)

        # 绘制皮肤预览
        preview_y = name_rect.bottom + 15
        self._draw_card_preview(surface, skin, content_rect.centerx, preview_y, is_selected)

        # 绘制描述
        desc_y = preview_y + 50
        desc_text = self.font_manager.render_text(skin['description'], 'small', (180, 180, 180))
        desc_rect = desc_text.get_rect(centerx=content_rect.centerx, top=desc_y)
        surface.blit(desc_text, desc_rect)

        # 绘制状态指示器
        status_y = desc_rect.bottom + 8
        self._draw_status_indicator(surface, skin, content_rect.centerx, status_y)

    def _get_skin_id_from_key(self, key):
        """从key中提取皮肤ID"""
        if key.startswith('snake'):
            try:
                return int(key[5:])  # 提取snake后面的数字
            except ValueError:
                return 0
        return 0

    def _draw_card_preview(self, surface, skin, center_x, center_y, is_selected):
        """绘制卡片内的皮肤预览"""
        key = skin['image_prefix']
        skin_id = self._get_skin_id_from_key(key)

        # 获取皮肤颜色配置
        colors = get_snake_colors(skin_id, is_selected)  # is_selected作为加速状态

        # 使用图片管理器获取蛇形象贴图（蛇头一定存在）
        head_image = self.image_manager.get_snake_image(skin_id, "head")
        body_image = self.image_manager.get_snake_image(skin_id, "body0")

        # 缩放蛇头图片为合适大小并水平翻转（让蛇头朝向右边）
        head_size = (GameBalance.SNAKE_HEAD_SIZE, GameBalance.SNAKE_HEAD_SIZE)
        scaled_head = pygame.transform.scale(head_image, head_size)
        # 水平翻转图片，让蛇头朝向右边
        flipped_head = pygame.transform.flip(scaled_head, True, False)

        # 绘制蛇头（蛇头一定存在）
        head_rect = flipped_head.get_rect(center=(center_x, center_y))
        surface.blit(flipped_head, head_rect)

        # 如果有蛇身图片，则使用蛇身图片
        if body_image:
            # 缩放蛇身图片为合适大小
            body_size = (GameBalance.SNAKE_BODY_SIZE, GameBalance.SNAKE_BODY_SIZE)
            scaled_body = pygame.transform.scale(body_image, body_size)

            # 绘制蛇身段（2个身体段）
            for i in range(2):
                body_x = center_x - (i + 1) * (GameBalance.SNAKE_BODY_SIZE + 5)
                body_rect = scaled_body.get_rect(center=(body_x, center_y))
                surface.blit(scaled_body, body_rect)
        else:
            # 没有蛇身图片时使用默认圆点绘制蛇身
            body_radius = GameBalance.SNAKE_BODY_SIZE // 2 * (1.2 if is_selected else 1.0)
            for i in range(3):
                body_x = center_x - (i + 1) * (GameBalance.SNAKE_BODY_SIZE)
                body_color = colors['highlight'] if is_selected else colors['body_fill']
                pygame.draw.circle(surface, body_color, (body_x, center_y), body_radius)
                pygame.draw.circle(surface, colors['body_border'], (body_x, center_y), body_radius, 1)

        # 选中状态添加发光效果
        if is_selected:
            glow_radius = 35
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*colors['highlight'], 80),
                               (glow_radius, glow_radius), glow_radius)
            glow_rect = glow_surface.get_rect(center=(center_x, center_y))
            surface.blit(glow_surface, glow_rect)

    def _draw_status_indicator(self, surface, skin, center_x, center_y):
        """绘制状态指示器"""
        # 检查图片资源状态
        head_path = f"snake_game/assets/graphics/snake/{skin['image_prefix']}/{skin['image_prefix']}_head.png"
        body_path = f"snake_game/assets/graphics/snake/{skin['image_prefix']}/{skin['image_prefix']}_body0.png"

        head_exists = os.path.exists(head_path)
        body_exists = os.path.exists(body_path)

        # 状态文本和颜色
        if head_exists and body_exists:
            status_text = "图片资源完整"
            status_color = (100, 255, 100)
        elif head_exists:
            status_text = "部分图片资源"
            status_color = (255, 200, 100)
        else:
            status_text = "使用默认图形"
            status_color = (200, 200, 200)

        # 绘制状态指示器
        status_surf = self.font_manager.render_text(status_text, 'small', status_color)
        status_rect = status_surf.get_rect(center=(center_x, center_y))
        surface.blit(status_surf, status_rect)

    def _draw_back_button(self, surface):
        """绘制返回按钮"""
        # 检查鼠标是否悬停
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.back_button_rect.collidepoint(mouse_pos)

        # 按钮颜色
        if is_hovered:
            bg_color = (60, 60, 80)
            text_color = (255, 255, 200)
            border_color = (255, 255, 100)
        else:
            bg_color = (50, 50, 60)
            text_color = (200, 200, 200)
            border_color = (100, 100, 120)

        # 绘制按钮背景
        pygame.draw.rect(surface, bg_color, self.back_button_rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.back_button_rect, 2, border_radius=8)

        # 绘制按钮文本
        back_text = self.font_manager.render_text("返回主菜单", 'medium', text_color)
        back_rect = back_text.get_rect(center=self.back_button_rect.center)
        surface.blit(back_text, back_rect)



    def _draw_controls_help(self, surface):
        """绘制控制提示"""
        help_texts = [
            "←→↑↓ 选择卡片    回车 选择皮肤    ESC/B 返回主菜单"
        ]

        for i, text in enumerate(help_texts):
            help_text = self.font_manager.render_text(text, 'help', (150, 150, 150))
            help_rect = help_text.get_rect(center=(self.config.SCREEN_W // 2,
                                                   self.config.SCREEN_H - 30 - i * 25))
            surface.blit(help_text, help_rect)

    def get_selected_skin(self):
        """获取选中的皮肤ID"""
        if self.selected_skin:
            # 从key中提取数字ID
            key = self.selected_skin.get('image_prefix', 'snake0')
            if key.startswith('snake'):
                try:
                    skin_id = int(key[5:])  # 提取snake后面的数字
                    print(f"皮肤选择返回皮肤ID: {skin_id}")
                    return skin_id
                except ValueError:
                    return 0
        print("皮肤选择返回默认皮肤ID: 0")
        return 0  # 默认返回snake0

    def handle_mouse_event(self, event):
        """处理鼠标事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
            mouse_pos = pygame.mouse.get_pos()

            # 检查是否点击了皮肤卡片
            for i, (x, y) in enumerate(self.card_positions):
                card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
                if card_rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    self.selected_skin = self.skin_options[i]
                    # 立即保存皮肤ID到全局配置
                    skin_id = self._get_skin_id_from_key(self.selected_skin['image_prefix'])
                    self.config.set_skin_id(skin_id)
                    print(f"选择了皮肤: {self.selected_skin['name']}, 皮肤ID: {skin_id}")
                    return True



            # 检查是否点击了返回按钮
            if self.back_button_rect.collidepoint(mouse_pos):
                self.finished = True
                return True

        return False
