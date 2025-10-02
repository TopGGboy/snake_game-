import pygame
import json
import os
from ..components.snake import Snake
from ..components.food import FoodManager
from ..components.wall import WallManager
from ..configs.config import Config
from ..configs.game_balance import GameBalance
from ..configs.difficulty_loader import get_difficulty_loader
from ..configs.level_loader import get_level_loader
from ..utils.grid_utils import GridUtils
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.font_manager import get_font_manager
from .level_loading import LevelLoadingScreen
from .level_pause_menu import LevelPauseMenu
from .level_game_over import LevelGameOverMenu
from .level_state_manager import LevelStateManager


class LevelMode:
    def __init__(self, level_name):
        """
        初始化关卡模式
        :param level_name: 关卡名称 (如 "level_01")
        """
        self.finished = False
        self.next = None
        self.level_name = level_name

        # 获取关卡加载器
        self.level_loader = get_level_loader()
        self.level_config = self.level_loader.load_level_config(level_name)

        if not self.level_config:
            # 如果关卡加载失败，使用默认配置
            self.level_config = self._get_default_level_config()
            print(f"警告: 关卡 {level_name} 加载失败，使用默认配置")

        # 获取难度配置加载器
        self.difficulty_loader = get_difficulty_loader()

        # 获取屏幕尺寸和全局配置
        self.config = Config.get_instance()
        self.screen_width = self.config.SCREEN_W
        self.screen_height = self.config.SCREEN_H

        # 创建蛇实例，使用全局配置中的皮肤ID
        skin_id = self.config.get_skin_id()
        print(f"创建蛇实例，使用全局皮肤ID: {skin_id}")
        self.snake = Snake("snake0", skin_id=skin_id)

        # 应用关卡配置
        self._apply_level_config()

        # 创建食物管理器
        self.food_manager = FoodManager(max_food_count=GameBalance.MAX_FOOD_COUNT)

        # 创建墙管理器并加载墙体
        self.wall_manager = WallManager()
        self._setup_walls()

        # 关卡导航相关属性
        self.available_levels = self._get_available_levels()
        self.current_level_index = self._get_current_level_index()

        # 创建状态管理器
        self.state_manager = LevelStateManager(self, self.screen_width, self.screen_height)

        # 游戏统计
        self.score = 0
        self.target_score = self.level_config.get('target_score', 100)
        self.level_completed = False

        # 时间管理
        self.last_time = pygame.time.get_ticks()

        # 性能监控
        self.performance_monitor = PerformanceMonitor()

        # 字体管理器
        self.font_manager = get_font_manager()

        # 游戏状态
        self.game_over = False
        self.paused = False

        # 调试选项
        self.debug_collision = False

        print(f"关卡模式初始化完成 - 关卡: {self.level_config.get('name', '未知')}, 目标分数: {self.target_score}")

    def _get_available_levels(self):
        """获取所有可用的关卡"""
        levels_dir = "./src/configs/level"
        available_levels = []

        # 检查关卡目录是否存在
        if os.path.exists(levels_dir):
            for file in os.listdir(levels_dir):
                if file.startswith('level_') and file.endswith('.json'):
                    level_name = file.replace('.json', '')
                    available_levels.append(level_name)

        # 如果没有找到关卡文件，返回默认关卡列表
        if not available_levels:
            available_levels = ['level_01', 'level_02', 'level_03']

        return sorted(available_levels)

    def _get_current_level_index(self):
        """获取当前关卡在可用关卡列表中的索引"""
        for i, level in enumerate(self.available_levels):
            if level == self.level_name:
                return i
        return 0

    def _get_default_level_config(self):
        """获取默认关卡配置"""
        return {
            'name': '默认关卡',
            'description': '默认关卡配置',
            'target_score': 100,
            'difficulty': 'easy',
            'map': [],
            'snake': {
                'speed': 4,
                'initial_position': [8, 10]
            },
            'food': {},
            'game_settings': {
                'score_multiplier': 1.0,
                'walls_kill': True,
                'self_collision': True
            }
        }

    def _apply_level_config(self):
        """应用关卡配置到游戏参数"""
        # 应用蛇的配置
        snake_config = self.level_config.get('snake', {})
        speed = snake_config.get('speed', 4)

        # 将JSON中的速度值转换为实际的移动速度
        actual_speed = speed * 30  # 假设每个格子30像素

        self.snake.config.move_speed = actual_speed
        self.snake.normal_speed = actual_speed
        self.snake.boost_speed = actual_speed * self.snake.config.boost_multiplier

        # 设置蛇的初始位置
        initial_pos_config = snake_config.get('initial_position', [8, 10])
        initial_pos = GridUtils.align_to_grid(initial_pos_config[0] * 30, initial_pos_config[1] * 30)
        self.snake.rect.center = initial_pos
        print(f"蛇初始位置设置为: {initial_pos}")
        self.snake.reset(initial_pos)

        # 应用游戏设置
        game_settings = self.level_config.get('game_settings', {})
        self.score_multiplier = game_settings.get('score_multiplier', 1.0)
        self.walls_kill = game_settings.get('walls_kill', True)
        self.self_collision = game_settings.get('self_collision', True)

    def _setup_walls(self):
        """根据关卡配置设置墙壁"""
        # 使用关卡配置加载墙体
        self.wall_manager.load_from_difficulty_config(self.level_config)
        print(f"从关卡配置加载了墙体: {self.level_config.get('name', '未知')}")

    def handle_event(self, event):
        """
        处理pygame事件
        :param event: pygame事件
        """
        # 使用状态管理器处理事件
        self.state_manager.handle_event(event)

        # 检查游戏状态并更新状态管理器
        if self.level_completed and self.state_manager.get_current_state() != self.state_manager.STATE_LEVEL_COMPLETE:
            # 关卡完成，切换到关卡完成状态
            self.state_manager.set_state(self.state_manager.STATE_LEVEL_COMPLETE)
        elif self.game_over and self.state_manager.get_current_state() != self.state_manager.STATE_GAME_OVER:
            # 游戏结束，切换到游戏结束状态
            self.state_manager.set_state(self.state_manager.STATE_GAME_OVER)
            self.state_manager.level_game_over.set_level_info(self.current_level_index + 1, len(self.available_levels),
                                                              self.level_completed)
        elif self.paused and self.state_manager.get_current_state() != self.state_manager.STATE_PAUSE:
            # 游戏暂停，切换到暂停状态
            self.state_manager.set_state(self.state_manager.STATE_PAUSE)
            self.state_manager.level_pause_menu.set_level_info(self.current_level_index + 1, len(self.available_levels))
        elif not self.paused and self.state_manager.get_current_state() == self.state_manager.STATE_PAUSE:
            # 如果暂停状态被取消，确保状态管理器也回到游戏状态
            self.state_manager.set_state(self.state_manager.STATE_GAME)

    def update(self, surface, keys):
        """
        更新游戏状态
        :param surface: 绘制表面
        :param keys: 键盘按键状态
        """
        # 性能监控开始
        self.performance_monitor.start_frame()
        self.performance_monitor.start_update_timing()

        # 处理输入
        self._handle_input(keys)

        # 检查关卡是否完成
        if not self.level_completed and self.score >= self.target_score:
            self.level_completed = True
            self.show_level_loading = True

            # 游戏胜利，切换到胜利界面（使用暂停界面，但标题改为游戏胜利）
            self.state_manager.set_state(self.state_manager.STATE_LEVEL_COMPLETE)
            self.state_manager.level_pause_menu.set_level_info(self.current_level_index + 1, len(self.available_levels))
            print(f"关卡完成！得分: {self.score}, 目标分数: {self.target_score}")

        # 更新状态管理器
        self.state_manager.update(surface, keys)

        # 如果处于界面状态或游戏暂停，不更新游戏逻辑
        if self.state_manager.is_in_interface_state() or self.paused:
            # 如果游戏暂停，暂停时更新last_time，防止恢复时时间跳跃
            if self.paused:
                self.last_time = pygame.time.get_ticks()
            return

        # 如果关卡完成，显示完成界面
        if self.level_completed:
            self._draw_level_complete(surface)
        elif not self.game_over:
            # 计算时间增量
            current_time = pygame.time.get_ticks()
            dt = current_time - self.last_time
            self.last_time = current_time

            # 处理蛇的键盘输入
            self.snake.handle_input(keys)

            # 基于时间更新蛇的位置
            self.snake.update(dt)

            # 更新食物并检查食物碰撞
            snake_head_pos = (self.snake.position[0], self.snake.position[1])
            snake_body_positions = [(seg[0], seg[1]) for seg in self.snake.body_segments]

            # 添加墙壁位置到避免列表
            avoid_positions = snake_body_positions.copy()
            avoid_positions.append(snake_head_pos)
            avoid_positions.extend(self.wall_manager.get_wall_positions())

            score_gained = self.food_manager.update(dt, snake_head_pos, snake_body_positions, self.snake.rect)

            # 如果食物被重新生成，确保避开墙壁
            for food in self.food_manager.foods:
                if hasattr(food, '_needs_repositioning') and food._needs_repositioning:
                    food.randomize_position(avoid_positions)
                    food._needs_repositioning = False

            # 如果吃到食物，蛇增长
            if score_gained > 0:
                self.snake.grow()
                # 应用分数倍率
                actual_score = int(score_gained * getattr(self, 'score_multiplier', 1.0))
                self.score += actual_score
                print(f"得分: {self.score}, 蛇长度: {self.snake.get_length()}")

            # 检查其他碰撞
            self._check_collisions()

        # 性能监控结束更新阶段
        self.performance_monitor.end_update_timing()
        self.performance_monitor.start_draw_timing()

        # 绘制游戏元素
        self.draw(surface)

        # 性能监控结束绘制阶段
        self.performance_monitor.end_draw_timing()

    def _handle_input(self, keys):
        """处理额外的输入"""
        # F1 切换性能显示
        if keys[pygame.K_F1]:
            self.performance_monitor.toggle_display()

        # F3 切换碰撞区域调试显示
        if keys[pygame.K_F3]:
            self.debug_collision = not self.debug_collision
            print(f"碰撞区域调试: {'开启' if self.debug_collision else '关闭'}")

        # F4 切换碰撞检测调试日志
        if keys[pygame.K_F4]:
            from src.components.food import Food
            Food.DEBUG_COLLISION = not Food.DEBUG_COLLISION
            print(f"碰撞检测调试日志: {'开启' if Food.DEBUG_COLLISION else '关闭'}")

    def _check_collisions(self):
        """
        检查所有碰撞情况
        """
        # 检查是否撞到自己
        if getattr(self, 'self_collision', True) and self.snake.check_self_collision():
            self.snake.is_dead = True
            self.game_over = True
            # 立即切换到游戏结束状态
            self.state_manager.set_state(self.state_manager.STATE_GAME_OVER)
            self.state_manager.level_game_over.set_level_info(self.current_level_index + 1, len(self.available_levels),
                                                              self.level_completed)
            print(f"游戏结束：蛇撞到自己了！最终得分: {self.score}")
            return

        # 检查是否撞到墙壁
        if getattr(self, 'walls_kill', True):
            snake_head_pos = (self.snake.position[0], self.snake.position[1])
            if self.wall_manager.check_collision(snake_head_pos, self.snake.config.collision_radius):
                self.snake.is_dead = True
                self.game_over = True
                # 立即切换到游戏结束状态
                self.state_manager.set_state(self.state_manager.STATE_GAME_OVER)
                self.state_manager.level_game_over.set_level_info(self.current_level_index + 1, len(self.available_levels),
                                                                  self.level_completed)
                print(f"游戏结束：蛇撞到墙壁了！最终得分: {self.score}")
                return

        # 检查是否撞到边界
        if not getattr(self, 'walls_kill', True) or self.wall_manager.get_wall_count() == 0:
            if self.snake.check_boundary_collision(screen_width=self.screen_width, screen_height=self.screen_height):
                self.snake.is_dead = True
                self.game_over = True
                # 立即切换到游戏结束状态
                self.state_manager.set_state(self.state_manager.STATE_GAME_OVER)
                self.state_manager.level_game_over.set_level_info(self.current_level_index + 1, len(self.available_levels),
                                                                  self.level_completed)
                print(f"游戏结束：蛇撞到边界了！最终得分: {self.score}")
                return

    def draw(self, surface):
        """
        绘制游戏画面
        :param surface: 绘制表面
        """
        # 获取颜色主题
        colors = GameBalance.get_color_scheme('classic')
        surface.fill(colors['background'])

        # 绘制网格（可选）
        self._draw_grid(surface, colors['grid'])

        # 绘制墙壁（带碰撞调试）
        self.wall_manager.draw(surface, self.debug_collision)

        # 绘制食物（带碰撞调试）
        self.food_manager.draw(surface, self.debug_collision)

        # 绘制蛇（带碰撞调试）
        self.snake.draw(surface, self.debug_collision)

        # 绘制UI
        self._draw_ui(surface, colors['text'])

        # 绘制状态管理器界面
        self.state_manager.draw(surface)

        # 绘制性能监控
        self.performance_monitor.draw_stats(surface)

    def _draw_grid(self, surface, grid_color):
        """绘制网格线（调试用）"""
        show_grid = True
        if not show_grid:
            return

        for x in range(0, self.screen_width, GridUtils.GRID_SIZE):
            pygame.draw.line(surface, grid_color, (x, 0), (x, self.screen_height))
        for y in range(0, self.screen_height, GridUtils.GRID_SIZE):
            pygame.draw.line(surface, grid_color, (0, y), (self.screen_width, y))

    def _draw_ui(self, surface, text_color):
        """
        绘制用户界面
        :param surface: 绘制表面
        :param text_color: 文本颜色
        """
        # 绘制关卡信息
        level_text = self.font_manager.render_text(f"关卡: {self.level_config.get('name', '未知')}", 'score',
                                                   text_color)
        surface.blit(level_text, (10, 10))

        # 绘制分数
        score_text = self.font_manager.render_text(f"分数: {self.score}/{self.target_score}", 'score', text_color)
        surface.blit(score_text, (10, 50))

        # 绘制蛇的长度
        length_text = self.font_manager.render_text(f"长度: {self.snake.get_length()}", 'score', text_color)
        surface.blit(length_text, (10, 90))

        # 绘制进度条
        self._draw_progress_bar(surface)

        # 绘制控制提示
        help_texts = [
            "ESC/P: 暂停游戏",
            "F1: 性能监控",
            "F3: 碰撞调试",
            "F4: 碰撞日志",
            "方向键: 移动",
            "空格键: 加速"
        ]

        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'small', (150, 150, 150))
            surface.blit(help_surface, (self.screen_width - 150, 10 + i * 20))

    def _draw_progress_bar(self, surface):
        """绘制进度条"""
        progress = min(self.score / self.target_score, 1.0)
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 130

        # 背景
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        # 进度
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_width * progress), bar_height))
        # 边框
        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

        # 进度文本
        progress_text = self.font_manager.render_text(f"{int(progress * 100)}%", 'small', (255, 255, 255))
        text_rect = progress_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        surface.blit(progress_text, text_rect)

    def _go_to_next_level(self):
        """切换到下一关"""
        if self.current_level_index < len(self.available_levels) - 1:
            next_level = self.available_levels[self.current_level_index + 1]
            self.finished = True
            self.next = f'level_mode:{next_level}'
            print(f"切换到下一关: {next_level}")
        else:
            # 已经是最后一关，返回主菜单
            self.finished = True
            self.next = 'main_menu'
            print("已经是最后一关，返回主菜单")

    def _go_to_previous_level(self):
        """切换到上一关"""
        if self.current_level_index > 0:
            prev_level = self.available_levels[self.current_level_index - 1]
            self.finished = True
            self.next = f'level_mode:{prev_level}'
            print(f"切换到上一关: {prev_level}")
        else:
            # 已经是第一关，返回主菜单
            self.finished = True
            self.next = 'main_menu'
            print("已经是第一关，返回主菜单")

    def _draw_level_complete(self, surface):
        """绘制关卡完成界面"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # 完成文本
        complete_text = self.font_manager.render_text("关卡完成！", 'title', (255, 255, 0))
        text_rect = complete_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        surface.blit(complete_text, text_rect)

        # 得分信息
        score_text = self.font_manager.render_text(f"得分: {self.score}/{self.target_score}", 'xlarge', (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 10))
        surface.blit(score_text, score_rect)

        # 关卡导航信息
        level_info = f"当前关卡: {self.current_level_index + 1}/{len(self.available_levels)}"
        level_text = self.font_manager.render_text(level_info, 'large', (200, 200, 200))
        level_rect = level_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        surface.blit(level_text, level_rect)

        # 继续提示
        if self.current_level_index < len(self.available_levels) - 1:
            continue_text = self.font_manager.render_text("按回车键进入下一关", 'large', (200, 200, 200))
        else:
            continue_text = self.font_manager.render_text("按回车键返回主菜单", 'large', (200, 200, 200))
        continue_rect = continue_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 90))
        surface.blit(continue_text, continue_rect)

    def restart_game(self):
        """重新开始游戏"""
        # 重新设置蛇的初始位置
        snake_config = self.level_config.get('snake', {})
        initial_pos_config = snake_config.get('initial_position', [8, 10])
        initial_pos = GridUtils.align_to_grid(initial_pos_config[0] * 30, initial_pos_config[1] * 30)
        self.snake.reset(initial_pos)

        # 重新应用关卡配置
        self._apply_level_config()

        # 重置食物管理器
        self.food_manager.reset()

        # 重新设置墙壁
        self.wall_manager.clear_walls()
        self._setup_walls()

        self.score = 0
        self.level_completed = False
        self.game_over = False
        self.paused = False
        self.show_level_loading = False
        self.show_level_pause = False
        self.show_level_game_over = False
        self.last_time = pygame.time.get_ticks()
        self.performance_monitor.reset_stats()

        # 重置状态管理器
        self.state_manager.set_state(self.state_manager.STATE_GAME)

        print(f"关卡重新开始 - {self.level_config.get('name', '未知')}")
