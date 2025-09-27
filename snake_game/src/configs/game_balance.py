"""
游戏平衡性配置
"""


class GameBalance:
    """游戏平衡性参数配置"""

    # 蛇的尺寸配置（经过调试优化）
    SNAKE_HEAD_SIZE = 40
    SNAKE_BODY_SIZE = 25

    # 移动和网格配置
    GRID_SIZE = 20

    # 食物配置
    FOOD_SIZE = 30  # 食物尺寸
    FOOD_SCORE_VALUE = 10  # 食物分数
    MAX_FOOD_COUNT = 1  # 同时存在的食物数量
    FOOD_GENERATION_MARGIN = 2  # 食物生成时的边缘留白网格数

    # 蛇的初始配置
    INITIAL_BODY_SEGMENTS = 3  # 初始身体段数
    INITIAL_POSITION = (400, 300)  # 初始位置

    # 顺滑移动配置
    SMOOTH_MOVE_SPEED = 120.0  # 像素/秒 - 蛇的移动速度
    SMOOTH_TURN_SPEED = 180.0  # 度/秒 - 转向速度
    SMOOTH_SEGMENT_DISTANCE = 20.0  # 身体段之间的距离
    SMOOTH_COLLISION_RADIUS = 12.0  # 碰撞检测半径
    SMOOTH_MAX_TURN_ANGLE = 90.0  # 每秒最大转向角度
    SMOOTH_TURNING_ENABLED = True  # 启用平滑转向

    SMOOTH_BOOST_MULTIPLIER = 2.0  # 加速倍数

    # 游戏难度配置
    DIFFICULTY_LEVELS = {
        'easy': {
            'move_delay': 400,
            'food_score': 5
        },
        'normal': {
            'move_delay': 300,
            'food_score': 10
        },
        'hard': {
            'move_delay': 200,
            'food_score': 15
        },
        'expert': {
            'move_delay': 150,
            'food_score': 20
        }
    }

    @classmethod
    def get_difficulty_config(cls, difficulty: str = 'normal') -> dict:
        """
        获取难度配置
        :param difficulty: 难度等级
        :return: 难度配置字典
        """
        return cls.DIFFICULTY_LEVELS.get(difficulty, cls.DIFFICULTY_LEVELS['normal'])

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
