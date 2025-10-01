"""
蛇形象配置文件
支持多种蛇形象，如果存在图片资源则使用图片，否则使用默认颜色
"""

SNAKE_SKINS = {
    "snake0": {
        "name": "经典小蛇",
        "description": "传统的绿色小蛇形象",
        "image_prefix": "snake0",
        "head_color": (0, 255, 0),
        "body_color": (0, 200, 0),
        "border_color": (0, 150, 0),
        "highlight_color": (150, 255, 150),
        "unlocked": True
    },
    "snake1": {
        "name": "现代大蛇",
        "description": "带有身体图片的现代蛇形象",
        "image_prefix": "snake1",
        "head_color": (255, 100, 0),
        "body_color": (200, 80, 0),
        "border_color": (150, 60, 0),
        "highlight_color": (255, 200, 150),
        "unlocked": True
    }
}

def get_available_skins():
    """获取可用的蛇形象列表"""
    return [skin for skin in SNAKE_SKINS.values() if skin["unlocked"]]

def get_skin_by_key(key):
    """根据key获取蛇形象配置"""
    return SNAKE_SKINS.get(key, SNAKE_SKINS["snake0"])

def get_skin_keys():
    """获取所有蛇形象的key列表"""
    return list(SNAKE_SKINS.keys())

def get_available_snake_images():
    """获取可用的蛇形象列表（兼容旧函数名）"""
    return get_available_skins()

def get_snake_image_config(skin_id):
    """根据皮肤ID获取蛇形象配置"""
    key = f"snake{skin_id}"
    return SNAKE_SKINS.get(key, SNAKE_SKINS["snake0"])