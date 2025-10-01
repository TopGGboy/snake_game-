"""
图片资源管理器
"""
import os
import pygame
from typing import Dict, Tuple, Optional, Any
from .tools import process_game_image
from ..configs.game_balance import GameBalance



class ImageManager:
    """图片资源管理器类"""

    def __init__(self):
        self.snake_images: Dict[Tuple[int, str], pygame.Surface] = {}
        self.food_images: Dict[str, pygame.Surface] = {}
        self.ui_images: Dict[str, pygame.Surface] = {}
        
        # 图片目录
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        self.snake_dir = os.path.join(self.assets_dir, "graphics", "snake")
        self.food_dir = os.path.join(self.assets_dir, "graphics", "food")
        self.ui_dir = os.path.join(self.assets_dir, "graphics", "ui")
        
        # 确保目录存在
        os.makedirs(self.snake_dir, exist_ok=True)
        os.makedirs(self.food_dir, exist_ok=True)
        os.makedirs(self.ui_dir, exist_ok=True)
        
        # 预加载所有图片（使用延迟加载，避免视频模式问题）
        self._preload_images()
        
        print("图片管理器初始化完成")

    def _preload_images(self) -> None:
        """预加载所有图片资源"""
        self._load_snake_images()
        self._load_food_images()
        self._load_ui_images()

    def _load_snake_images(self) -> None:
        """加载蛇的图片资源"""
        print("加载蛇的图片资源...")
        
        # 检查snake目录下的所有子目录
        if os.path.exists(self.snake_dir):
            for item in os.listdir(self.snake_dir):
                snake_path = os.path.join(self.snake_dir, item)
                if os.path.isdir(snake_path):
                    # 这是一个蛇皮肤目录
                    try:
                        skin_id = int(item.replace("snake", ""))
                        self._load_snake_skin(skin_id, snake_path)
                    except ValueError:
                        print(f"跳过无效的蛇皮肤目录: {item}")

    def _load_snake_skin(self, skin_id: int, skin_path: str) -> None:
        """加载特定蛇皮肤的图片"""
        print(f"加载蛇皮肤 {skin_id} 的图片...")
        
        # 加载头部图片
        head_path = os.path.join(skin_path, f"snake{skin_id}_head.png")
        if os.path.exists(head_path):
            try:
                # 处理图片： 抠图 + 标准化
                head_image = process_game_image(image_path=head_path, target_size=GameBalance.SNAKE_HEAD_SIZE)
                self.snake_images[(skin_id, "head")] = head_image
                print(f"✓ 加载蛇头图片: snake{skin_id}_head.png")
            except Exception as e:
                print(f"✗ 加载蛇头图片失败: {head_path}, 错误: {e}")
        
        # 加载身体图片
        for i in range(10):  # 最多加载10个身体图片
            body_path = os.path.join(skin_path, f"snake{skin_id}_body{i}.png")
            if os.path.exists(body_path):
                try:
                    # 处理图片： 抠图 + 标准化
                    body_image = process_game_image(image_path=body_path, target_size=GameBalance.SNAKE_BODY_SIZE)
                    self.snake_images[(skin_id, f"body{i}")] = body_image
                    print(f"✓ 加载蛇身图片: snake{skin_id}_body{i}.png")
                except Exception as e:
                    print(f"✗ 加载蛇身图片失败: {body_path}, 错误: {e}")
            else:
                break  # 没有更多身体图片

    def _load_food_images(self) -> None:
        """加载食物图片资源"""
        print("加载食物图片资源...")
        
        if os.path.exists(self.food_dir):
            for filename in os.listdir(self.food_dir):
                if filename.endswith(".png"):
                    food_name = filename.replace(".png", "")
                    food_path = os.path.join(self.food_dir, filename)
                    try:
                        # 处理图片： 抠图 + 标准化
                        food_image = process_game_image(image_path=food_path, target_size=GameBalance.FOOD_SIZE)
                        self.food_images[food_name] = food_image
                        print(f"✓ 加载食物图片: {filename}")
                    except Exception as e:
                        print(f"✗ 加载食物图片失败: {food_path}, 错误: {e}")

    def _load_ui_images(self) -> None:
        """加载UI图片资源"""
        print("加载UI图片资源...")
        
        if os.path.exists(self.ui_dir):
            for filename in os.listdir(self.ui_dir):
                if filename.endswith(".png"):
                    ui_name = filename.replace(".png", "")
                    ui_path = os.path.join(self.ui_dir, filename)
                    try:
                        ui_image = pygame.image.load(ui_path).convert_alpha()
                        self.ui_images[ui_name] = ui_image
                        print(f"✓ 加载UI图片: {filename}")
                    except Exception as e:
                        print(f"✗ 加载UI图片失败: {ui_path}, 错误: {e}")

    def get_snake_image(self, skin_id: int, image_type: str) -> Optional[pygame.Surface]:
        """
        获取蛇的图片
        
        Args:
            skin_id: 皮肤ID
            image_type: 图片类型 ("head", "body0", "body1", 等)
            
        Returns:
            图片Surface，如果不存在返回None
        """
        return self.snake_images.get((skin_id, image_type))

    def has_snake_images(self, skin_id: int) -> bool:
        """检查指定皮肤是否有图片资源"""
        return any(key[0] == skin_id for key in self.snake_images.keys())

    def get_food_image(self, food_name: str, size: int = None) -> Optional[pygame.Surface]:
        """获取食物图片"""
        return self.food_images.get(food_name)

    def get_ui_image(self, ui_name: str) -> Optional[pygame.Surface]:
        """获取UI图片"""
        return self.ui_images.get(ui_name)

    def get_available_snake_skins(self) -> list:
        """获取可用的蛇皮肤ID列表"""
        skin_ids = set()
        for key in self.snake_images.keys():
            skin_ids.add(key[0])
        return sorted(list(skin_ids))

    def get_snake_skin_preview(self, skin_id: int, size: Tuple[int, int] = (100, 100)) -> Optional[pygame.Surface]:
        """获取蛇皮肤的预览图"""
        head_image = self.get_snake_image(skin_id, "head")
        if head_image:
            return pygame.transform.scale(head_image, size)
        return None

    def reload_images(self) -> None:
        """重新加载所有图片"""
        self.snake_images.clear()
        self.food_images.clear()
        self.ui_images.clear()
        self._preload_images()
        print("图片资源已重新加载")


# 全局图片管理器实例
_image_manager: Optional[ImageManager] = None


def get_image_manager() -> ImageManager:
    """获取全局图片管理器实例"""
    global _image_manager
    if _image_manager is None:
        _image_manager = ImageManager()
    return _image_manager


def reload_image_manager() -> None:
    """重新加载图片管理器"""
    global _image_manager
    _image_manager = None
    get_image_manager()