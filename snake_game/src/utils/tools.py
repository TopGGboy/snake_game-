"""
图片处理工具函数

版权所有 © 2025 "果香蛇踪"游戏开发团队
联系方式：3085678256@qq.com

本程序受版权法保护，未经授权禁止复制、修改、分发或用于商业用途。
"""
import os
import pygame


def get_content_bounds(image, alpha_threshold=5):
    """获取图片中非透明内容的边界（优化版，处理抗锯齿边缘）"""
    width, height = image.get_size()
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found_content = False
    
    # 第一遍扫描：检测主要内容区域
    for x in range(width):
        for y in range(height):
            pixel = image.get_at((x, y))
            if len(pixel) > 3 and pixel[3] > alpha_threshold:
                found_content = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    
    if not found_content:
        return None
    
    # 第二遍扫描：扩展边界以包含半透明边缘
    margin = 2  # 扩展2像素以包含抗锯齿边缘
    min_x = max(0, min_x - margin)
    min_y = max(0, min_y - margin)
    max_x = min(width - 1, max_x + margin)
    max_y = min(height - 1, max_y + margin)
    
    return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)


def smooth_edges(image, threshold=15):
    """平滑边缘，去除白边（优化版）"""
    width, height = image.get_size()
    smoothed_image = image.copy()
    
    # 两遍处理：第一遍检测边缘，第二遍应用平滑
    edge_pixels = set()
    
    # 第一遍：标记边缘像素
    for x in range(width):
        for y in range(height):
            pixel = image.get_at((x, y))
            if len(pixel) > 3 and 0 < pixel[3] < 255:
                # 检查周围是否有完全不透明或完全透明的像素
                has_opaque = False
                has_transparent = False
                
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbor_pixel = image.get_at((nx, ny))
                            if len(neighbor_pixel) > 3:
                                if neighbor_pixel[3] == 255:
                                    has_opaque = True
                                elif neighbor_pixel[3] == 0:
                                    has_transparent = True
                
                # 如果是边缘像素（介于透明和不透明之间）
                if has_opaque and has_transparent:
                    edge_pixels.add((x, y))
    
    # 第二遍：处理边缘像素
    for x, y in edge_pixels:
        pixel = image.get_at((x, y))
        if len(pixel) > 3 and pixel[3] < threshold:
            # 对于低alpha的边缘像素，如果周围透明像素较多，则设为完全透明
            transparent_count = 0
            total_count = 0
            
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor_pixel = image.get_at((nx, ny))
                        if len(neighbor_pixel) > 3:
                            total_count += 1
                            if neighbor_pixel[3] < 10:  # 几乎透明
                                transparent_count += 1
            
            if total_count > 0 and transparent_count / total_count > 0.4:
                smoothed_image.set_at((x, y), (0, 0, 0, 0))
    
    return smoothed_image


def extract_main_subject(image_path, colorkey=(255, 255, 255), white_threshold=220):
    """直接将白色区域变成透明（高级优化版）"""
    try:
        # 初始化pygame显示模式（如果未初始化）
        if not pygame.display.get_init():
            pygame.display.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
        original_image = pygame.image.load(image_path).convert_alpha()
        
        # 创建透明背景的图片
        result_image = pygame.Surface(original_image.get_size(), pygame.SRCALPHA)
        result_image.fill((0, 0, 0, 0))
        
        width, height = original_image.get_size()
        
        # 计算颜色与白色的相似度
        def color_similarity_to_white(r, g, b):
            """计算颜色与白色的相似度（0-1，1表示完全白色）"""
            # 使用欧几里得距离计算
            distance = ((255 - r) ** 2 + (255 - g) ** 2 + (255 - b) ** 2) ** 0.5
            max_distance = (255 ** 2 * 3) ** 0.5  # 最大可能距离
            similarity = 1 - (distance / max_distance)
            return similarity
        
        # 遍历每个像素，智能处理白色区域
        for x in range(width):
            for y in range(height):
                pixel = original_image.get_at((x, y))
                
                if len(pixel) >= 3:
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    alpha = pixel[3] if len(pixel) == 4 else 255
                    
                    # 计算与白色的相似度
                    similarity = color_similarity_to_white(r, g, b)
                    
                    # 智能阈值处理
                    if similarity > 0.85:  # 85%以上相似度认为是白色
                        # 完全透明处理
                        result_image.set_at((x, y), (0, 0, 0, 0))
                    elif similarity > 0.7:  # 70-85%相似度，处理抗锯齿边缘
                        # 根据相似度设置透明度
                        new_alpha = int(alpha * (1 - similarity) * 2)
                        result_image.set_at((x, y), (r, g, b, new_alpha))
                    else:
                        # 非白色区域保留原样
                        result_image.set_at((x, y), (r, g, b, alpha))
        
        return result_image
    except (pygame.error, FileNotFoundError) as e:
        print(f"无法加载图片 {image_path}: {e}")
        return None


