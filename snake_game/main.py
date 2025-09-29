"""
贪吃蛇游戏主入口文件
"""
import pygame
from src.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
