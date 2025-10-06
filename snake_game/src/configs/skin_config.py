"""
蛇形象配置文件
支持多种蛇形象，包含完整的颜色配置和加速效果
"""

# 蛇形象配置（统一配置）
SNAKE_SKINS = {
    "snake0": {
        "name": "黄金小蛇",
        "description": "经典的金黄色小蛇形象",
        "image_prefix": "snake0",
        "skin_id": 0,
        "unlocked": True,
        "color_config": {
            'normal': {
                'head_fill': (255, 215, 0),  # 金黄色蛇头
                'head_border': (218, 165, 32),  # 深金色蛇头边框
                'body_fill': (255, 215, 0),  # 金黄色蛇身
                'body_border': (218, 165, 32),  # 深金色蛇身边框
                'highlight': (255, 255, 224)  # 浅黄高光
            },
            'boost': {
                'head_fill': (255, 215, 0),  # 金黄色蛇头
                'head_border': (255, 140, 0),  # 深橙色蛇头边框
                'body_fill': (255, 215, 0),  # 金黄色蛇身
                'body_border': (255, 140, 0),  # 深橙色蛇身边框
                'highlight': (255, 255, 224)  # 浅黄高光
            },
            'boost_effect': {
                'pulse_speed': 0.1,  # 加速脉冲速度
                'glow_intensity': 0.8,  # 发光强度
                'trail_length': 3  # 拖尾效果长度
            }
        }
    },
    "snake1": {
        "name": "草原绿蟒",
        "description": "热带的绿蟒蛇形象",
        "image_prefix": "snake1",
        "skin_id": 1,
        "unlocked": True,
        "color_config": {
            'normal': {
                'head_fill': (200, 80, 0),  # 橙色蛇头
                'head_border': (150, 60, 0),  # 深橙色蛇头边框
                'body_fill': (200, 80, 0),  # 橙色蛇身
                'body_border': (150, 60, 0),  # 深橙色蛇身边框
                'highlight': (255, 200, 150)  # 浅橙高光
            },
            'boost': {
                'head_fill': (255, 140, 0),  # 亮橙色蛇头
                'head_border': (200, 100, 0),  # 橙红色蛇头边框
                'body_fill': (255, 140, 0),  # 亮橙色蛇身
                'body_border': (200, 100, 0),  # 橙红色蛇身边框
                'highlight': (255, 220, 180)  # 浅橙高光
            },
            'boost_effect': {
                'pulse_speed': 0.15,  # 加速脉冲速度
                'glow_intensity': 0.9,  # 发光强度
                'trail_length': 4  # 拖尾效果长度
            }
        }
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


def get_snake_color_config(skin_id):
    """根据皮肤ID获取蛇颜色配置"""
    for skin in SNAKE_SKINS.values():
        if skin["skin_id"] == skin_id:
            return skin["color_config"]
    # 默认返回snake0的配置
    return SNAKE_SKINS["snake0"]["color_config"]


def get_snake_colors(skin_id, is_boosting=False):
    """根据皮肤ID和加速状态获取蛇颜色"""
    config = get_snake_color_config(skin_id)
    state = 'boost' if is_boosting else 'normal'
    return config[state]


def get_boost_effect_config(skin_id):
    """根据皮肤ID获取加速效果配置"""
    config = get_snake_color_config(skin_id)
    return config.get('boost_effect', SNAKE_SKINS["snake0"]["color_config"]["boost_effect"])
