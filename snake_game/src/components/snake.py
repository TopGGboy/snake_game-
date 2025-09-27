"""
优化后的蛇类定义
"""
import os
import json
from typing import List, Tuple, Optional
from enum import Enum

import pygame
from ..utils import tools
from ..utils.grid_utils import GridUtils
from ..configs.config import Config
from ..configs.game_balance import GameBalance


class Direction(Enum):
    """方向枚举"""
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"


class SnakeConfig:
    """蛇的配置类"""

    def __init__(self):
        # 基础配置
        self.head_size = GameBalance.SNAKE_HEAD_SIZE
        self.body_size = GameBalance.SNAKE_BODY_SIZE
        self.initial_body_segments = GameBalance.INITIAL_BODY_SEGMENTS

        # 完全顺滑移动配置
        self.move_speed = 120.0  # 像素/秒 - 蛇的移动速度
        self.turn_speed = 180.0  # 度/秒 - 转向速度
        self.segment_distance = 20.0  # 身体段之间的距离
        self.collision_radius = 12.0  # 碰撞检测半径

        # 控制响应性
        self.max_turn_angle = 90.0  # 每秒最大转向角度
        self.smooth_turning = True  # 启用平滑转向


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
        """加载并预处理所有方向的图片"""
        from ..utils.image_manager import get_image_manager

        manager = get_image_manager()

        # 获取头部和身体图片（图片应该已经在游戏初始化时预加载了）
        original_head = manager.get_snake_head(self.name, self.config.head_size)
        self.body_image = manager.get_snake_body(self.name, self.config.body_size)

        if original_head is None or self.body_image is None:
            print(f"警告: 无法加载蛇 {self.name} 的图片，使用默认图片")
            # 使用备用方案
            original_head = tools.create_default_image(self.config.head_size, (0, 255, 0))
            self.body_image = tools.create_default_image(self.config.body_size, (0, 200, 0))

        # 预加载所有方向的头部图片
        self.head_images = {
            Direction.LEFT: original_head,
            Direction.RIGHT: pygame.transform.rotate(original_head, 180),
            Direction.UP: pygame.transform.rotate(original_head, -90),
            Direction.DOWN: pygame.transform.rotate(original_head, 90)
        }

        print(f"图片加载完成 - 头部: {original_head.get_size()}, 身体: {self.body_image.get_size()}")

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

        # 设置头部图片和rect
        self.head_image = self.head_images[Direction.RIGHT]
        self.rect = self.head_image.get_rect()
        self.rect.center = (int(self.position[0]), int(self.position[1]))

        # 输入状态
        self.input_direction = [0, 0]  # [x, y] 输入方向

        print(f"蛇头初始位置: {initial_pos}")

    def _setup_body_segments(self) -> None:
        """初始化身体段"""
        self.body_segments: List[List[float]] = []  # 身体段位置 [x, y]

        # 根据初始位置和段间距离创建身体段
        for i in range(self.config.initial_body_segments):
            segment_x = self.position[0] - (i + 1) * self.config.segment_distance
            segment_y = self.position[1]
            self.body_segments.append([segment_x, segment_y])

        # 路径追踪 - 记录蛇头的移动轨迹供身体段跟随
        self.path_points: List[Tuple[float, float]] = []
        self.path_distances: List[float] = []  # 累积距离
        self.total_path_length = 0.0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """处理键盘输入 - 支持连续方向控制"""
        # 重置输入方向
        self.input_direction = [0, 0]

        # 检查按键状态
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.input_direction[0] -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.input_direction[0] += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.input_direction[1] -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.input_direction[1] += 1

        # 计算目标角度并开始移动
        if self.input_direction[0] != 0 or self.input_direction[1] != 0:
            import math
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
        self._update_smooth_movement(dt_seconds)

    def _update_smooth_movement(self, dt_seconds: float) -> None:
        """更新完全顺滑的移动"""
        import math

        # 只有在开始移动后才更新
        if not self.is_moving:
            return

        # 1. 更新角度（平滑转向）
        if self.config.smooth_turning:
            angle_diff = self._get_angle_difference(self.target_angle, self.angle)
            max_turn = self.config.turn_speed * dt_seconds

            if abs(angle_diff) > max_turn:
                # 限制转向速度
                turn_direction = 1 if angle_diff > 0 else -1
                self.angle += turn_direction * max_turn
            else:
                # 直接到达目标角度
                self.angle = self.target_angle
        else:
            self.angle = self.target_angle

        # 标准化角度
        self.angle = self._normalize_angle(self.angle)

        # 2. 计算速度向量
        angle_rad = math.radians(self.angle)
        speed = self.config.move_speed
        self.velocity[0] = math.cos(angle_rad) * speed
        self.velocity[1] = math.sin(angle_rad) * speed

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
            max_path_length = len(self.body_segments) * self.config.segment_distance * 2
            while (self.path_distances and
                   self.total_path_length - self.path_distances[0] > max_path_length):
                self.path_points.pop(0)
                self.path_distances.pop(0)

    def _update_head_image(self) -> None:
        """根据当前角度更新头部图片"""
        # 根据角度选择最接近的方向
        normalized_angle = self.angle % 360

        if -45 <= normalized_angle <= 45 or 315 <= normalized_angle <= 360:
            direction = Direction.RIGHT
        elif 45 < normalized_angle < 135:
            direction = Direction.DOWN
        elif 135 <= normalized_angle <= 225:
            direction = Direction.LEFT
        else:  # 225 < angle < 315
            direction = Direction.UP

        self.head_image = self.head_images[direction]

    def _update_body_segments_smooth(self) -> None:
        """更新身体段位置（完全顺滑模式）"""
        if not self.body_segments:
            return

        # 如果路径点不足，使用简单跟随
        if len(self.path_points) < 2:
            # 简单的直线跟随
            for i, segment in enumerate(self.body_segments):
                distance = (i + 1) * self.config.segment_distance
                # 计算反向方向
                import math
                angle_rad = math.radians(self.angle + 180)  # 反向
                segment[0] = self.position[0] + math.cos(angle_rad) * distance
                segment[1] = self.position[1] + math.sin(angle_rad) * distance
            return

        # 为每个身体段计算在路径上的位置
        for i, segment in enumerate(self.body_segments):
            # 计算该段应该距离头部的距离
            target_distance = (i + 1) * self.config.segment_distance

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
            new_x = self.position[0] - self.config.segment_distance
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

    def draw(self, surface: pygame.Surface) -> None:
        """绘制蛇"""
        # 绘制身体段
        for segment in self.body_segments:
            body_rect = self.body_image.get_rect()
            body_rect.center = (int(segment[0]), int(segment[1]))
            surface.blit(self.body_image, body_rect)

        # 绘制头部
        head_rect = self.head_image.get_rect()
        head_rect.center = (int(self.position[0]), int(self.position[1]))
        surface.blit(self.head_image, head_rect)

    def reset(self, initial_pos: Tuple[int, int] = (400, 300)) -> None:
        """重置蛇到初始状态"""
        self._setup_initial_state(initial_pos)
        self._setup_body_segments()
        print(f"蛇 {self.name} 已重置到位置: {initial_pos}")
