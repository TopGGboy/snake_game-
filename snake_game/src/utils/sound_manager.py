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
        self.music_end_event = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.music_end_event)
        
        # 预加载的音乐缓存
        self.music_cache = {}  # {music_type: music_path}
        self.preloaded_music = {}  # {music_type: loaded_music_object}
        
        # 音效相关属性
        self.sound_effects = {}  # 音效缓存 {sound_name: sound_object}
        self.sound_volume = 0.7  # 音效默认音量

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

    def preload_music(self, music_path, music_type):
        """预加载音乐到缓存"""
        if os.path.exists(music_path):
            self.music_cache[music_type] = music_path
            # 提前加载音乐文件到内存
            try:
                # 使用pygame.mixer.Sound预加载音乐
                sound = pygame.mixer.Sound(music_path)
                self.preloaded_music[music_type] = sound
                print(f"音乐已预加载到内存: {music_path} (类型: {music_type})")
            except Exception as e:
                print(f"预加载音乐到内存失败: {e}")
                # 仍然缓存路径，但使用传统加载方式
                print(f"音乐已预加载到缓存: {music_path} (类型: {music_type})")
            return True
        else:
            print(f"预加载音乐文件不存在: {music_path}")
            return False

    def get_preloaded_music(self, music_type):
        """获取预加载的音乐路径"""
        return self.music_cache.get(music_type)

    def play_background_music(self, loops=-1):
        """播放背景音乐"""
        if self.background_music and not self.is_music_playing:
            try:
                # 如果音乐已经在预加载缓存中，直接播放
                if self.current_music_type in self.preloaded_music:
                    pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                self.is_music_playing = True
                print("背景音乐开始播放")
                return True
            except Exception as e:
                print(f"播放背景音乐失败: {e}")
                return False
        return False

    def play_preloaded_music(self, music_type, loops=-1):
        """播放预加载的音乐"""
        if music_type in self.preloaded_music:
            # 使用预加载到内存的音乐
            try:
                sound = self.preloaded_music[music_type]
                # 立即停止当前音乐
                if self.is_music_playing:
                    self.stop_background_music()
                
                # 设置音乐类型
                self.current_music_type = music_type
                self.background_music = self.music_cache[music_type]
                # 播放预加载的音乐
                channel = sound.play(loops=loops)
                if channel:
                    self.is_music_playing = True
                    print(f"播放预加载音乐: {music_type}")
                    return True
            except Exception as e:
                print(f"播放预加载音乐失败: {e}")
        
        # 回退到传统方式
        if music_type in self.music_cache:
            music_path = self.music_cache[music_type]
            if self.load_background_music(music_path, music_type):
                return self.play_background_music(loops)
        return False

    def handle_music_events(self):
        """处理音乐事件，用于无缝循环"""
        for event in pygame.event.get(self.music_end_event):
            if event.type == self.music_end_event:
                # 音乐播放结束，重新开始播放实现无缝循环
                if self.is_music_playing:
                    try:
                        # 如果是预加载的音乐，使用Sound对象循环
                        if self.current_music_type in self.preloaded_music:
                            sound = self.preloaded_music[self.current_music_type]
                            channel = sound.play(loops=-1)
                            if channel:
                                print("预加载音乐无缝循环播放")
                        else:
                            # 传统方式循环
                            pygame.mixer.music.play()
                            print("音乐无缝循环播放")
                    except Exception as e:
                        print(f"音乐循环播放失败: {e}")

    def stop_background_music(self):
        """停止背景音乐"""
        if self.is_music_playing:
            # 如果是预加载的音乐，停止对应的Sound播放
            if self.current_music_type in self.preloaded_music:
                try:
                    sound = self.preloaded_music[self.current_music_type]
                    sound.stop()
                except Exception as e:
                    print(f"停止预加载音乐失败: {e}")
            else:
                # 传统方式停止
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
        """切换到主界面音乐"""
        # 使用预加载的音乐，避免重新加载文件
        if self.play_preloaded_music("main"):
            return True
        # 如果预加载失败，尝试直接加载
        elif self.load_background_music("assets/sound/main.mp3", "main"):
            # 立即停止当前音乐
            if self.is_music_playing:
                self.stop_background_music()
            return self.play_background_music()
        return False

    def switch_to_game_music(self):
        """切换到游戏运行时音乐"""
        # 使用预加载的音乐，避免重新加载文件
        if self.play_preloaded_music("game"):
            return True
        # 如果预加载失败，尝试直接加载
        elif self.load_background_music("assets/sound/run_background.mp3", "game"):
            # 立即停止当前音乐
            if self.is_music_playing:
                self.stop_background_music()
            return self.play_background_music()
        return False

    def is_music_loaded(self):
        """检查是否有音乐已加载"""
        return self.background_music is not None

    def get_current_music_type(self):
        """获取当前播放的音乐类型"""
        return self.current_music_type

    def initialize_preloading(self):
        """初始化预加载所有游戏音乐和音效"""
        # 预加载主界面音乐
        self.preload_music("assets/sound/main.mp3", "main")
        # 预加载游戏音乐
        self.preload_music("assets/sound/run_background.mp3", "game")
        
        # 预加载音效
        self.preload_sound_effect("assets/sound/eat.mp3", "eat")
        self.preload_sound_effect("assets/sound/high_speed.mp3", "high_speed")
        self.preload_sound_effect("assets/sound/game_over.mp3", "game_over")
        
        print("游戏音乐和音效预加载完成")

    def preload_sound_effect(self, sound_path, sound_name):
        """预加载音效到缓存"""
        if os.path.exists(sound_path):
            try:
                sound = pygame.mixer.Sound(sound_path)
                self.sound_effects[sound_name] = sound
                print(f"音效已预加载: {sound_path} (名称: {sound_name})")
                return True
            except Exception as e:
                print(f"预加载音效失败: {e}")
                return False
        else:
            print(f"音效文件不存在: {sound_path}")
            return False

    def play_sound_effect(self, sound_name):
        """播放音效"""
        if sound_name in self.sound_effects:
            try:
                sound = self.sound_effects[sound_name]
                sound.set_volume(self.sound_volume)
                sound.play()
                print(f"播放音效: {sound_name}")
                return True
            except Exception as e:
                print(f"播放音效失败: {e}")
                return False
        else:
            print(f"音效未找到: {sound_name}")
            return False

    def set_sound_volume(self, volume):
        """设置音效音量 (0.0 到 1.0)"""
        if 0.0 <= volume <= 1.0:
            self.sound_volume = volume
            return True
        return False

    def get_sound_volume(self):
        """获取当前音效音量"""
        return self.sound_volume

    def play_eat_sound(self):
        """播放吃食物音效"""
        return self.play_sound_effect("eat")

    def play_high_speed_sound(self):
        """播放加速音效"""
        return self.play_sound_effect("high_speed")

    def play_game_over_sound(self):
        """播放游戏结束音效"""
        return self.play_sound_effect("game_over")
