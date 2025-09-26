"""
字体管理器 - 统一管理游戏中的所有字体
"""
import os
import pygame
from typing import Dict, Optional


class FontManager:
    """字体管理器单例类"""
    
    _instance: Optional['FontManager'] = None
    _fonts: Dict[str, pygame.font.Font] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.font_path = os.path.join('resources', 'font', 'font_1.ttf')
        self._load_fonts()
    
    def _load_fonts(self):
        """加载所有需要的字体尺寸"""
        # 检查字体文件是否存在
        if not os.path.exists(self.font_path):
            print(f"警告: 字体文件 {self.font_path} 不存在，使用系统默认字体")
            self.font_path = None
        
        # 定义常用的字体尺寸
        font_sizes = {
            'small': 18,
            'medium': 24,
            'large': 36,
            'xlarge': 48,
            'title': 72,
            'score': 32,
            'menu': 40,
            'help': 20
        }
        
        # 加载所有尺寸的字体
        for size_name, size in font_sizes.items():
            try:
                if self.font_path:
                    font = pygame.font.Font(self.font_path, size)
                else:
                    font = pygame.font.Font(None, size)
                self._fonts[size_name] = font
                print(f"字体加载成功: {size_name} ({size}px)")
            except pygame.error as e:
                print(f"字体加载失败 {size_name}: {e}")
                # 使用系统默认字体作为备用
                self._fonts[size_name] = pygame.font.Font(None, size)
    
    def get_font(self, size_name: str = 'medium') -> pygame.font.Font:
        """
        获取指定尺寸的字体
        
        Args:
            size_name: 字体尺寸名称 ('small', 'medium', 'large', 'xlarge', 'title', 'score', 'menu', 'help')
        
        Returns:
            pygame.font.Font: 字体对象
        """
        if size_name in self._fonts:
            return self._fonts[size_name]
        else:
            print(f"警告: 未找到字体尺寸 '{size_name}'，使用默认字体")
            return self._fonts.get('medium', pygame.font.Font(None, 24))
    
    def get_custom_font(self, size: int) -> pygame.font.Font:
        """
        获取自定义尺寸的字体
        
        Args:
            size: 字体大小（像素）
        
        Returns:
            pygame.font.Font: 字体对象
        """
        try:
            if self.font_path:
                return pygame.font.Font(self.font_path, size)
            else:
                return pygame.font.Font(None, size)
        except pygame.error as e:
            print(f"自定义字体加载失败 ({size}px): {e}")
            return pygame.font.Font(None, size)
    
    def render_text(self, text: str, size_name: str = 'medium', color: tuple = (255, 255, 255), antialias: bool = True) -> pygame.Surface:
        """
        渲染文本
        
        Args:
            text: 要渲染的文本
            size_name: 字体尺寸名称
            color: 文本颜色 (R, G, B)
            antialias: 是否抗锯齿
        
        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        font = self.get_font(size_name)
        return font.render(text, antialias, color)
    
    def get_text_size(self, text: str, size_name: str = 'medium') -> tuple:
        """
        获取文本的尺寸
        
        Args:
            text: 文本内容
            size_name: 字体尺寸名称
        
        Returns:
            tuple: (width, height)
        """
        font = self.get_font(size_name)
        return font.size(text)
    
    @classmethod
    def get_instance(cls) -> 'FontManager':
        """获取字体管理器实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# 便捷函数
def get_font_manager() -> FontManager:
    """获取字体管理器实例的便捷函数"""
    return FontManager.get_instance()


def render_text(text: str, size_name: str = 'medium', color: tuple = (255, 255, 255)) -> pygame.Surface:
    """渲染文本的便捷函数"""
    return get_font_manager().render_text(text, size_name, color)


def get_font(size_name: str = 'medium') -> pygame.font.Font:
    """获取字体的便捷函数"""
    return get_font_manager().get_font(size_name)