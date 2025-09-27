"""
图片处理工具函数
"""
import os
import pygame


def get_content_bounds(image):
    """获取图片中非透明内容的边界"""
    width, height = image.get_size()
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found_content = False

    for x in range(width):
        for y in range(height):
            pixel = image.get_at((x, y))
            if len(pixel) > 3 and pixel[3] > 0:
                found_content = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if found_content:
        return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    return None


def extract_main_subject(image_path, colorkey=(255, 255, 255)):
    """从背景图片中抠出主体部分"""
    try:
        original_image = pygame.image.load(image_path).convert_alpha()
        original_image.set_colorkey(colorkey)

        content_bounds = get_content_bounds(original_image)
        if content_bounds:
            cropped_image = pygame.Surface((content_bounds.width, content_bounds.height), pygame.SRCALPHA)
            cropped_image.fill((0, 0, 0, 0))
            cropped_image.blit(original_image, (0, 0), content_bounds)
            return cropped_image
        else:
            return original_image
    except (pygame.error, FileNotFoundError) as e:
        print(f"无法加载图片 {image_path}: {e}")
        return None


def normalize_to_standard_size(image, standard_size=64):
    """将图片标准化到统一尺寸"""
    if image is None:
        return None

    original_width, original_height = image.get_size()
    max_dimension = max(original_width, original_height)
    # 使用更大的缩放比例，确保图片填满标准尺寸
    scale_factor = standard_size * 0.95 / max_dimension

    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    scaled_image = pygame.transform.scale(image, (new_width, new_height))

    standard_image = pygame.Surface((standard_size, standard_size), pygame.SRCALPHA)
    standard_image.fill((0, 0, 0, 0))

    # 精确居中计算，确保像素级对齐
    x_offset = (standard_size - new_width) // 2
    y_offset = (standard_size - new_height) // 2

    # 如果有奇数像素差，向上取整确保居中
    if (standard_size - new_width) % 2 == 1:
        x_offset += 1
    if (standard_size - new_height) % 2 == 1:
        y_offset += 1

    standard_image.blit(scaled_image, (x_offset, y_offset))

    return standard_image


def create_default_image(size, color=(255, 0, 0)):
    """创建默认图片"""
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    image.fill(color)
    pygame.draw.rect(image, (150, 0, 0), image.get_rect(), 2)
    return image


def process_game_image(image_path, target_size=32, colorkey=(255, 255, 255), standard_size=64):
    """完整的图片处理流程"""
    main_subject = extract_main_subject(image_path, colorkey)
    standard_image = normalize_to_standard_size(main_subject, standard_size)

    if standard_image is None:
        return create_default_image(target_size)

    return pygame.transform.scale(standard_image, (target_size, target_size))


def process_snake_image(image_path, colorkey=(255, 255, 255), target_size=32):
    """处理蛇的图片（向后兼容）"""
    return process_game_image(image_path, target_size, colorkey)