def normalize_to_standard_size(image, standard_size=128):
    """将图片缩放到标准尺寸，保持宽高比和内容完整性"""
    if image is None:
        return create_default_image(standard_size)

    original_width, original_height = image.get_size()
    
    if original_width == 0 or original_height == 0:
        return create_default_image(standard_size)
    
    # 计算最佳缩放比例，确保图片完全包含在标准尺寸内
    scale_factor = min(standard_size / original_width, standard_size / original_height)
    
    # 计算新尺寸（至少1像素）
    new_width = max(1, int(original_width * scale_factor))
    new_height = max(1, int(original_height * scale_factor))
    
    # 使用平滑缩放保持图像质量
    try:
        scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
    except:
        scaled_image = pygame.transform.scale(image, (new_width, new_height))
    
    # 创建标准尺寸的透明画布
    result_image = pygame.Surface((standard_size, standard_size), pygame.SRCALPHA)
    result_image.fill((0, 0, 0, 0))
    
    # 居中放置缩放后的图片
    x_offset = (standard_size - new_width) // 2
    y_offset = (standard_size - new_height) // 2
    result_image.blit(scaled_image, (x_offset, y_offset))
    
    return result_image


def create_default_image(size, color=(255, 0, 0)):
    """创建默认图片"""
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    image.fill(color)
    pygame.draw.rect(image, (150, 0, 0), image.get_rect(), 2)
    return image


def standardize_image_processing(image_path, target_size=32, colorkey=(255, 255, 255), standard_size=128):
    """标准化图片处理流程：提取主题 → 缩放到统一大小 → 透明化背景 → 缩放到目标大小"""
    try:
        # 1. 提取主题（白色背景透明化）
        main_subject = extract_main_subject(image_path, colorkey)
        
        if main_subject is None:
            return create_default_image(target_size)
        
        # 2. 缩放到统一标准尺寸（保持宽高比）
        standardized_image = normalize_to_standard_size(main_subject, standard_size)
        
        # 3. 进一步优化透明化处理（处理残留白边）
        optimized_image = optimize_transparency(standardized_image, colorkey)
        
        # 4. 缩放到最终目标尺寸
        final_image = pygame.transform.smoothscale(optimized_image, (target_size, target_size))
        
        return final_image 
        
    except Exception as e:
        print(f"图片处理失败 {image_path}: {e}")
        return create_default_image(target_size)


def optimize_transparency(image, colorkey=(255, 255, 255), white_threshold=230):
    """优化透明度处理，去除残留白边"""
    width, height = image.get_size()
    result_image = image.copy()
    
    for x in range(width):
        for y in range(height):
            pixel = image.get_at((x, y))
            
            if len(pixel) >= 3:
                r, g, b = pixel[0], pixel[1], pixel[2]
                alpha = pixel[3] if len(pixel) == 4 else 255
                
                # 检测接近白色的像素
                if r > white_threshold and g > white_threshold and b > white_threshold:
                    # 如果是接近白色的像素，设为完全透明
                    result_image.set_at((x, y), (0, 0, 0, 0))
                elif alpha > 0:
                    # 对于非透明像素，确保不是白色背景
                    color_distance = ((r - colorkey[0]) ** 2 + 
                                     (g - colorkey[1]) ** 2 + 
                                     (b - colorkey[2]) ** 2) ** 0.5
                    
                    # 如果颜色与背景色太接近，降低透明度
                    if color_distance < 30:
                        new_alpha = max(0, alpha - int(30 - color_distance))
                        result_image.set_at((x, y), (r, g, b, new_alpha))
    
    return result_image


def process_game_image(image_path, target_size=32, colorkey=(255, 255, 255), standard_size=128):
    """完整的图片处理流程（标准化版本）"""
    return standardize_image_processing(image_path, target_size, colorkey, standard_size)


def process_snake_image(image_path, colorkey=(255, 255, 255), target_size=32):
    """处理蛇的图片（向后兼容）"""
    return standardize_image_processing(image_path, target_size, colorkey)


def batch_process_images(image_paths, target_sizes=None, colorkey=(255, 255, 255)):
    """批量处理图片，支持不同目标尺寸"""
    if target_sizes is None:
        target_sizes = [32] * len(image_paths)
    
    processed_images = {}
    
    for i, image_path in enumerate(image_paths):
        target_size = target_sizes[i] if i < len(target_sizes) else 32
        processed_images[image_path] = standardize_image_processing(
            image_path, target_size, colorkey
        )
    
    return processed_images


def get_image_dimensions(image_path):
    """获取图片原始尺寸信息"""
    try:
        image = pygame.image.load(image_path)
        return image.get_size()
    except:
        return (0, 0)


def get_image_processing_info(image_path):
    """获取图片处理信息"""
    original_size = get_image_dimensions(image_path)
    return {
        "original_size": original_size,
        "standard_size": 128,
        "processing_steps": ["主题提取", "标准化缩放", "透明化优化", "目标缩放"]
    }
