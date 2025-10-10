"""
性能监控工具

版权所有 © 2025 "果香蛇踪"游戏开发团队
联系方式：3085678256@qq.com

本程序受版权法保护，未经授权禁止复制、修改、分发或用于商业用途。
"""
import time
import pygame
from typing import Dict, List
from collections import deque
from .font_manager import get_font_manager


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_samples: int = 60):
        self.max_samples = max_samples
        self.frame_times: deque = deque(maxlen=max_samples)
        self.update_times: deque = deque(maxlen=max_samples)
        self.draw_times: deque = deque(maxlen=max_samples)
        
        self.last_frame_time = time.time()
        self.frame_count = 0
        
        # 性能统计
        self.stats = {
            'fps': 0.0,
            'avg_frame_time': 0.0,
            'avg_update_time': 0.0,
            'avg_draw_time': 0.0,
            'min_fps': float('inf'),
            'max_fps': 0.0
        }
        
        self.show_stats = False
        
    def start_frame(self):
        """开始新帧的计时"""
        current_time = time.time()
        if self.frame_count > 0:
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)
        
        self.last_frame_time = current_time
        self.frame_count += 1
        
    def start_update_timing(self):
        """开始更新阶段计时"""
        self.update_start_time = time.time()
        
    def end_update_timing(self):
        """结束更新阶段计时"""
        if hasattr(self, 'update_start_time'):
            update_time = time.time() - self.update_start_time
            self.update_times.append(update_time)
            
    def start_draw_timing(self):
        """开始绘制阶段计时"""
        self.draw_start_time = time.time()
        
    def end_draw_timing(self):
        """结束绘制阶段计时"""
        if hasattr(self, 'draw_start_time'):
            draw_time = time.time() - self.draw_start_time
            self.draw_times.append(draw_time)
    
    def update_stats(self):
        """更新性能统计"""
        if len(self.frame_times) > 0:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            self.stats['fps'] = current_fps
            self.stats['avg_frame_time'] = avg_frame_time * 1000  # 转换为毫秒
            self.stats['min_fps'] = min(self.stats['min_fps'], current_fps)
            self.stats['max_fps'] = max(self.stats['max_fps'], current_fps)
            
        if len(self.update_times) > 0:
            self.stats['avg_update_time'] = (sum(self.update_times) / len(self.update_times)) * 1000
            
        if len(self.draw_times) > 0:
            self.stats['avg_draw_time'] = (sum(self.draw_times) / len(self.draw_times)) * 1000
    
    def toggle_display(self):
        """切换性能显示"""
        self.show_stats = not self.show_stats
        
    def draw_stats(self, surface: pygame.Surface):
        """绘制性能统计信息"""
        if not self.show_stats:
            return
            
        self.update_stats()
        
        font_manager = get_font_manager()
        y_offset = 10
        line_height = 25
        
        stats_text = [
            f"FPS: {self.stats['fps']:.1f}",
            f"Frame Time: {self.stats['avg_frame_time']:.2f}ms",
            f"Update Time: {self.stats['avg_update_time']:.2f}ms",
            f"Draw Time: {self.stats['avg_draw_time']:.2f}ms",
            f"Min FPS: {self.stats['min_fps']:.1f}",
            f"Max FPS: {self.stats['max_fps']:.1f}"
        ]
        
        # 绘制半透明背景
        bg_rect = pygame.Rect(5, 5, 200, len(stats_text) * line_height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(128)
        bg_surface.fill((0, 0, 0))
        surface.blit(bg_surface, bg_rect)
        
        # 绘制文本
        for i, text in enumerate(stats_text):
            color = (255, 255, 255)
            if "FPS:" in text and self.stats['fps'] < 30:
                color = (255, 100, 100)  # 低FPS时显示红色
            elif "FPS:" in text and self.stats['fps'] > 50:
                color = (100, 255, 100)  # 高FPS时显示绿色
                
            text_surface = font_manager.render_text(text, 'medium', color)
            surface.blit(text_surface, (10, y_offset + i * line_height))
    
    def get_performance_report(self) -> Dict:
        """获取性能报告"""
        self.update_stats()
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计数据"""
        self.frame_times.clear()
        self.update_times.clear()
        self.draw_times.clear()
        self.stats['min_fps'] = float('inf')
        self.stats['max_fps'] = 0.0
        self.frame_count = 0