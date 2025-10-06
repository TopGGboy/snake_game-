"""
现代化主菜单 - 具有渐变背景和动画效果
"""
import pygame
import math
import random
from ..configs.config import Config
from ..configs.skin_config import get_snake_colors
from ..configs.game_balance import GameBalance
from ..utils.font_manager import get_font_manager
from ..utils.image_manager import get_image_manager


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
        self.menu_options = ["无尽模式", "闯关模式", "选择皮肤", "退出"]
        self.selected_option = 0  # 当前选中的选项
        
        # 动画参数
        self.animation_time = 0
        self.button_hover_animation = [0] * len(self.menu_options)
        
        # 颜色配置
        self.colors = {
            'background_start': (10, 20, 40),     # 深蓝渐变起始
            'background_end': (30, 40, 80),       # 深蓝渐变结束
            'title_gradient_start': (255, 215, 0), # 金色渐变起始
            'title_gradient_end': (255, 165, 0),   # 橙色渐变结束
            'button_normal': (70, 80, 120),       # 按钮正常状态
            'button_hover': (90, 100, 160),       # 按钮悬停状态
            'button_selected': (255, 215, 0),     # 按钮选中状态
            'button_text': (240, 240, 240),       # 按钮文字
            'button_border': (120, 140, 200),     # 按钮边框
            'help_text': (180, 180, 200),         # 帮助文字
            'preview_bg': (30, 35, 60),           # 预览背景
            'preview_border': (80, 100, 160),     # 预览边框
            'particle_color': (100, 150, 255, 50) # 粒子效果颜色
        }
        
        # 粒子效果
        self.particles = []
        self._init_particles()

    def _init_particles(self):
        """初始化粒子效果"""
        for _ in range(20):
            self.particles.append({
                'x': random.uniform(self.config.SCREEN_W * 0.2, self.config.SCREEN_W * 0.8),
                'y': random.uniform(self.config.SCREEN_H * 0.2, self.config.SCREEN_H * 0.8),
                'size': random.uniform(1, 4),
                'speed_x': random.uniform(-0.5, 0.5),
                'speed_y': random.uniform(-0.5, 0.5),
                'life': random.uniform(50, 150)
            })

    def _update_particles(self):
        """更新粒子效果"""
        for particle in self.particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            particle['life'] -= 1
            
            # 重置死亡的粒子
            if particle['life'] <= 0 or particle['x'] < 0 or particle['x'] > self.config.SCREEN_W or particle['y'] < 0 or particle['y'] > self.config.SCREEN_H:
                particle['x'] = random.uniform(self.config.SCREEN_W * 0.2, self.config.SCREEN_W * 0.8)
                particle['y'] = random.uniform(self.config.SCREEN_H * 0.2, self.config.SCREEN_H * 0.8)
                particle['life'] = random.uniform(50, 150)

    def update_cursor(self, event_key):
        """
        处理菜单导航
        """
        if event_key == pygame.K_UP or event_key == pygame.K_w:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif event_key == pygame.K_DOWN or event_key == pygame.K_s:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif event_key == pygame.K_RETURN or event_key == pygame.K_SPACE:
            if self.selected_option == 0:  # 无尽模式
                self.finished = True
                self.config.MAIN_MENU_FLAG = False
            elif self.selected_option == 1:  # 闯关模式
                self.finished = True
                self.next = "level_selection"
            elif self.selected_option == 2:  # 选择皮肤
                self.finished = True
                self.next = "skin_selection"
            elif self.selected_option == 3:  # 退出
                pygame.quit()
                quit()

    def update(self, surface, keys):
        """
        更新主菜单界面
        """
        # 更新动画时间
        self.animation_time += 1
        if self.animation_time > 360:
            self.animation_time = 0
            
        # 更新按钮悬停动画
        for i in range(len(self.menu_options)):
            if i == self.selected_option:
                self.button_hover_animation[i] = min(self.button_hover_animation[i] + 0.2, 1.0)
            else:
                self.button_hover_animation[i] = max(self.button_hover_animation[i] - 0.1, 0.0)
                
        # 更新粒子效果
        self._update_particles()
        
        self.draw(surface)

    def draw(self, surface):
        """
        绘制现代化主菜单
        """
        # 绘制渐变背景
        self._draw_gradient_background(surface)
        
        # 绘制粒子效果
        self._draw_particles(surface)
        
        # 绘制标题（带渐变效果）
        self._draw_title(surface)
        
        # 绘制菜单选项（现代化按钮）
        self._draw_menu_buttons(surface)
        
        # 绘制当前蛇形象预览
        self._draw_snake_preview(surface)
        
        # 绘制控制提示
        self._draw_help_text(surface)

    def _draw_gradient_background(self, surface):
        """绘制渐变背景"""
        for y in range(self.config.SCREEN_H):
            # 计算当前行的颜色插值
            ratio = y / self.config.SCREEN_H
            r = int(self.colors['background_start'][0] * (1 - ratio) + self.colors['background_end'][0] * ratio)
            g = int(self.colors['background_start'][1] * (1 - ratio) + self.colors['background_end'][1] * ratio)
            b = int(self.colors['background_start'][2] * (1 - ratio) + self.colors['background_end'][2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.config.SCREEN_W, y))

    def _draw_particles(self, surface):
        """绘制粒子效果"""
        for particle in self.particles:
            alpha = min(255, int(particle['life'] * 2.55))
            color = (*self.colors['particle_color'][:3], alpha)
            pygame.draw.circle(surface, color, (int(particle['x']), int(particle['y'])), int(particle['size']))

    def _draw_title(self, surface):
        """绘制标题（带渐变效果）"""
        title_text = "贪吃蛇游戏"
        title_font = self.font_manager.get_font('title')
        
        # 创建标题表面
        title_surface = pygame.Surface((self.config.SCREEN_W, 100), pygame.SRCALPHA)
        
        # 绘制渐变标题
        for i, char in enumerate(title_text):
            # 计算字符的渐变颜色
            char_ratio = i / len(title_text)
            r = int(self.colors['title_gradient_start'][0] * (1 - char_ratio) + self.colors['title_gradient_end'][0] * char_ratio)
            g = int(self.colors['title_gradient_start'][1] * (1 - char_ratio) + self.colors['title_gradient_end'][1] * char_ratio)
            b = int(self.colors['title_gradient_start'][2] * (1 - char_ratio) + self.colors['title_gradient_end'][2] * char_ratio)
            
            # 渲染单个字符
            char_surface = title_font.render(char, True, (r, g, b))
            char_rect = char_surface.get_rect()
            char_rect.x = i * 80 + 50
            char_rect.y = 20
            
            # 添加发光效果
            glow_surface = title_font.render(char, True, (r, g, b, 100))
            for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                glow_rect = char_rect.copy()
                glow_rect.x += offset[0] * 2
                glow_rect.y += offset[1] * 2
                title_surface.blit(glow_surface, glow_rect)
            
            title_surface.blit(char_surface, char_rect)
        
        # 定位标题
        title_rect = title_surface.get_rect(center=(self.config.SCREEN_W // 2, 120))
        surface.blit(title_surface, title_rect)

    def _draw_menu_buttons(self, surface):
        """绘制现代化菜单按钮"""
        button_width = 300
        button_height = 60
        button_spacing = 20
        start_y = 220
        
        for i, option in enumerate(self.menu_options):
            # 计算按钮位置
            x = self.config.SCREEN_W // 2 - button_width // 2
            y = start_y + i * (button_height + button_spacing)
            
            # 计算动画效果
            anim_value = self.button_hover_animation[i]
            scale_factor = 1.0 + anim_value * 0.05
            glow_intensity = int(anim_value * 100)
            
            # 创建按钮表面
            button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            
            # 绘制按钮背景（带圆角）
            button_color = self.colors['button_hover'] if i == self.selected_option else self.colors['button_normal']
            pygame.draw.rect(button_surface, button_color, (0, 0, button_width, button_height), 
                            border_radius=15)
            
            # 绘制边框
            border_color = (*self.colors['button_border'], 150 + glow_intensity)
            pygame.draw.rect(button_surface, border_color, (0, 0, button_width, button_height), 
                            width=3, border_radius=15)
            
            # 绘制选中状态的发光效果
            if i == self.selected_option:
                glow_color = (*self.colors['button_selected'], 50 + glow_intensity)
                for glow_size in range(3, 0, -1):
                    pygame.draw.rect(button_surface, glow_color, 
                                   (-glow_size, -glow_size, button_width + glow_size*2, button_height + glow_size*2), 
                                   width=glow_size, border_radius=15 + glow_size)
            
            # 绘制按钮文字
            text_color = self.colors['button_text']
            if i == self.selected_option:
                # 选中状态的文字发光效果
                text_surface = self.font_manager.render_text(option, 'menu', text_color)
                glow_surface = self.font_manager.render_text(option, 'menu', (*text_color, 100))
                
                # 添加文字发光
                for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    text_rect = text_surface.get_rect(center=(button_width//2 + offset[0], button_height//2 + offset[1]))
                    button_surface.blit(glow_surface, text_rect)
            else:
                text_surface = self.font_manager.render_text(option, 'menu', text_color)
            
            # 绘制文字
            text_rect = text_surface.get_rect(center=(button_width//2, button_height//2))
            button_surface.blit(text_surface, text_rect)
            
            # 应用缩放动画
            if scale_factor != 1.0:
                scaled_width = int(button_width * scale_factor)
                scaled_height = int(button_height * scale_factor)
                scaled_surface = pygame.transform.scale(button_surface, (scaled_width, scaled_height))
                scaled_rect = scaled_surface.get_rect(center=(x + button_width//2, y + button_height//2))
                surface.blit(scaled_surface, scaled_rect)
            else:
                surface.blit(button_surface, (x, y))

    def _draw_help_text(self, surface):
        """绘制控制提示"""
        help_text = "使用 ↑↓ 方向键或 W/S 键选择，回车或空格确认"
        help_surface = self.font_manager.render_text(help_text, 'help', self.colors['help_text'])
        help_rect = help_surface.get_rect(center=(self.config.SCREEN_W // 2, self.config.SCREEN_H - 40))
        surface.blit(help_surface, help_rect)

    def _draw_snake_preview(self, surface):
        """绘制现代化蛇形象预览"""
        # 获取当前皮肤ID
        current_skin_id = self.config.get_skin_id()

        # 预览区域位置和大小
        preview_x = self.config.SCREEN_W - 240
        preview_y = 250
        preview_width = 240
        preview_height = 160

        # 创建预览表面（带透明度）
        preview_surface = pygame.Surface((preview_width, preview_height), pygame.SRCALPHA)
        
        # 绘制现代化预览背景
        pygame.draw.rect(preview_surface, (*self.colors['preview_bg'], 200), 
                        (0, 0, preview_width, preview_height), border_radius=15)
        pygame.draw.rect(preview_surface, (*self.colors['preview_border'], 200), 
                        (0, 0, preview_width, preview_height), width=2, border_radius=15)
        
        # 添加发光边框效果
        glow_intensity = int((math.sin(self.animation_time * 0.1) + 1) * 30)
        for i in range(3):
            glow_size = i + 1
            glow_color = (*self.colors['preview_border'], 50 - i*15 + glow_intensity)
            pygame.draw.rect(preview_surface, glow_color, 
                           (-glow_size, -glow_size, preview_width + glow_size*2, preview_height + glow_size*2), 
                           width=1, border_radius=15 + glow_size)

        # 绘制标题
        preview_title = self.font_manager.render_text("当前蛇形象", 'medium', (240, 240, 240))
        title_rect = preview_title.get_rect(center=(preview_width // 2, 25))
        preview_surface.blit(preview_title, title_rect)

        # 使用图片管理器获取蛇形象贴图
        head_image = self.image_manager.get_snake_image(current_skin_id, "head")
        body_image = self.image_manager.get_snake_image(current_skin_id, "body0")

        # 预览中心位置
        preview_center_x = preview_width // 2 + 15
        preview_center_y = preview_height // 2 + 10

        # 缩放蛇头图片为合适大小并水平翻转（让蛇头朝向右边）
        head_size = (GameBalance.SNAKE_HEAD_SIZE + 5, GameBalance.SNAKE_HEAD_SIZE + 5)
        scaled_head = pygame.transform.scale(head_image, head_size)
        flipped_head = pygame.transform.flip(scaled_head, True, False)

        # 添加蛇头发光效果
        head_glow = pygame.Surface((head_size[0] + 8, head_size[1] + 8), pygame.SRCALPHA)
        pygame.draw.ellipse(head_glow, (*self.colors['button_selected'], 80), 
                          (0, 0, head_size[0] + 8, head_size[1] + 8))
        head_glow_rect = head_glow.get_rect(center=(preview_center_x, preview_center_y))
        preview_surface.blit(head_glow, head_glow_rect)

        # 绘制蛇头（蛇头一定存在）
        head_rect = flipped_head.get_rect(center=(preview_center_x, preview_center_y))
        preview_surface.blit(flipped_head, head_rect)

        # 如果有蛇身图片，则使用蛇身图片
        if body_image:
            # 缩放蛇身图片为合适大小
            body_size = (GameBalance.SNAKE_BODY_SIZE + 3, GameBalance.SNAKE_BODY_SIZE + 3)
            scaled_body = pygame.transform.scale(body_image, body_size)

            # 绘制蛇身段（3个身体段，带间距动画）
            for i in range(3):
                # 添加身体段间距动画
                spacing_factor = math.sin(self.animation_time * 0.05 + i * 0.5) * 0.3 + 1.0
                body_x = preview_center_x - (i + 1) * (GameBalance.SNAKE_BODY_SIZE + 8) * spacing_factor
                body_rect = scaled_body.get_rect(center=(body_x, preview_center_y))
                preview_surface.blit(scaled_body, body_rect)
        else:
            # 没有蛇身图片时使用默认圆点绘制蛇身
            colors = get_snake_colors(current_skin_id, is_boosting=False)
            body_radius = (GameBalance.SNAKE_BODY_SIZE + 3) // 2
            for i in range(3):
                # 添加身体段间距动画
                spacing_factor = math.sin(self.animation_time * 0.05 + i * 0.5) * 0.3 + 1.0
                body_x = preview_center_x - (i + 1) * (GameBalance.SNAKE_BODY_SIZE + 8) * spacing_factor
                body_color = colors['body_fill']
                # 添加身体段发光效果
                pygame.draw.circle(preview_surface, (*body_color, 200), (int(body_x), preview_center_y), body_radius + 2)
                pygame.draw.circle(preview_surface, body_color, (int(body_x), preview_center_y), body_radius)
                pygame.draw.circle(preview_surface, colors['body_border'], (int(body_x), preview_center_y), body_radius, 1)

        # 绘制皮肤ID信息
        skin_info = self.font_manager.render_text(f"皮肤 #{current_skin_id + 1}", 'small', (220, 220, 240))
        info_rect = skin_info.get_rect(center=(preview_width // 2, preview_height - 25))
        preview_surface.blit(skin_info, info_rect)

        # 将预览表面绘制到主表面
        surface.blit(preview_surface, (preview_x, preview_y))
