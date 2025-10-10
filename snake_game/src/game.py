"""
游戏主控

版权所有 © 2025 "果香蛇踪"游戏开发团队
联系方式：3085678256@qq.com

本程序受版权法保护，未经授权禁止复制、修改、分发或用于商业用途。
"""
import pygame
import os
from .configs.config import Config
from .states.main_menu import MainMenu
from .states.difficulty_selection import DifficultySelection
from .states.infinite_mode import InfiniteMode
from .states.skin_selection import SkinSelection
from .states.level_selection import LevelSelection
from .states.level_mode import LevelMode
from .utils.sound_manager import SoundManager


class Game:
    def __init__(self):
        """
        初始化游戏控制器
        """
        self.config = Config.get_instance()  # 使用单例模式

        # 初始化 pygame（如果还没有初始化）
        pygame.init()
        # 创建显示窗口
        self.screen = pygame.display.set_mode(Config.SCREEN_SIZE)
        pygame.display.set_caption("果香蛇踪")  # 设置窗口标题
        self.clock = pygame.time.Clock()  # 创建时钟对象的控制频率

        self.state = MainMenu()  # 当前游戏状态， 默认围为主菜单
        self.next_state = None

        self.keys = pygame.key.get_pressed()  # 获取当前的按键状态
        self.pause_flag = False  # 暂停状态

        self.return_home_flage = False  # 返回主菜单标志
        self.selected_difficulty = None  # 存储选中的难度配置
        self.selected_skin = None  # 存储选中的皮肤配置
        self.selected_level = None  # 存储选中的关卡配置

        # 初始化声音管理器并预加载所有音乐
        self.sound_manager = SoundManager.get_instance()
        self.sound_manager.initialize_preloading()  # 预加载所有音乐文件

        # 直接播放预加载的主界面音乐（使用预加载机制）
        self.sound_manager.switch_to_main_music()

    def run(self):
        """
        游戏主循环
        """
        while True:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    # 判断是否在主界面或菜单状态
                    flag = self.config.MAIN_MENU_FLAG
                    if flag:
                        # 主界面逻辑，使用update_cursor方法
                        if hasattr(self.state, 'update_cursor'):
                            self.state.update_cursor(event.key)
                    else:
                        # 游戏进行中，将事件传递给当前状态
                        if hasattr(self.state, 'handle_event'):
                            self.state.handle_event(event)

                    self.keys = pygame.key.get_pressed()

                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 鼠标事件处理
                    if hasattr(self.state, 'handle_event'):
                        self.state.handle_event(event)

            # 处理音乐事件，实现无缝循环
            self.sound_manager.handle_music_events()

            # 更新游戏状态（无论是否暂停都需要更新，因为暂停逻辑现在在各个状态内部处理）
            self.update()

            pygame.display.update()
            self.clock.tick(Config.FPS)

    def update(self):
        """
        更新游戏状态
        """
        # 如果当前状态完成且不需要返回主菜单
        if self.state.finished and self.return_home_flage == False:
            self.next_state = self.state.next

            if self.next_state == "main_menu":
                # 返回主菜单
                # 切换到主界面音乐
                self.sound_manager.switch_to_main_music()

                self.state = MainMenu()
                self.state.finished = False
                self.config.MAIN_MENU_FLAG = True

            elif self.next_state == "difficulty_selection":
                # 进入难度选择
                self.state = DifficultySelection()
                self.state.finished = False
                self.config.MAIN_MENU_FLAG = True  # 保持菜单模式用于键盘导航

            elif self.next_state == "infinite_mode":
                # 进入无尽模式
                # 如果来自难度选择，获取选中的难度配置
                if hasattr(self.state, 'get_selected_difficulty'):
                    self.selected_difficulty = self.state.get_selected_difficulty()

                # 如果来自皮肤选择，获取选中的皮肤ID
                if hasattr(self.state, 'get_selected_skin'):
                    self.selected_skin = self.state.get_selected_skin()
                    # 更新全局配置中的皮肤ID
                    self.config.set_skin_id(self.selected_skin)
                    print(f"选择了皮肤ID: {self.selected_skin}")
                else:
                    # 如果没有选择皮肤，使用当前配置中的皮肤ID
                    self.selected_skin = self.config.get_skin_id()

                # 切换到游戏运行时音乐（使用预加载机制）
                self.sound_manager.switch_to_game_music()

                self.state = InfiniteMode(self.selected_difficulty, self.selected_skin)
                self.state.finished = False
                self.config.MAIN_MENU_FLAG = False

            elif self.next_state == "skin_selection":
                # 进入皮肤选择，传递前一个状态信息
                previous_state = None
                if hasattr(self.state, 'get_selected_level'):
                    previous_state = "level_selection"  # 从关卡选择来的
                elif hasattr(self.state, 'get_selected_difficulty'):
                    previous_state = "difficulty_selection"  # 从难度选择来的

                self.state = SkinSelection(previous_state)
                self.state.finished = False
                self.config.MAIN_MENU_FLAG = True  # 保持菜单模式用于键盘导航

            elif self.next_state == "level_selection":
                # 进入关卡选择
                print("切换到关卡选择界面...")
                self.state = LevelSelection()
                self.state.finished = False
                self.config.MAIN_MENU_FLAG = True  # 保持菜单模式用于键盘导航
                print("关卡选择界面初始化完成")

            elif self.next_state.startswith("level_mode:"):
                # 进入关卡模式（支持从关卡内部切换关卡）
                level_file = self.next_state.split(":")[1]  # 解析关卡文件名
                print(f"切换到关卡: {level_file}")

                # 关卡模式现在直接从全局配置获取皮肤ID
                # 传递关卡名称而不是文件路径
                self.state = LevelMode(level_file)
                self.state.finished = False
                self.config.MAIN_MENU_FLAG = False

                # 切换到游戏运行时音乐（使用预加载机制）
                self.sound_manager.switch_to_game_music()

            elif self.next_state == "main_menu":
                # 返回主菜单（从皮肤选择或关卡选择返回时）
                if hasattr(self.state, 'get_selected_skin'):
                    self.selected_skin = self.state.get_selected_skin()
                    # 更新全局配置中的皮肤ID
                    self.config.set_skin_id(self.selected_skin)
                    print(f"从皮肤选择返回，皮肤ID: {self.selected_skin}")

                # 切换到主界面音乐（使用预加载机制）
                self.sound_manager.switch_to_main_music()

                # 返回主菜单
                self.state = MainMenu()
                self.state.finished = False
                self.config.MAIN_MENU_FLAG = True

        self.state.update(self.screen, self.keys)
