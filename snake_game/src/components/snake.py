"""
优化后的蛇类定义
"""
import os
import json
from typing import List, Tuple, Optional
from enum import Enum

import pygame
from ..utils import tools
from ..configs.config import Config


class Direction(Enum):
    """方向枚举"""
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"


class SnakeConfig:
    """蛇的配置类"""
    def __init__(self):
        self.head_size = 48
        self.body_size = 86
        self.move_speed = 20
        self.move_delay = 300
        self.initial_body_segments = 3
        self.collision_threshold_ratio = 0.2
        
    @classmethod
    def from_json(cls, json_path: str) -> 'SnakeConfig':
        """从JSON文件加载配置"""
        config = cls()
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    config.head_size = data.get('head_size', config.head_size)
                    config.body_size = data.get('body_size', config.body_size)
                    config.move_speed = data.get('move_speed', config.move_speed)
                    config.move_delay = data.get('move_delay', config.move_delay)
                    config.initial_body_segments = data.get('initial_body_segments', config.initial_body_segments)
            except (json.JSONDecodeError, IOError) as e:
                print(f"配置文件加载失败，使用默认配置: {e}")
        return config


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
        config_path = os.path.join('src/data/snakes', f'{self.name}.json')
        return SnakeConfig.from_json(config_path)

    def _load_images(self) -> None:
        """加载并预处理所有方向的图片"""
        # 加载原始图片
        head_path = os.path.join('assets', 'graphics', 'snake', self.name, f'{self.name}_head.png')
        body_path = os.path.join('assets', 'graphics', 'snake', self.name, f'{self.name}_body0.png')
        
        original_head = tools.process_snake_image(
            head_path, 
            colorkey=(255, 255, 255),
            target_size=self.config.head_size
        )
        
        self.body_image = tools.process_snake_image(
            body_path,
            colorkey=(255, 255, 255), 
            target_size=self.config.body_size
        )
        
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
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT  # 缓存下一个方向，避免快速按键导致的问题
        self.is_dead = False
        
        # 设置头部位置
        self.head_image = self.head_images[self.direction]
        self.rect = self.head_image.get_rect()
        self.rect.center = initial_pos
        
        # 移动相关
        self.move_timer = 0
        
    def _setup_body_segments(self) -> None:
        """初始化身体段"""
        self.body_segments: List[List[int]] = []
        
        # 根据初始方向和移动步长计算身体段位置
        for i in range(self.config.initial_body_segments):
            segment_x = self.rect.centerx - (i + 1) * self.config.move_speed
            segment_y = self.rect.centery
            self.body_segments.append([segment_x, segment_y])

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """处理键盘输入，使用缓存机制避免快速按键问题"""
        direction_map = {
            pygame.K_UP: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT
        }
        
        for key, new_direction in direction_map.items():
            if keys[key] and self._is_valid_direction_change(new_direction):
                self.next_direction = new_direction
                break

    def _is_valid_direction_change(self, new_direction: Direction) -> bool:
        """检查方向改变是否有效（防止反向移动）"""
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return new_direction != opposite_directions.get(self.direction)

    def update(self, dt: int) -> None:
        """更新蛇的状态"""
        if self.is_dead:
            return
            
        self.move_timer += dt
        
        if self.move_timer >= self.config.move_delay:
            self._move()
            self.move_timer = 0

    def _move(self) -> None:
        """移动蛇"""
        # 应用缓存的方向改变
        if self.next_direction != self.direction:
            self.direction = self.next_direction
            self.head_image = self.head_images[self.direction]
            
            # 更新rect保持位置
            old_center = self.rect.center
            self.rect = self.head_image.get_rect()
            self.rect.center = old_center
        
        # 保存当前头部位置
        old_head_center = [self.rect.centerx, self.rect.centery]
        
        # 移动头部
        direction_vectors = {
            Direction.RIGHT: (self.config.move_speed, 0),
            Direction.LEFT: (-self.config.move_speed, 0),
            Direction.UP: (0, -self.config.move_speed),
            Direction.DOWN: (0, self.config.move_speed)
        }
        
        dx, dy = direction_vectors[self.direction]
        self.rect.centerx += dx
        self.rect.centery += dy
        
        # 更新身体段
        self._update_body_segments(old_head_center)

    def _update_body_segments(self, old_head_center: List[int]) -> None:
        """更新身体段位置"""
        if not self.body_segments:
            return
            
        # 从尾部开始，每个段移动到前一个段的位置
        for i in range(len(self.body_segments) - 1, 0, -1):
            self.body_segments[i][0] = self.body_segments[i - 1][0]
            self.body_segments[i][1] = self.body_segments[i - 1][1]
        
        # 第一个身体段移动到头部的旧位置
        self.body_segments[0][0] = old_head_center[0]
        self.body_segments[0][1] = old_head_center[1]

    def grow(self) -> None:
        """增长蛇的身体"""
        if self.body_segments:
            # 在尾部添加新段
            tail = self.body_segments[-1]
            self.body_segments.append([tail[0], tail[1]])
        else:
            # 如果没有身体段，在头部后面添加
            self.body_segments.append([
                self.rect.centerx - self.config.move_speed,
                self.rect.centery
            ])

    def check_self_collision(self) -> bool:
        """检查是否撞到自己"""
        if len(self.body_segments) < 2:
            return False
            
        head_center = (self.rect.centerx, self.rect.centery)
        collision_threshold = int(self.config.body_size * self.config.collision_threshold_ratio)
        
        # 从第二节开始检查（跳过紧邻头部的第一节）
        for segment in self.body_segments[1:]:
            dx = abs(head_center[0] - segment[0])
            dy = abs(head_center[1] - segment[1])
            
            if dx < collision_threshold and dy < collision_threshold:
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
        return (self.rect.centerx, self.rect.centery)

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
        surface.blit(self.head_image, self.rect)

    def reset(self, initial_pos: Tuple[int, int] = (400, 300)) -> None:
        """重置蛇到初始状态"""
        self._setup_initial_state(initial_pos)
        self._setup_body_segments()
        print(f"蛇 {self.name} 已重置")