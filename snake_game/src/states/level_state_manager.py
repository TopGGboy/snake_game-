import pygame
from .level_loading import LevelLoadingScreen
from .level_pause_menu import LevelPauseMenu
from .level_game_over import LevelGameOverMenu


class LevelStateManager:
    """关卡状态管理器 - 统一管理关卡模式的所有界面状态切换"""
    
    def __init__(self, level_mode_instance, screen_width, screen_height):
        """
        初始化状态管理器
        :param level_mode_instance: LevelMode实例
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        """
        self.level_mode = level_mode_instance
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 定义所有可能的状态
        self.STATE_GAME = 'game'           # 游戏进行中
        self.STATE_PAUSE = 'pause'         # 暂停界面
        self.STATE_LOADING = 'loading'     # 加载界面
        self.STATE_GAME_OVER = 'game_over' # 游戏结束界面
        self.STATE_LEVEL_COMPLETE = 'level_complete'  # 关卡完成界面
        
        # 当前状态
        self.current_state = self.STATE_LOADING
        
        # 创建界面实例
        self.level_loading = LevelLoadingScreen(screen_width, screen_height)
        self.level_pause_menu = LevelPauseMenu(screen_width, screen_height, level_mode_instance, 
                                              level_mode_instance.current_level_index + 1, 
                                              len(level_mode_instance.available_levels))
        self.level_game_over = LevelGameOverMenu(screen_width, screen_height)
        
        # 状态切换回调
        self.on_state_change = None
    
    def set_state(self, new_state):
        """设置新的状态"""
        if new_state != self.current_state:
            old_state = self.current_state
            self.current_state = new_state
            
            # 同步游戏状态
            if new_state == self.STATE_PAUSE:
                self.level_mode.paused = True
                self.level_pause_menu.reset()
            elif new_state == self.STATE_GAME:
                self.level_mode.paused = False
            elif new_state == self.STATE_LOADING:
                self.level_loading.reset()
            elif new_state == self.STATE_GAME_OVER:
                self.level_game_over.reset()
            
            # 调用状态改变回调
            if self.on_state_change:
                self.on_state_change(old_state, new_state)
    
    def handle_event(self, event):
        """处理事件 - 根据当前状态分发到对应的界面"""
        if self.current_state == self.STATE_LOADING:
            return self._handle_loading_event(event)
        elif self.current_state == self.STATE_PAUSE:
            return self._handle_pause_event(event)
        elif self.current_state == self.STATE_GAME_OVER:
            return self._handle_game_over_event(event)
        elif self.current_state == self.STATE_GAME:
            return self._handle_game_event(event)
        elif self.current_state == self.STATE_LEVEL_COMPLETE:
            return self._handle_level_complete_event(event)
    
    def update(self, surface, keys):
        """更新界面 - 根据当前状态更新对应的界面"""
        if self.current_state == self.STATE_LOADING:
            self.level_loading.update(surface, keys)
        elif self.current_state == self.STATE_PAUSE:
            self.level_pause_menu.update(surface, keys)
        elif self.current_state == self.STATE_GAME_OVER:
            self.level_game_over.update(surface, keys)
        elif self.current_state == self.STATE_LEVEL_COMPLETE:
            # 关卡完成状态也使用暂停界面来更新
            self.level_pause_menu.update(surface, keys)
    
    def draw(self, surface):
        """绘制界面 - 根据当前状态绘制对应的界面"""
        if self.current_state == self.STATE_LOADING:
            self.level_loading.draw(surface)
        elif self.current_state == self.STATE_PAUSE:
            self.level_pause_menu.draw(surface)
        elif self.current_state == self.STATE_GAME_OVER:
            self.level_game_over.draw(surface)
        elif self.current_state == self.STATE_LEVEL_COMPLETE:
            # 关卡完成状态也使用暂停界面来绘制
            self.level_pause_menu.draw(surface)
    
    def _handle_loading_event(self, event):
        """处理加载界面事件"""
        self.level_loading.handle_event(event)
        if self.level_loading.is_finished():
            self.set_state(self.STATE_GAME)
    
    def _handle_pause_event(self, event):
        """处理暂停界面事件"""
        self.level_pause_menu.handle_event(event)
        if self.level_pause_menu.is_finished():
            action = self.level_pause_menu.get_action()
            if action == 'resume':
                # 恢复游戏时，确保暂停状态被清除
                self.level_mode.paused = False
                self.set_state(self.STATE_GAME)
            elif action == 'restart':
                self.level_mode.restart_game()
                self.set_state(self.STATE_GAME)
            elif action == 'next_level':
                self.level_mode._go_to_next_level()
            elif action == 'previous_level':
                self.level_mode._go_to_previous_level()
            elif action == 'main_menu':
                self.level_mode.finished = True
                self.level_mode.next = 'main_menu'
            elif action == 'quit':
                pygame.quit()
                quit()
    
    def _handle_game_over_event(self, event):
        """处理游戏结束界面事件"""
        self.level_game_over.handle_event(event)
        if self.level_game_over.is_finished():
            action = self.level_game_over.get_action()
            if action == 'restart':
                self.level_mode.restart_game()
                self.set_state(self.STATE_GAME)
            elif action == 'next_level':
                self.level_mode._go_to_next_level()
            elif action == 'previous_level':
                self.level_mode._go_to_previous_level()
            elif action == 'main_menu':
                self.level_mode.finished = True
                self.level_mode.next = 'main_menu'
            elif action == 'quit':
                pygame.quit()
                quit()
    
    def _handle_game_event(self, event):
        """处理游戏进行中事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                # ESC或P键暂停游戏
                if not self.level_mode.game_over and not self.level_mode.level_completed:
                    self.set_state(self.STATE_PAUSE)
    
    def _handle_level_complete_event(self, event):
        """处理关卡完成事件 - 使用暂停界面显示游戏胜利"""
        # 设置暂停界面为胜利模式
        self.level_pause_menu.set_victory_mode(True)
        
        # 处理暂停界面事件
        self.level_pause_menu.handle_event(event)
        if self.level_pause_menu.is_finished():
            action = self.level_pause_menu.get_action()
            if action == 'resume' or action == 'next_level':
                # 继续游戏或下一关都跳转到下一关
                self.level_mode._go_to_next_level()
            elif action == 'restart':
                self.level_mode.restart_game()
                self.set_state(self.STATE_GAME)
            elif action == 'previous_level':
                self.level_mode._go_to_previous_level()
            elif action == 'main_menu':
                self.level_mode.finished = True
                self.level_mode.next = 'main_menu'
            elif action == 'quit':
                pygame.quit()
                quit()
    
    def is_in_interface_state(self):
        """检查是否处于界面状态（非游戏状态）"""
        return self.current_state in [self.STATE_LOADING, self.STATE_PAUSE, self.STATE_GAME_OVER, self.STATE_LEVEL_COMPLETE]
    
    def get_current_state(self):
        """获取当前状态"""
        return self.current_state