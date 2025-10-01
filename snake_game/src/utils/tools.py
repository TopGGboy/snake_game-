"""
图片处理工具函数
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


def normalize_to_standard_size(image, standard_size=64):
    """将图片标准化到统一尺寸（简化版）"""
    if image is None:
        return None

    original_width, original_height = image.get_size()
    max_dimension = max(original_width, original_height)
    
    if max_dimension == 0:
        return create_default_image(standard_size)
    
    # 简单的缩放比例计算
    scale_factor = standard_size * 0.9 / max_dimension

    new_width = max(1, int(original_width * scale_factor))
    new_height = max(1, int(original_height * scale_factor))

    # 使用平滑缩放
    try:
        scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
    except:
        scaled_image = pygame.transform.scale(image, (new_width, new_height))

    standard_image = pygame.Surface((standard_size, standard_size), pygame.SRCALPHA)
    standard_image.fill((0, 0, 0, 0))

    # 居中放置
    x_offset = (standard_size - new_width) // 2
    y_offset = (standard_size - new_height) // 2

    standard_image.blit(scaled_image, (x_offset, y_offset))
    
    return standard_image


def create_default_image(size, color=(255, 0, 0)):
    """创建默认图片"""
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    image.fill(color)
    pygame.draw.rect(image, (150, 0, 0), image.get_rect(), 2)
    return image


def process_game_image(image_path, target_size=32, colorkey=(255, 255, 255), standard_size=64):
    """完整的图片处理流程（简化版）"""
    main_subject = extract_main_subject(image_path, colorkey)
    
    if main_subject is None:
        return create_default_image(target_size)
    
    # 直接缩放到目标尺寸，不再进行标准化
    return pygame.transform.scale(main_subject, (target_size, target_size))


def process_snake_image(image_path, colorkey=(255, 255, 255), target_size=32):
    """处理蛇的图片（向后兼容）"""
    return process_game_image(image_path, target_size, colorkey)
