"""
皮肤配置文件
"""

SKIN_CONFIG = {
    "default": {
        "name": "默认皮肤",
        "description": "经典金黄色皮肤",
        "unlocked": True
    },
    "red": {
        "name": "红色皮肤", 
        "description": "热情红色皮肤",
        "unlocked": True
    },
    "blue": {
        "name": "蓝色皮肤",
        "description": "冷静蓝色皮肤", 
        "unlocked": True
    },
    "green": {
        "name": "绿色皮肤",
        "description": "自然绿色皮肤",
        "unlocked": True
    },
    "purple": {
        "name": "紫色皮肤",
        "description": "神秘紫色皮肤",
        "unlocked": True
    }
}

def get_available_skins():
    """获取所有可用的皮肤"""
    return list(SKIN_CONFIG.keys())

def get_skin_info(skin_name):
    """获取皮肤信息"""
    return SKIN_CONFIG.get(skin_name, SKIN_CONFIG["default"])

def is_skin_unlocked(skin_name):
    """检查皮肤是否已解锁"""
    skin_info = SKIN_CONFIG.get(skin_name)
    if skin_info:
        return skin_info["unlocked"]
    return False