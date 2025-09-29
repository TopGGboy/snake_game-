"""
优化后的蛇类定义
"""
import os
import json
from typing import List, Tuple, Optional
from enum import Enum

import pygame
import math
from ..utils import tools
from ..utils.grid_utils import GridUtils
from ..configs.config import Config
from ..configs.game_balance import GameBalance
from ..utils.image_manager import get_image_manager


class SnakeConfig:
    """蛇的配置类"""

    def __init__(self):
        # 基础配置
        self.head_size = GameBalance.SNAKE_HEAD_SIZE  # 蛇的尺寸
        self.body_size = GameBalance.SNAKE_BODY_SIZE  # 蛇身体段的尺寸
        self.initial_body_segments = GameBalance.INITIAL_BODY_SEGMENTS  # 蛇的初始身体段数

        # 完全顺滑移动配置 - 从GameBalance获取
        self.move_speed = GameBalance.SMOOTH_MOVE_SPEED  # 蛇的移动速度
        self.turn_speed = GameBalance.SMOOTH_TURN_SPEED  # 蛇的转向速度
        self.segment_distance = GameBalance.SMOOTH_SEGMENT_DISTANCE  # 身体段之间的距离
        self.collision_radius = GameBalance.SMOOTH_COLLISION_RADIUS  # 碰撞检测半径
        self.max_turn_angle = GameBalance.SMOOTH_MAX_TURN_ANGLE  # 每秒最大转向角度
        self.smooth_turning = GameBalance.SMOOTH_TURNING_ENABLED  # 启用平滑转向

        # 加速配置
        self.boost_multiplier = GameBalance.SMOOTH_BOOST_MULTIPLIER


