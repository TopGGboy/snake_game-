import pygame
from src.components.snake import Snake
from src.components.food import FoodManager
from src.components.wall import WallManager
from src.configs.config import Config
from src.configs.game_balance import GameBalance
from src.configs.difficulty_loader import get_difficulty_loader
from src.utils.image_manager import initialize_game_images
from src.utils.grid_utils import GridUtils
from src.utils.performance_monitor import PerformanceMonitor
from src.utils.font_manager import get_font_manager


class InfiniteMode:
    def __init__(self, difficulty_config=None):
        """
        初始化无尽模式
        :param difficulty_config: 难度配置字典
        """
        self.finished = False
        self.next = None

        # 获取难度配置加载器
        self.difficulty_loader = get_difficulty_loader()

        # 处理难度配置
        self.difficulty_config = difficulty_config or {
            'name': '默认模式',
            'key': 'default',
            'json_config': None
        }

        # 获取JSON配置
        self.json_config = None
        if self.difficulty_config and 'json_config' in self.difficulty_config:
            self.json_config = self.difficulty_config['json_config']

        # 如果没有JSON配置，尝试加载
        if not self.json_config and 'key' in self.difficulty_config:
            self.json_config = self.difficulty_loader.load_difficulty_config(self.difficulty_config['key'])

        # 初始化图片管理器
        print("初始化图片管理器...")
        initialize_game_images()

        self.snake = Snake("snake0")  # 创建蛇实例

        # 获取屏幕尺寸
        self.config = Config.get_instance()
        self.screen_width = self.config.SCREEN_W
        self.screen_height = self.config.SCREEN_H

        # 根据JSON配置设置游戏参数
        self._apply_json_config()

        # 创建食物管理器
        self.food_manager = FoodManager(max_food_count=GameBalance.MAX_FOOD_COUNT)

        # 创建墙管理器并加载墙体
        self.wall_manager = WallManager()
        self._setup_walls()

        # 游戏统计
        self.score = 0
        self.high_score = 0

        # 难度和速度管理
        self.current_difficulty = self.difficulty_config.get('key', 'default')
        self.dynamic_speed = False  # 是否启用动态速度调整

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
        self.debug_collision = False  # 是否显示碰撞区域

        print(f"无尽模式初始化完成 - 难度: {self.difficulty_config.get('name', '默认')}")

    def _apply_json_config(self):
        """应用JSON配置到游戏参数"""
        if not self.json_config:
            # 使用默认配置
            self.snake.config.move_speed = 120.0
            self.snake.normal_speed = 120.0
            self.snake.boost_speed = 120.0 * self.snake.config.boost_multiplier

            # 设置默认初始位置
            initial_pos = GridUtils.align_to_grid(*GameBalance.INITIAL_POSITION)
            self.snake.rect.center = initial_pos
            print(f"使用默认配置，蛇初始位置: {initial_pos}")
            return

        # 应用蛇的配置
        snake_config = self.json_config.get('snake', {})
        speed = snake_config.get('speed', 5)

        # 将JSON中的速度值转换为实际的移动速度
        # JSON中的speed是每秒移动的格子数，需要转换为像素/秒
        actual_speed = speed * 30  # 假设每个格子30像素

        self.snake.config.move_speed = actual_speed
        self.snake.normal_speed = actual_speed
        self.snake.boost_speed = actual_speed * self.snake.config.boost_multiplier

        # 设置蛇的初始位置
        if self.json_config:
            initial_pos = self.difficulty_loader.get_snake_initial_position(self.json_config)
        else:
            initial_pos = GridUtils.align_to_grid(*GameBalance.INITIAL_POSITION)

        self.snake.rect.center = initial_pos
        print(f"蛇初始位置设置为: {initial_pos}")
        self.snake.reset(initial_pos)

        # 应用食物配置
        food_config = self.json_config.get('food', {})
        special_food_chance = food_config.get('special_food_chance', 0.1)

        # 应用游戏设置
        game_settings = self.json_config.get('game_settings', {})
        self.score_multiplier = game_settings.get('score_multiplier', 1.0)
        self.walls_kill = game_settings.get('walls_kill', True)
        self.self_collision = game_settings.get('self_collision', True)

    def _setup_walls(self):
        """根据JSON配置设置墙壁"""
        if not self.json_config:
            # 没有JSON配置，创建默认边界墙壁
            self.wall_manager.create_border_walls(margin=30)
            print("创建了默认边界墙壁")
            return

        # 使用JSON配置加载墙体
        self.wall_manager.load_from_difficulty_config(self.json_config)
        print(f"从JSON配置加载了墙体: {self.json_config.get('name', '未知')}")

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

        if not self.game_over and not self.paused:
            # 计算时间增量
            current_time = pygame.time.get_ticks()
            dt = current_time - self.last_time
            self.last_time = current_time

            # 处理蛇的键盘输入（只处理方向改变，不立即移动）
            self.snake.handle_input(keys)

            # 动态调整蛇的移动速度
            if self.dynamic_speed:
                new_delay = GameBalance.calculate_speed_increase(self.score)
                self.snake.config.move_delay = new_delay

            # 基于时间更新蛇的位置
            self.snake.update(dt)

            # 更新食物并检查食物碰撞
            snake_head_pos = (self.snake.position[0], self.snake.position[1])  # 蛇头浮点坐标
            snake_body_positions = [(seg[0], seg[1]) for seg in self.snake.body_segments]  # 身体浮点坐标

            # 添加墙壁位置到避免列表
            avoid_positions = snake_body_positions.copy()
            avoid_positions.append(snake_head_pos)
            avoid_positions.extend(self.wall_manager.get_wall_positions())

            score_gained = self.food_manager.update(dt, snake_head_pos, snake_body_positions, self.snake.rect)  # 获取得分

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
                self.high_score = max(self.high_score, self.score)
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

        # F2 切换动态速度
        if keys[pygame.K_F2]:
            self.dynamic_speed = not self.dynamic_speed
            print(f"动态速度调整: {'开启' if self.dynamic_speed else '关闭'}")

        # F3 切换碰撞区域调试显示
        if keys[pygame.K_F3]:
            self.debug_collision = not self.debug_collision
            print(f"碰撞区域调试: {'开启' if self.debug_collision else '关闭'}")

        # F4 切换碰撞检测调试日志
        if keys[pygame.K_F4]:
            from src.components.food import Food
            Food.DEBUG_COLLISION = not Food.DEBUG_COLLISION
            print(f"碰撞检测调试日志: {'开启' if Food.DEBUG_COLLISION else '关闭'}")

        # R 重新开始游戏
        if keys[pygame.K_r] and self.game_over:
            self.restart_game()

    def _check_collisions(self):
        """
        检查所有碰撞情况
        """
        # 检查是否撞到自己（如果启用自碰撞）
        if getattr(self, 'self_collision', True) and self.snake.check_self_collision():
            self.snake.is_dead = True
            self.game_over = True
            print(f"游戏结束：蛇撞到自己了！最终得分: {self.score}")
            return

        # 检查是否撞到墙壁（如果启用墙壁碰撞）
        if getattr(self, 'walls_kill', True):
            snake_head_pos = (self.snake.position[0], self.snake.position[1])
            if self.wall_manager.check_collision(snake_head_pos, self.snake.config.collision_radius):
                self.snake.is_dead = True
                self.game_over = True
                print(f"游戏结束：蛇撞到墙壁了！最终得分: {self.score}")
                return

        # 检查是否撞到边界（如果没有墙壁或墙壁不致命）
        if not getattr(self, 'walls_kill', True) or self.wall_manager.get_wall_count() == 0:
            if self.snake.check_boundary_collision(screen_width=self.screen_width, screen_height=self.screen_height):
                self.snake.is_dead = True
                self.game_over = True
                print(f"游戏结束：蛇撞到边界了！最终得分: {self.score}")
                return

    def draw(self, surface):
        """
        绘制游戏画面
        :param surface: 绘制表面
        """
        # 获取颜色主题
        colors = GameBalance.get_color_scheme('classic')
        surface.fill(colors['background'])  # 填充背景色

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

        # 绘制游戏结束界面
        if self.game_over:
            self._draw_game_over(surface)

        # 绘制性能监控
        self.performance_monitor.draw_stats(surface)

    def _draw_grid(self, surface, grid_color):
        """绘制网格线（调试用）"""
        # 可以通过配置开关控制是否显示网格
        show_grid = True  # 设置为True可显示网格
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
        # 绘制分数
        score_text = self.font_manager.render_text(f"分数: {self.score}", 'score', text_color)
        surface.blit(score_text, (10, 10))

        # 绘制最高分
        high_score_text = self.font_manager.render_text(f"最高分: {self.high_score}", 'score', text_color)
        surface.blit(high_score_text, (10, 50))

        # 绘制蛇的长度
        length_text = self.font_manager.render_text(f"长度: {self.snake.get_length()}", 'score', text_color)
        surface.blit(length_text, (10, 90))

        # 绘制难度信息
        difficulty_color = self._get_difficulty_color()
        difficulty_text = self.font_manager.render_text(f"难度: {self.difficulty_config['name']}", 'medium',
                                                        difficulty_color)
        surface.blit(difficulty_text, (10, 130))

        # 绘制速度信息
        current_speed = self.snake.get_current_speed()
        speed_text = self.font_manager.render_text(f"速度: {current_speed:.0f}", 'medium', text_color)
        surface.blit(speed_text, (10, 160))

        # 绘制加速状态
        if self.snake.is_boost_active():
            boost_text = self.font_manager.render_text("🚀 加速中", 'medium', (255, 255, 0))
            surface.blit(boost_text, (10, 190))

        # 绘制控制提示
        help_texts = [
            "F1: 性能监控",
            "F2: 动态速度",
            "F3: 碰撞调试",
            "F4: 碰撞日志",
            "方向键: 移动",
            "空格键: 加速"
        ]

        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 'small', (150, 150, 150))
            surface.blit(help_surface, (self.screen_width - 150, 10 + i * 20))

    def _draw_game_over(self, surface):
        """绘制游戏结束界面"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # 游戏结束文本
        game_over_text = self.font_manager.render_text("游戏结束", 'title', (255, 255, 255))
        text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        surface.blit(game_over_text, text_rect)

        # 最终分数
        final_score_text = self.font_manager.render_text(f"最终得分: {self.score}", 'xlarge', (255, 255, 255))
        score_rect = final_score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 10))
        surface.blit(final_score_text, score_rect)

        # 重新开始提示
        restart_text = self.font_manager.render_text("按 R 重新开始", 'large', (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 70))
        surface.blit(restart_text, restart_rect)

    def _get_difficulty_color(self):
        """根据难度获取颜色"""
        difficulty_colors = {
            'entertainment': (100, 255, 100),  # 绿色
            'hard': (255, 255, 100),  # 黄色
            'nightmare': (255, 100, 100)  # 红色
        }
        return difficulty_colors.get(self.difficulty_config['key'], (255, 255, 255))

    def restart_game(self):
        """重新开始游戏"""
        # 重新设置蛇的初始位置
        if self.json_config:
            initial_pos = self.difficulty_loader.get_snake_initial_position(self.json_config)
        else:
            initial_pos = GridUtils.align_to_grid(*GameBalance.INITIAL_POSITION)

        self.snake.reset(initial_pos)

        # 重新应用JSON配置
        self._apply_json_config()

        # 重置食物管理器
        self.food_manager.reset()

        # 重新设置墙壁
        self.wall_manager.clear_walls()
        self._setup_walls()

        self.score = 0
        self.game_over = False
        self.last_time = pygame.time.get_ticks()
        self.performance_monitor.reset_stats()
        print(f"游戏重新开始 - 难度: {self.difficulty_config.get('name', '默认')}")
