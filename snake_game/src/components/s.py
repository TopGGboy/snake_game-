"""
蛇类定义
"""
import os
import json

import pygame
from ..utils import tools


class Snake(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        # 加载头部和身体图片
        self.head_image = None
        self.body_image = None
        self.head_size = 48
        self.body_size = 86
        self.load_images()

        # 先设置状态和朝向
        self.setup_states()
        self.setup_velocities()
        self.setup_timers()

        # 初始化位置和身体列表（使用旋转后的头部图片）
        self.rect = self.head_image.get_rect()
        self.rect.center = (400, 300)  # 使用中心点设置初始位置

        # 初始化头部方向 - 确保蛇头朝向正确（必须在rect创建后调用）
        self.update_head_rotation()

        # 身体部分 - 存储每个身体段的中心位置
        self.body_segments = []

        # 初始化几个身体段，使用中心点对齐
        # 根据移动步长调整间距，确保身体段不重叠
        segment_spacing = self.vel  # 使用移动步长作为间距，确保连续性

        for i in range(3):  # 初始3个身体段
            # 根据初始朝向（向右）计算身体段位置
            body_center_x = self.rect.centerx - (i + 1) * segment_spacing
            body_center_y = self.rect.centery
            self.body_segments.append([body_center_x, body_center_y])

        # 调试信息：打印图片尺寸
        print(f"蛇 {self.name} 图片加载完成:")
        print(f"  头部图片尺寸: {self.head_image.get_size()}")
        print(f"  身体图片尺寸: {self.body_image.get_size()}")

    # 加载头部和身体图片
    def load_images(self):
        # 加载并处理头部图片：移除背景，裁剪主元素，缩放到合适大小
        head_image_path = os.path.join('assets', 'graphics', 'snake', self.name, f'{self.name}_head.png')
        self.original_head_image = tools.process_snake_image(head_image_path, colorkey=(255, 255, 255),
                                                             target_size=self.head_size)
        self.head_image = self.original_head_image  # 当前显示的头部图片

        # 加载并处理身体图片：移除背景，裁剪主元素，缩放到合适大小
        body_image_path = os.path.join('assets', 'graphics', 'snake', self.name, f'{self.name}_body0.png')
        self.body_image = tools.process_snake_image(body_image_path, colorkey=(255, 255, 255),
                                                    target_size=self.body_size)

    def update_head_rotation(self):
        """
        根据移动方向旋转蛇头
        """
        if self.face == "R":
            # 向右：旋转180度（因为原图朝左）
            self.head_image = pygame.transform.rotate(self.original_head_image, 180)
        elif self.face == "L":
            # 向左：不旋转（原图就是朝左）
            self.head_image = self.original_head_image
        elif self.face == "U":
            # 向上：旋转-90度（修正方向）
            self.head_image = pygame.transform.rotate(self.original_head_image, -90)
        elif self.face == "D":
            # 向下：旋转90度（修正方向）
            self.head_image = pygame.transform.rotate(self.original_head_image, 90)

        # 更新rect以保持位置正确（仅在rect已存在时）
        if hasattr(self, 'rect'):
            old_center = self.rect.center
            self.rect = self.head_image.get_rect()
            self.rect.center = old_center

    # 加载小蛇数据
    def load_data(self):
        file_name = self.name + '.json'
        file_path = os.path.join('snake_game/src/data/snakes', file_name)
        with open(file_path) as f:
            self.snake_data = json.load(f)

    # 小蛇初始化状态
    def setup_states(self):
        self.face = "R"  # 初始朝向右
        self.dead = False

    # 设置小蛇速度
    def setup_velocities(self):
        self.vel = 20  # 设置移动步长，与身体段间距一致
        self.move_timer = 0
        self.move_delay = 300  # 移动间隔（毫秒），稍微慢一点更容易控制

    # 设置计时器
    def setup_timers(self):
        self.walking_time = 0

    # 处理键盘输入，控制蛇的移动方向
    def handle_input(self, keys):
        """
        处理键盘输入，控制蛇的移动方向
        """
        # 防止蛇反向移动（避免直接撞到自己的身体）
        if keys[pygame.K_UP] and self.face != "D":
            self.face = "U"
        elif keys[pygame.K_DOWN] and self.face != "U":
            self.face = "D"
        elif keys[pygame.K_LEFT] and self.face != "R":
            self.face = "L"
        elif keys[pygame.K_RIGHT] and self.face != "L":
            self.face = "R"

        self.update_head_rotation()

    # 绘制蛇
    def draw(self, surface):
        # 先绘制身体部分 - 使用中心点定位
        for segment in self.body_segments:
            body_rect = self.body_image.get_rect()
            body_rect.center = (int(segment[0]), int(segment[1]))
            surface.blit(self.body_image, body_rect)

        # 最后绘制头部，确保头部在最上层
        surface.blit(self.head_image, self.rect)

    # 更新蛇的位置
    def update(self, dt):
        self.move_timer += dt

        # 只在达到移动间隔时才移动
        if self.move_timer >= self.move_delay:
            # 保存当前头部中心位置
            old_head_center = [self.rect.centerx, self.rect.centery]

            # 根据朝向移动头部中心点
            if self.face == "R":
                self.rect.centerx += self.vel
            elif self.face == "L":
                self.rect.centerx -= self.vel
            elif self.face == "U":
                self.rect.centery -= self.vel
            elif self.face == "D":
                self.rect.centery += self.vel

            # 更新身体段位置 - 每个段移动到前一个段的中心位置
            if self.body_segments:
                # 从尾部开始，每个段移动到前一个段的位置
                for i in range(len(self.body_segments) - 1, 0, -1):
                    self.body_segments[i][0] = self.body_segments[i - 1][0]
                    self.body_segments[i][1] = self.body_segments[i - 1][1]

                # 第一个身体段移动到头部的旧中心位置
                self.body_segments[0][0] = old_head_center[0]
                self.body_segments[0][1] = old_head_center[1]

            # 重置移动计时器
            self.move_timer = 0

    def grow(self):
        """
        增长蛇的身体（当吃到食物时调用）
        """
        if self.body_segments:
            # 在尾部添加一个新的身体段，使用中心位置
            tail = self.body_segments[-1]
            new_segment = [tail[0], tail[1]]
            self.body_segments.append(new_segment)
        else:
            # 如果没有身体段，在头部后面添加一个，使用中心位置
            segment_spacing = 45
            new_segment = [self.rect.centerx - segment_spacing, self.rect.centery]
            self.body_segments.append(new_segment)

    def check_self_collision(self):
        """
        检查蛇是否撞到自己（使用中心点碰撞检测）
        """
        head_center = (self.rect.centerx, self.rect.centery)
        # 使用身体尺寸作为碰撞检测阈值，使蛇头的碰撞高度与身体一致
        collision_threshold = int(self.body_size * 0.2)  # 碰撞检测阈值，基于身体尺寸调整

        # 从第二节身体开始检查（跳过第一节与头部相连的部分）
        for i in range(1, len(self.body_segments)):
            segment = self.body_segments[i]
            # 计算头部中心和身体段中心的距离
            dx = abs(head_center[0] - segment[0])
            dy = abs(head_center[1] - segment[1])

            # 如果距离小于阈值，认为发生碰撞
            if dx < collision_threshold and dy < collision_threshold:
                return True
        return False
