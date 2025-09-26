"""
游戏主控
"""
import pygame
from src.configs.config import Config
from src.states.main_menu import MainMenu
from src.states.infinite_mode import InfiniteMode


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
        self.clock = pygame.time.Clock()  # 创建时钟对象的控制频率

        self.state = MainMenu()  # 当前游戏状态， 默认围为主菜单
        self.next_state = None

        self.keys = pygame.key.get_pressed()  # 获取当前的按键状态
        self.pause_flag = False  # 暂停状态

        self.return_home_flage = False  # 返回主菜单标志

    def run(self):
        """
        游戏主循环
        """
        while True:
            # 鼠标事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    # 判断是否在主界面
                    flag = self.config.MAIN_MENU_FLAG
                    if flag:
                        # 主界面逻辑
                        self.state.update_cursor(event.key)

                    self.keys = pygame.key.get_pressed()

                    # 暂停游戏
                    if event.key == pygame.K_ESCAPE and flag == False:
                        self.pause_flag = not self.pause_flag

                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 暂停界面的鼠标检测功能
                    pass

            # 如果没有暂停则更新游戏状态
            if not self.pause_flag:
                self.update()

            # 如果暂停则显示暂停界面
            if self.pause_flag:
                pass

            pygame.display.update()
            self.clock.tick(Config.FPS)

    def update(self):
        """
        更新游戏状态
        """
        # 如果当前状态完成且不需要返回主菜单
        if self.state.finished and self.return_home_flage == False:
            self.next_state = self.state.next

            if self.next_state == "infinite_mode":
                self.state = InfiniteMode()
                self.state.finished = False

        self.state.update(self.screen, self.keys)