class Snake(pygame.sprite.Sprite):
    """优化后的蛇类"""

    def __init__(self, name: str, initial_pos: Tuple[int, int] = (400, 300)):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.config = self._load_config()

        # 加载图片资源
        self._load_images()

        # 初始化状态
        self._setup_initial_state(initial_pos)

        # 初始化身体段
        self._setup_body_segments()

        print(f"蛇 {self.name} 初始化完成")

    def _load_config(self) -> SnakeConfig:
        """加载蛇的配置"""
        return SnakeConfig()

    def _load_images(self) -> None:
        """加载并预处理所有方向的图"""
        manager = get_image_manager()

        # 获取头部和身体图片（图片应该已经在游戏初始化时预加载了）
        original_head = manager.get_snake_head(self.name, self.config.head_size)
        # self.body_image = manager.get_snake_body(self.name, self.config.body_size)
        self.body_image = ''

        if original_head is None or self.body_image is None:
            print(f"警告: 无法加载蛇 {self.name} 的图片，使用默认图片")
            # 使用备用方案
            original_head = tools.create_default_image(self.config.head_size, (0, 255, 0))
            # self.body_image = tools.create_default_image(self.config.body_size, (0, 200, 0))

        # 创建角度图片缓存（每15度一个，统一的图片系统）
        # 原始图片朝左（180度），所以需要调整旋转角度
        self.angle_images = {}
        for angle in range(0, 360, 15):  # 每15度创建一个图片
            # 原始图片是180度（朝左），所以实际旋转角度需要减去180度
            rotation_angle = -(angle - 180)
            rotated_image = pygame.transform.rotate(original_head, rotation_angle)
            self.angle_images[angle] = rotated_image

        print(f"图片加载完成 - 头部: {original_head.get_size()}")
        print(f"角度图片: {len(self.angle_images)}个 (每15度)")

    def _setup_initial_state(self, initial_pos: Tuple[int, int]) -> None:
        """设置初始状态"""
        self.is_dead = False

        # 完全顺滑移动 - 使用浮点坐标和角度
        self.position = [float(initial_pos[0]), float(initial_pos[1])]  # 当前位置
        self.angle = 0.0  # 当前角度（度），0度为向右
        self.target_angle = 0.0  # 目标角度

        # 速度向量 - 初始静止
        self.velocity = [0.0, 0.0]  # [vx, vy]
        self.is_moving = False  # 是否开始移动

        # 加速功能
        self.is_boosting = False  # 是否正在加速
        self.boost_multiplier = self.config.boost_multiplier  # 加速倍数
        self.normal_speed = self.config.move_speed  # 保存正常速度
        self.boost_speed = self.normal_speed * self.boost_multiplier  # 加速后的速度

        # 蛇身颜色配置
        self.body_colors = {
            'normal': {
                'fill': (255, 215, 0),  # 金黄色（如图片）
                'border': (218, 165, 32),  # 深金色边框
                'highlight': (255, 255, 224)  # 浅黄高光
            },
            'boost': {
                'fill': (255, 215, 0),  # 金黄色
                'border': (255, 140, 0),  # 深橙色边框
                'highlight': (255, 255, 224)  # 浅黄高光
            }
        }
        self.body_radius = self.config.body_size // 2  # 蛇身圆圈半径

        # 动画效果
        self.animation_time = 0.0  # 动画时间计数器
        self.pulse_speed = 3.0  # 脉动速度

        # 渲染选项 - 简化为固定大小
        self.use_connections = True  # 是否绘制连接线段

        # 设置头部图片和rect（初始朝右，即0度）
        self.head_image = self.angle_images[0]
        self.rect = self.head_image.get_rect()
        self.rect.center = (int(self.position[0]), int(self.position[1]))

        # 输入状态
        self.input_direction = [0, 0]  # [x, y] 输入方向

        print(f"蛇头初始位置: {initial_pos}")

    def _get_runtime_segment_distance(self) -> float:
        """获取运行时使用的身体段间距，确保所有地方使用相同的计算方式"""
        return self.body_radius * 1.6

    def _setup_body_segments(self) -> None:
        """初始化身体段"""
        self.body_segments: List[List[float]] = []  # 身体段位置 [x, y]

        # 根据初始位置和段间距离创建身体段
        # 使用与运行时相同的间距计算方式，确保一致性
        runtime_segment_distance = self._get_runtime_segment_distance()

        for i in range(self.config.initial_body_segments):
            segment_x = self.position[0] - (i + 1) * runtime_segment_distance
            segment_y = self.position[1]
            self.body_segments.append([segment_x, segment_y])

        # 路径追踪 - 记录蛇头的移动轨迹供身体段跟随
        self.path_points: List[Tuple[float, float]] = []
        self.path_distances: List[float] = []  # 累积距离
        self.total_path_length = 0.0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """处理键盘输入 - 支持连续方向控制和加速"""
        # 重置输入方向
        self.input_direction = [0, 0]

        # 检查方向按键状态
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.input_direction[0] -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.input_direction[0] += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.input_direction[1] -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.input_direction[1] += 1

        # 检查加速按键（空格键）
        self.is_boosting = keys[pygame.K_SPACE]

        # 计算目标角度并开始移动
        if self.input_direction[0] != 0 or self.input_direction[1] != 0:
            self.target_angle = math.degrees(math.atan2(self.input_direction[1], self.input_direction[0]))
            self.is_moving = True  # 开始移动

    def _normalize_angle(self, angle: float) -> float:
        """标准化角度到 -180 到 180 度范围"""
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle

    def _get_angle_difference(self, target: float, current: float) -> float:
        """计算两个角度之间的最短差值"""
        diff = target - current
        return self._normalize_angle(diff)

    def update(self, dt: int) -> None:
        """更新蛇的状态"""
        if self.is_dead:
            return

        dt_seconds = dt / 1000.0

        # 更新动画时间
        self.animation_time += dt_seconds

        self._update_smooth_movement(dt_seconds)

    def _update_smooth_movement(self, dt_seconds: float) -> None:
        """更新完全顺滑的移动"""
        # 只有在开始移动后才更新
        if not self.is_moving:
            return

        # 1. 更新角度（优化的平滑转向）
        if self.config.smooth_turning:
            angle_diff = self._get_angle_difference(self.target_angle, self.angle)
            
            # 自适应转向速度：角度差越大，转向越快
            base_turn_speed = self.config.turn_speed
            adaptive_multiplier = min(2.0, 1.0 + abs(angle_diff) / 90.0)  # 最大2倍速度
            adaptive_turn_speed = base_turn_speed * adaptive_multiplier
            
            max_turn = adaptive_turn_speed * dt_seconds
            
            # 小角度直接转向，大角度渐进转向
            if abs(angle_diff) <= 15.0:  # 15度以内直接转向
                self.angle = self.target_angle
            elif abs(angle_diff) > max_turn:
                # 渐进式转向
                turn_direction = 1 if angle_diff > 0 else -1
                self.angle += turn_direction * max_turn
            else:
                # 直接到达目标角度
                self.angle = self.target_angle
        else:
            self.angle = self.target_angle

        # 标准化角度
        self.angle = self._normalize_angle(self.angle)

        # 数学原理： 使用三角函数将极坐标（角度+速度）转换为直角坐标（vx, vy）。
        # 2. 计算速度向量（根据加速状态调整速度）
        angle_rad = math.radians(self.angle)  # 将角度转换为弧度
        speed = self.boost_speed if self.is_boosting else self.normal_speed  # 根据加速状态调整速度
        self.velocity[0] = math.cos(angle_rad) * speed  # 计算x轴速度
        self.velocity[1] = math.sin(angle_rad) * speed  # 计算y轴速度

        # 3. 更新位置
        old_position = self.position.copy()
        self.position[0] += self.velocity[0] * dt_seconds
        self.position[1] += self.velocity[1] * dt_seconds

        # 4. 更新路径追踪
        self._update_path_tracking(old_position)

        # 5. 更新身体段位置
        self._update_body_segments_smooth()

        # 6. 更新头部图片方向
        self._update_head_image()

        # 7. 更新rect
        self.rect.center = (int(self.position[0]), int(self.position[1]))

    def _update_path_tracking(self, old_position: List[float]) -> None:
        """更新路径追踪"""
        # 计算移动距离
        dx = self.position[0] - old_position[0]
        dy = self.position[1] - old_position[1]
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > 0.5:  # 只有移动距离足够大时才记录
            # 添加新的路径点
            self.path_points.append((self.position[0], self.position[1]))
            self.total_path_length += distance
            self.path_distances.append(self.total_path_length)

            # 限制路径点数量，避免内存过度使用
            max_path_length = len(self.body_segments) * self._get_runtime_segment_distance() * 2
            while (self.path_distances and
                   self.total_path_length - self.path_distances[0] > max_path_length):
                self.path_points.pop(0)
                self.path_distances.pop(0)

    def _update_head_image(self) -> None:
        """根据当前角度更新头部图片"""
        normalized_angle = self.angle % 360

        # 找到最接近的15度倍数角度
        closest_angle = round(normalized_angle / 15) * 15
        closest_angle = closest_angle % 360
        self.head_image = self.angle_images[closest_angle]

    def _update_body_segments_smooth(self) -> None:
        """更新身体段位置（完全顺滑模式）- 优化连续性"""
        if not self.body_segments:
            return

        # 如果路径点不足，使用简单跟随
        if len(self.path_points) < 2:
            # 简单的直线跟随 - 使用更紧密的间距
            runtime_segment_distance = self._get_runtime_segment_distance()
            for i, segment in enumerate(self.body_segments):
                # 使用稍小的间距确保连续性
                distance = (i + 1) * runtime_segment_distance  # 约1.6倍半径的间距
                angle_rad = math.radians(self.angle + 180)  # 反向
                segment[0] = self.position[0] + math.cos(angle_rad) * distance
                segment[1] = self.position[1] + math.sin(angle_rad) * distance
            return

        # 为每个身体段计算在路径上的位置 - 使用优化的间距
        runtime_segment_distance = self._get_runtime_segment_distance()
        for i, segment in enumerate(self.body_segments):
            # 使用更紧密的间距确保连续性
            target_distance = (i + 1) * runtime_segment_distance

            # 在路径上找到对应距离的位置
            segment_pos = self._get_position_on_path(target_distance)
            if segment_pos:
                segment[0] = segment_pos[0]
                segment[1] = segment_pos[1]

    def _get_position_on_path(self, distance_from_head: float) -> Optional[Tuple[float, float]]:
        """在路径上获取距离头部指定距离的位置"""
        if not self.path_points or not self.path_distances:
            return None

        target_distance = self.total_path_length - distance_from_head

        if target_distance <= 0:
            # 距离太远，返回路径起点
            return self.path_points[0] if self.path_points else None

        # 在路径距离数组中查找位置
        for i in range(len(self.path_distances) - 1):
            if self.path_distances[i] <= target_distance <= self.path_distances[i + 1]:
                # 在两个点之间插值
                t = ((target_distance - self.path_distances[i]) /
                     (self.path_distances[i + 1] - self.path_distances[i]))

                p1 = self.path_points[i]
                p2 = self.path_points[i + 1]

                return (
                    p1[0] + (p2[0] - p1[0]) * t,
                    p1[1] + (p2[1] - p1[1]) * t
                )

        # 如果没找到，返回最后一个点
        return self.path_points[-1] if self.path_points else None

    def grow(self) -> None:
        """增长蛇的身体"""
        if self.body_segments:
            # 在尾部添加新段
            tail = self.body_segments[-1]
            self.body_segments.append([tail[0], tail[1]])
        else:
            # 如果没有身体段，在头部后面添加
            new_x = self.position[0] - self._get_runtime_segment_distance()
            new_y = self.position[1]
            self.body_segments.append([new_x, new_y])

    def check_self_collision(self) -> bool:
        """检查是否撞到自己"""
        # 只有在移动时才检查碰撞
        if not self.is_moving:
            return False

        if len(self.body_segments) < 4:  # 至少需要4个身体段才可能撞到自己
            return False

        head_center = (self.position[0], self.position[1])
        collision_threshold = self.config.collision_radius

        # 从第四节开始检查（跳过紧邻头部的前三节，避免误判）
        for segment in self.body_segments[3:]:
            segment_pos = (segment[0], segment[1])
            dx = head_center[0] - segment_pos[0]
            dy = head_center[1] - segment_pos[1]
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < collision_threshold:
                return True
        return False

    def check_boundary_collision(self, screen_width: int, screen_height: int) -> bool:
        """检查是否撞到边界"""
        return (self.rect.left < 0 or
                self.rect.right > screen_width or
                self.rect.top < 0 or
                self.rect.bottom > screen_height)

    def check_food_collision(self, food_rect: pygame.Rect) -> bool:
        """检查是否吃到食物"""
        return self.rect.colliderect(food_rect)

    def die(self) -> None:
        """蛇死亡"""
        self.is_dead = True
        print(f"蛇 {self.name} 死亡")

    def get_head_position(self) -> Tuple[int, int]:
        """获取头部位置"""
        return (int(self.position[0]), int(self.position[1]))

    def get_body_segments(self) -> List[Tuple[int, int]]:
        """获取身体段位置列表"""
        return [(int(seg[0]), int(seg[1])) for seg in self.body_segments]

    def get_length(self) -> int:
        """获取蛇的长度（包括头部）"""
        return len(self.body_segments) + 1

    def is_boost_active(self) -> bool:
        """获取当前是否正在加速"""
        return self.is_boosting

    def get_current_speed(self) -> float:
        """获取当前移动速度"""
        return self.boost_speed if self.is_boosting else self.normal_speed

    def _draw_connection(self, surface: pygame.Surface, pos1: Tuple[int, int],
                         pos2: Tuple[int, int], colors: dict, radius: int) -> None:
        """绘制两个身体段之间的连接"""
        # 计算两点之间的距离
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        distance = math.sqrt(dx * dx + dy * dy)

        # 如果距离很小，不需要连接
        if distance < radius * 1.5:
            return

        # 计算连接矩形的参数
        if distance > 0:
            # 单位向量
            ux = dx / distance
            uy = dy / distance

            # 垂直向量
            vx = -uy * radius * 0.8  # 稍微细一点
            vy = ux * radius * 0.8

            # 矩形的四个顶点
            points = [
                (pos1[0] + vx, pos1[1] + vy),
                (pos1[0] - vx, pos1[1] - vy),
                (pos2[0] - vx, pos2[1] - vy),
                (pos2[0] + vx, pos2[1] + vy)
            ]

            # 绘制连接矩形
            pygame.draw.polygon(surface, colors['fill'], points)

    def _draw_body_circle(self, surface: pygame.Surface, pos: Tuple[int, int],
                          colors: dict, radius: int, segment_index: int = 0) -> None:
        """绘制圆形蛇身段"""
        # 加速状态下的脉动效果
        if self.is_boosting:
            pulse_factor = 1.0 + 0.1 * math.sin(self.animation_time * self.pulse_speed + segment_index * 0.3)
            radius = int(radius * pulse_factor)

        # 绘制阴影效果
        shadow_pos = (pos[0] + 2, pos[1] + 2)
        pygame.draw.circle(surface, (0, 0, 0, 100), shadow_pos, radius)

        # 绘制主体圆圈
        pygame.draw.circle(surface, colors['fill'], pos, radius)

        # 绘制边框
        pygame.draw.circle(surface, colors['border'], pos, radius, 2)

        # 绘制高光效果（左上角小圆圈）
        highlight_pos = (pos[0] - radius // 3, pos[1] - radius // 3)
        highlight_radius = max(radius // 4, 2)
        pygame.draw.circle(surface, colors['highlight'], highlight_pos, highlight_radius)

        # 加速状态下的额外光环效果
        if self.is_boosting:
            # 外圈光环
            glow_radius = radius + 4
            glow_color = (255, 255, 0, 80)  # 半透明黄色
            pygame.draw.circle(surface, glow_color[:3], pos, glow_radius, 1)

    def draw(self, surface: pygame.Surface, debug_collision: bool = False) -> None:
        """绘制蛇"""
        # 根据加速状态选择颜色
        colors = self.body_colors['boost'] if self.is_boosting else self.body_colors['normal']

        # 绘制身体段（圆形）- 固定大小确保连续性
        for i, segment in enumerate(self.body_segments):
            pos = (int(segment[0]), int(segment[1]))

            # 使用统一大小确保完美连续性
            radius = self.body_radius

            # 绘制连接线段（在圆圈之前绘制，避免覆盖）
            if self.use_connections and i > 0:
                prev_pos = (int(self.body_segments[i - 1][0]), int(self.body_segments[i - 1][1]))
                self._draw_connection(surface, prev_pos, pos, colors, radius)

            # 绘制圆形身体段
            self._draw_body_circle(surface, pos, colors, radius, i)

            # 调试：绘制身体段碰撞圆圈
            if debug_collision:
                pygame.draw.circle(surface, (0, 255, 255), pos,
                                   int(self.config.collision_radius), 2)

        # 绘制头部
        head_rect = self.head_image.get_rect()
        head_rect.center = (int(self.position[0]), int(self.position[1]))
        surface.blit(self.head_image, head_rect)

        # 调试：绘制蛇头碰撞圆圈
        if debug_collision:
            pygame.draw.circle(surface, (255, 0, 0),
                               (int(self.position[0]), int(self.position[1])),
                               int(self.config.collision_radius), 3)

    def reset(self, initial_pos: Tuple[int, int] = (400, 300)) -> None:
        """重置蛇到初始状态"""
        self._setup_initial_state(initial_pos)
        self._setup_body_segments()
        self.animation_time = 0.0  # 重置动画时间
        print(f"蛇 {self.name} 已重置到位置: {initial_pos}")
