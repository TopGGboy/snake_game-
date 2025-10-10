"""
游戏平衡性配置

版权所有 © 2025 "果香蛇踪"游戏开发团队
联系方式：3085678256@qq.com

本程序受版权法保护，未经授权禁止复制、修改、分发或用于商业用途。
"""


class GameBalance:
    """游戏平衡性参数配置"""

    # 蛇的尺寸配置（经过调试优化）
    SNAKE_HEAD_SIZE = 30  # 40
    SNAKE_BODY_SIZE = 15  # 25

    # 移动和网格配置
    GRID_SIZE = 20

    # 食物配置
    FOOD_SIZE = 25  # 食物尺寸
    MAX_FOOD_COUNT = 1  # 同时存在的食物数量
    FOOD_GENERATION_PIXEL = 50  # 食物生成时的边缘留白像素数（增加边距避免靠近墙壁）

    # 蛇的初始配置
    INITIAL_BODY_SEGMENTS = 3  # 初始身体段数
    INITIAL_POSITION = (400, 300)  # 初始位置

    # 顺滑移动配置
    SMOOTH_MOVE_SPEED = 120.0  # 像素/秒 - 蛇的移动速度
    SMOOTH_TURN_SPEED = 360.0  # 度/秒 - 转向速度（提高转向响应性）
    SMOOTH_SEGMENT_DISTANCE = 15.0  # 身体段之间的距离  20.0
    SMOOTH_COLLISION_RADIUS = 12.0  # 碰撞检测半径
    SMOOTH_MAX_TURN_ANGLE = 360.0  # 每秒最大转向角度（提高最大转向能力）
    SMOOTH_TURNING_ENABLED = True  # 启用平滑转向

    SMOOTH_BOOST_MULTIPLIER = 2.0  # 加速倍数

    # 食物类型配置
    FOOD_TYPES = {
        "food0": {  # 苹果
            "name": "苹果",
            "score_value": 10,
            "size": 25,
            "weight": 0.7  # 生成权重
        },
        "food1": {  # 西瓜
            "name": "西瓜",
            "score_value": 20,
            "size": 30,
            "weight": 0.3  # 生成权重
        }
    }

    @classmethod
    def get_food_config(cls, food_name: str):
        """获取食物配置"""
        return cls.FOOD_TYPES.get(food_name, cls.FOOD_TYPES["food0"])

    @classmethod
    def get_random_food_type(cls):
        """根据权重随机选择食物类型"""
        import random
        food_types = list(cls.FOOD_TYPES.keys())
        weights = [cls.FOOD_TYPES[food]["weight"] for food in food_types]
        return random.choices(food_types, weights=weights, k=1)[0]

    @classmethod
    def calculate_speed_increase(cls, score: int) -> int:
        """
        根据分数计算速度提升
        :param score: 当前分数
        :return: 调整后的移动延迟
        """
        # 每100分减少10毫秒延迟，最小100毫秒
        speed_reduction = (score // 100) * 10
        new_delay = max(100, cls.SNAKE_MOVE_DELAY - speed_reduction)
        return new_delay

    @classmethod
    def get_color_scheme(cls, theme: str = 'classic') -> dict:
        """
        获取颜色主题
        :param theme: 主题名称
        :return: 颜色配置字典
        """
        themes = {
            'classic': {
                'background': (0, 0, 0),
                'snake_head': (0, 255, 0),
                'snake_body': (0, 200, 0),
                'food': (255, 0, 0),
                'text': (255, 255, 255),
                'grid': (40, 40, 40)
            },
            'neon': {
                'background': (10, 10, 30),
                'snake_head': (0, 255, 255),
                'snake_body': (0, 200, 255),
                'food': (255, 100, 255),
                'text': (255, 255, 255),
                'grid': (50, 50, 100)
            },
            'retro': {
                'background': (20, 20, 20),
                'snake_head': (255, 255, 0),
                'snake_body': (200, 200, 0),
                'food': (255, 128, 0),
                'text': (255, 255, 255),
                'grid': (60, 60, 60)
            }
        }
        return themes.get(theme, themes['classic'])
