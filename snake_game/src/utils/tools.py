"""
图片处理工具函数
"""
import os
import pygame


def load_graphics(path, accept=('.jpg', '.png', '.bmp', '.gif')):
    """
    加载指定路径下的所有图片文件
    
    Args:
        path: str - 图片文件夹路径
        accept: tuple - 接受的文件扩展名
    
    Returns:
        dict - 图片名称到Surface对象的映射
    """
    graphics = {}
    for pic in os.listdir(path):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
            graphics[name] = img
    return graphics


def get_image(sheet, x, y, width, height, colorkey, scale=1):
    """
    从精灵表中提取图片并进行处理
    
    Args:
        sheet: pygame.Surface - 精灵表图片
        x: int - 提取区域的x坐标
        y: int - 提取区域的y坐标  
        width: int - 提取区域的宽度
        height: int - 提取区域的高度
        colorkey: tuple - 要移除的背景颜色 (R, G, B)
        scale: float - 缩放比例
    
    Returns:
        pygame.Surface - 处理后的图片
    """
    # 创建一个新的surface来存储提取的图片
    image = pygame.Surface((width, height)).convert_alpha()
    
    # 从精灵表中复制指定区域
    image.blit(sheet, (0, 0), (x, y, width, height))
    
    # 设置透明色键，移除指定颜色的背景
    image.set_colorkey(colorkey)
    
    # 如果需要缩放
    if scale != 1:
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = pygame.transform.scale(image, (new_width, new_height))
    
    return image


def get_content_bounds(image):
    """
    获取图片中非透明内容的边界
    
    Args:
        image: pygame.Surface - 要分析的图片
    
    Returns:
        pygame.Rect - 内容边界矩形，如果没有内容则返回None
    """
    width, height = image.get_size()
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found_content = False
    
    for x in range(width):
        for y in range(height):
            pixel = image.get_at((x, y))
            # 检查是否为非透明像素
            if len(pixel) > 3 and pixel[3] > 0:  # 有alpha通道且不透明
                found_content = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    
    if found_content:
        return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    return None


def process_snake_image(image_path, colorkey=(255, 255, 255), target_size=32):
    """
    处理蛇的图片：移除背景，裁剪到主元素，然后缩放到目标大小
    
    Args:
        image_path: str - 图片路径
        colorkey: tuple - 要移除的背景颜色 (R, G, B)
        target_size: int - 目标大小（像素）
    
    Returns:
        pygame.Surface - 处理后的图片
    """
    # 加载原始图片
    original_image = pygame.image.load(image_path).convert_alpha()
    
    # 移除背景色
    original_image.set_colorkey(colorkey)
    
    # 获取内容边界
    content_bounds = get_content_bounds(original_image)
    
    if content_bounds:
        # 裁剪到主元素
        cropped_image = pygame.Surface((content_bounds.width, content_bounds.height), pygame.SRCALPHA)
        cropped_image.fill((0, 0, 0, 0))  # 透明背景
        cropped_image.blit(original_image, (0, 0), content_bounds)
        
        # 缩放到目标大小，保持宽高比
        max_dimension = max(content_bounds.width, content_bounds.height)
        scale_factor = target_size * 0.9 / max_dimension  # 0.9倍缩放，让图片更大
        
        new_width = int(content_bounds.width * scale_factor)
        new_height = int(content_bounds.height * scale_factor)
        
        # 确保最小尺寸
        new_width = max(new_width, target_size // 4)
        new_height = max(new_height, target_size // 4)
        
        scaled_image = pygame.transform.scale(cropped_image, (new_width, new_height))
        
        # 创建一个正方形的surface，将缩放后的图片居中放置
        final_image = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
        final_image.fill((0, 0, 0, 0))  # 透明背景
        
        # 居中放置
        x_offset = (target_size - new_width) // 2
        y_offset = (target_size - new_height) // 2
        final_image.blit(scaled_image, (x_offset, y_offset))
        
        return final_image
    else:
        # 如果没有找到内容，直接缩放原图
        scaled_image = pygame.transform.scale(original_image, (int(target_size * 0.8), int(target_size * 0.8)))
        final_image = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
        final_image.fill((0, 0, 0, 0))
        
        # 居中放置
        offset = (target_size - int(target_size * 0.8)) // 2
        final_image.blit(scaled_image, (offset, offset))
        
        return final_image


def load_image_with_colorkey(image_path, colorkey=(255, 255, 255), scale=1):
    """
    加载图片并移除指定颜色的背景
    
    Args:
        image_path: str - 图片路径
        colorkey: tuple - 要移除的背景颜色 (R, G, B)，默认为白色
        scale: float - 缩放比例
    
    Returns:
        pygame.Surface - 处理后的图片
    """
    # 加载图片
    image = pygame.image.load(image_path).convert_alpha()
    
    # 设置透明色键，移除指定颜色的背景
    image.set_colorkey(colorkey)
    
    # 如果需要缩放
    if scale != 1:
        width, height = image.get_size()
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = pygame.transform.scale(image, (new_width, new_height))
    
    return image