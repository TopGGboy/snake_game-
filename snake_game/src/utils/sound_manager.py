"""
声音管理器
"""
import pygame
import os


class SoundManager:
    _instance = None

    def __init__(self):
        """初始化声音管理器"""
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.background_music = None
        self.current_music_type = None  # 当前播放的音乐类型
        self.music_volume = 0.9  # 默认音量80%
        self.is_music_playing = False
        self.fade_duration = 1000  # 淡入淡出过渡时间（毫秒）
        self.music_end_event = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.music_end_event)

    @classmethod
    def get_instance(cls):
        """获取声音管理器单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_background_music(self, music_path, music_type=None):
        """加载背景音乐"""
        if os.path.exists(music_path):
            # 检查音乐文件是否已加载
            if self.background_music != music_path or self.current_music_type != music_type:
                self.background_music = music_path
                self.current_music_type = music_type
                print(f"背景音乐已加载: {music_path} (类型: {music_type})")
            return True
        else:
            print(f"音乐文件不存在: {music_path}")
            return False

    def play_background_music(self, loops=-1, fade_ms=0):
        """播放背景音乐"""
        if self.background_music and not self.is_music_playing:
            try:
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                self.is_music_playing = True
                print("背景音乐开始播放")
                return True
            except Exception as e:
                print(f"播放背景音乐失败: {e}")
                return False
        return False

    def handle_music_events(self):
        """处理音乐事件，用于无缝循环"""
        for event in pygame.event.get(self.music_end_event):
            if event.type == self.music_end_event:
                # 音乐播放结束，重新开始播放实现无缝循环
                if self.is_music_playing:
                    try:
                        pygame.mixer.music.play()
                        print("音乐无缝循环播放")
                    except Exception as e:
                        print(f"音乐循环播放失败: {e}")

    def stop_background_music(self, fade_ms=0):
        """停止背景音乐"""
        if self.is_music_playing:
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
            self.is_music_playing = False
            print("背景音乐已停止")

    def pause_background_music(self):
        """暂停背景音乐"""
        if self.is_music_playing:
            pygame.mixer.music.pause()
            print("背景音乐已暂停")

    def unpause_background_music(self):
        """恢复背景音乐"""
        if self.is_music_playing:
            pygame.mixer.music.unpause()
            print("背景音乐已恢复")

    def set_music_volume(self, volume):
        """设置音乐音量 (0.0 到 1.0)"""
        if 0.0 <= volume <= 1.0:
            self.music_volume = volume
            if self.is_music_playing:
                pygame.mixer.music.set_volume(volume)
            return True
        return False

    def get_music_volume(self):
        """获取当前音乐音量"""
        return self.music_volume

    def switch_to_main_music(self):
        """切换到主界面音乐（带淡入淡出效果）"""
        self.stop_background_music(self.fade_duration)
        if self.load_background_music("assets/sound/main.mp3", "main"):
            # 等待淡出完成后再开始新音乐
            pygame.time.wait(self.fade_duration)
            return self.play_background_music(fade_ms=self.fade_duration)
        return False

    def switch_to_game_music(self):
        """切换到游戏运行时音乐（带淡入淡出效果）"""
        self.stop_background_music(self.fade_duration)
        if self.load_background_music("assets/sound/run_background.mp3", "game"):
            # 等待淡出完成后再开始新音乐
            pygame.time.wait(self.fade_duration)
            return self.play_background_music(fade_ms=self.fade_duration)
        return False

    def is_music_loaded(self):
        """检查是否有音乐已加载"""
        return self.background_music is not None

    def get_current_music_type(self):
        """获取当前播放的音乐类型"""
        return self.current_music_type
