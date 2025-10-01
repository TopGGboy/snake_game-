import os
from PIL import Image
import glob
import numpy as np


def get_content_bounds(img_array):
    """
    获取图片内容区域的边界框（排除纯黑色背景）
    """
    # 找到非白色和非纯黑色像素的位置
    # 纯黑色定义为RGB值都小于10
    is_not_black = np.any(img_array > 10, axis=-1)
    is_not_white = np.any(img_array < 240, axis=-1)
    content_mask = is_not_black & is_not_white

    if not np.any(content_mask):
        return None  # 没有有效内容

    # 获取内容区域的边界
    rows = np.any(content_mask, axis=1)
    cols = np.any(content_mask, axis=0)

    y_min, y_max = np.where(rows)[0][[0, -1]] if np.any(rows) else (0, img_array.shape[0] - 1)
    x_min, x_max = np.where(cols)[0][[0, -1]] if np.any(cols) else (0, img_array.shape[1] - 1)

    return (x_min, y_min, x_max, y_max)


def smart_resize_with_padding(img, target_size=(64, 64), padding_ratio=0.1):
    """
    智能缩放图片：根据内容大小自动调整缩放比例，确保内容填充画布

    Args:
        img: PIL Image对象
        target_size: 目标尺寸 (width, height)
        padding_ratio: 内容与画布边缘的间距比例
    """
    # 转换为numpy数组进行分析
    img_array = np.array(img)

    # 获取内容边界框
    bounds = get_content_bounds(img_array)

    if bounds is None:
        # 没有检测到内容，直接居中缩放
        return img.resize(target_size, Image.Resampling.LANCZOS)

    x_min, y_min, x_max, y_max = bounds
    content_width = x_max - x_min + 1
    content_height = y_max - y_min + 1

    # 计算目标内容区域大小（考虑边距）
    target_width = int(target_size[0] * (1 - 2 * padding_ratio))
    target_height = int(target_size[1] * (1 - 2 * padding_ratio))

    # 计算缩放比例（保持宽高比）
    scale_x = target_width / content_width
    scale_y = target_height / content_height
    scale = min(scale_x, scale_y)  # 使用较小的比例确保内容完全显示

    # 计算缩放后的内容尺寸
    new_content_width = int(content_width * scale)
    new_content_height = int(content_height * scale)

    # 计算在目标画布中的位置（居中）
    x_offset = (target_size[0] - new_content_width) // 2
    y_offset = (target_size[1] - new_content_height) // 2

    # 裁剪内容区域
    content_img = img.crop((x_min, y_min, x_max + 1, y_max + 1))

    # 缩放内容
    resized_content = content_img.resize((new_content_width, new_content_height), Image.Resampling.LANCZOS)

    # 创建白色背景
    result_img = Image.new('RGB', target_size, (255, 255, 255))

    # 将缩放后的内容粘贴到居中位置
    result_img.paste(resized_content, (x_offset, y_offset))

    return result_img


def process_images(input_dir, output_dir, target_size=(64, 64)):
    """
    优化处理图片：智能缩放确保内容填充画布

    Args:
        input_dir: 输入图片目录
        output_dir: 输出图片目录
        target_size: 目标尺寸 (width, height)
    """

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 支持的图片格式
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']

    processed_count = 0

    # 遍历所有图片文件
    for extension in image_extensions:
        pattern = os.path.join(input_dir, '**', extension)
        for image_path in glob.glob(pattern, recursive=True):
            try:
                # 打开图片
                with Image.open(image_path) as img:
                    # 转换为RGB模式（移除透明度）
                    if img.mode in ('RGBA', 'LA'):
                        # 创建白色背景
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        # 合并图片（将透明部分替换为白色）
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')

                    # 使用智能缩放处理图片
                    img_resized = smart_resize_with_padding(img, target_size)

                    # 构建输出路径（保持目录结构）
                    relative_path = os.path.relpath(image_path, input_dir)
                    output_path = os.path.join(output_dir, relative_path)

                    # 创建输出目录
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # 保存图片
                    img_resized.save(output_path, 'PNG')

                    print(f"处理成功: {image_path} -> {output_path}")
                    processed_count += 1

            except Exception as e:
                print(f"处理失败 {image_path}: {e}")

    print(f"\n总共处理了 {processed_count} 张图片")
    return processed_count


def main():
    # 设置路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    graphics_dir = os.path.join(base_dir, 'graphics')
    output_dir = os.path.join(base_dir, 'graphics_processed')

    # 处理图片
    print("开始处理图片...")
    processed_count = process_images(graphics_dir, output_dir)

    if processed_count > 0:
        print(f"\n处理完成！所有图片已保存到: {output_dir}")
        print("处理后的图片特征:")
        print("- 尺寸: 64x64 像素")
        print("- 格式: PNG")
        print("- 背景: 白色")
    else:
        print("未找到可处理的图片文件")


if __name__ == "__main__":
    main()
