"""
贪吃蛇游戏主入口文件

版权所有 © 2025 "果香蛇踪"游戏开发团队
联系方式：3085678256@qq.com

本程序受版权法保护，未经授权禁止复制、修改、分发或用于商业用途。
"""
import pygame
from src.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    # 游戏主函数
    main()
