"""
图片管理器 - 统一管理游戏中的所有图片资源
"""
import os
import pygame
from typing import Dict, Optional
from .tools import process_game_image


class ImageManager:
    """
    图片管理器 - 采用三步处理法管理所有游戏图片
    1. 抠出主体部分
    2. 标准化到64x64
    3. 根据需求缩放到目标尺寸
    """

    def __init__(self, standard_size: int = 64):
        self.standard_size = standard_size
        self.standard_images: Dict[str, pygame.Surface] = {}  # 标准化图片缓存
        self.processed_images: Dict[str, pygame.Surface] = {}  # 处理后图片缓存

    def load_standard_image(self, image_key: str, image_path: str, colorkey: tuple = (255, 255, 255)) -> bool:
        """
        加载并标准化图片到64x64
        
        Args:
            image_key: str - 图片标识符
            image_path: str - 图片路径
            colorkey: tuple - 背景色
            
        Returns:
            bool - 是否加载成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"图片文件不存在: {image_path}")
                return False

            # 确保pygame已初始化
            if not pygame.get_init():
                pygame.init()

            # 使用完整的图片处理流程
            try:
                # 使用工具函数进行完整的图片处理
                from .tools import process_game_image

                # 处理图片：抠图 + 标准化尺寸
                standard_image = process_game_image(image_path, self.standard_size, colorkey)

                if standard_image:
                    self.standard_images[image_key] = standard_image
                    print(f"标准化图片加载成功: {image_key} -> {self.standard_size}x{self.standard_size}")
                    return True
                else:
                    print(f"图片处理失败: {image_key}")
                    return False

            except Exception as e:
                print(f"图片处理时出错 {image_path}: {e}")
                return False

        except Exception as e:
            print(f"加载图片时出错 {image_path}: {e}")
            return False

    def get_image(self, image_key: str, target_size: int) -> Optional[pygame.Surface]:
        """
        获取指定尺寸的图片
        
        Args:
            image_key: str - 图片标识符
            target_size: int - 目标尺寸
            
        Returns:
            pygame.Surface - 处理后的图片，失败返回None
        """
        # 生成缓存键
        cache_key = f"{image_key}_{target_size}"

        # 检查缓存
        if cache_key in self.processed_images:
            return self.processed_images[cache_key]

        # 检查是否有标准化图片
        if image_key not in self.standard_images:
            print(f"未找到标准化图片: {image_key}")
            return None

        # 从标准化图片缩放到目标尺寸
        standard_image = self.standard_images[image_key]
        target_image = pygame.transform.scale(standard_image, (target_size, target_size))

        # 缓存结果
        self.processed_images[cache_key] = target_image

        return target_image

    def preload_snake_images(self, snake_name: str) -> bool:
        """
        预加载蛇的所有图片
        
        Args:
            snake_name: str - 蛇的名称
            
        Returns:
            bool - 是否全部加载成功
        """
        success = True

        # 加载蛇头
        head_path = os.path.join('assets', 'graphics', 'snake', snake_name, f'{snake_name}_head.png')
        if not self.load_standard_image(f"{snake_name}_head", head_path):
            success = False

        # # 加载蛇身（可能有多个身体段图片）
        # for i in range(5):  # 尝试加载body0到body4
        #     body_path = os.path.join('assets', 'graphics', 'snake', snake_name, f'{snake_name}_body{i}.png')
        #     if os.path.exists(body_path):
        #         self.load_standard_image(f"{snake_name}_body{i}", body_path)
        #     elif i == 0:  # 至少需要body0
        #         success = False

        return success

    def preload_food_images(self) -> bool:
        """
        预加载食物图片
        
        Returns:
            bool - 是否加载成功
        """
        food_path = os.path.join('assets', 'graphics', 'food', 'food0.png')
        return self.load_standard_image('food0', food_path)

    def get_snake_head(self, snake_name: str, size: int) -> Optional[pygame.Surface]:
        """获取蛇头图片"""
        image_key = f"{snake_name}_head"

        # 如果图片未加载，尝试懒加载
        if image_key not in self.standard_images:
            print(f"懒加载蛇头图片: {snake_name}")
            head_path = os.path.join('assets', 'graphics', 'snake', snake_name, f'{snake_name}_head.png')
            self.load_standard_image(image_key, head_path)

        return self.get_image(image_key, size)

    def get_snake_body(self, snake_name: str, size: int, segment_index: int = 0) -> Optional[pygame.Surface]:
        """获取蛇身图片"""
        image_key = f"{snake_name}_body{segment_index}"

        # 如果图片未加载，尝试懒加载
        if image_key not in self.standard_images:
            print(f"懒加载蛇身图片: {snake_name}_body{segment_index}")
            body_path = os.path.join('assets', 'graphics', 'snake', snake_name, f'{snake_name}_body{segment_index}.png')
            if os.path.exists(body_path):
                self.load_standard_image(image_key, body_path)

        return self.get_image(image_key, size)

    def get_food(self, food_name: str, size: int) -> Optional[pygame.Surface]:
        """获取食物图片"""
        # 如果图片未加载，尝试懒加载
        if food_name not in self.standard_images:
            print(f"懒加载食物图片: {food_name}")
            food_path = os.path.join('assets', 'graphics', 'food', f'{food_name}.png')
            if os.path.exists(food_path):
                self.load_standard_image(food_name, food_path)

        return self.get_image(food_name, size)

    def clear_cache(self):
        """清空缓存"""
        self.processed_images.clear()
        print("图片缓存已清空")

    def get_cache_info(self) -> dict:
        """获取缓存信息"""
        return {
            'standard_images': len(self.standard_images),  # 标准图片缓存数量
            'processed_images': len(self.processed_images),  # 处理图片缓存数量
            'standard_size': self.standard_size  # 标准图片尺寸
        }


# 全局图片管理器实例
_image_manager = None


def get_image_manager() -> ImageManager:
    """获取全局图片管理器实例"""
    global _image_manager
    if _image_manager is None:
        _image_manager = ImageManager()
    return _image_manager


def initialize_game_images():
    """初始化游戏所需的所有图片"""
    manager = get_image_manager()

    print("开始加载游戏图片...")

    # 加载蛇的图片
    snake_success = manager.preload_snake_images('snake0')

    # 加载食物图片
    food_success = manager.preload_food_images()

    # 输出加载结果
    cache_info = manager.get_cache_info()
    print(f"图片加载完成:")
    print(f"  标准化图片: {cache_info['standard_images']} 个")
    print(f"  标准尺寸: {cache_info['standard_size']}x{cache_info['standard_size']}")
    print(f"  蛇图片: {'成功' if snake_success else '失败'}")
    print(f"  食物图片: {'成功' if food_success else '失败'}")

    return snake_success and food_success
