"""
显示和界面处理
"""
import pygame


class Display:
    def __init__(self, config):
        self.config = config
        self.screen = pygame.display.set_mode(
            (config.screen_width, config.screen_height)
        )
        pygame.display.set_caption("贪吃蛇游戏")

    def draw(self, snake, food):
        """绘制游戏界面"""
        self.screen.fill(self.config.bg_color)
        snake.draw(self.screen)
        food.draw(self.screen)
        self.draw_score(snake.score)
        pygame.display.update()

    def draw_score(self, score):
        """绘制分数"""
        score_text = self.config.font.render(f"分数: {score}", True, self.config.text_color)
        self.screen.blit(score_text, (10, 10))

    def draw_game_over(self, score):
        """绘制游戏结束界面"""
        self.screen.fill(self.config.bg_color)

        game_over_text = self.config.font.render("游戏结束!", True, self.config.text_color)
        score_text = self.config.font.render(f"最终分数: {score}", True, self.config.text_color)
        restart_text = self.config.font.render("按R键重新开始", True, self.config.text_color)

        self.screen.blit(game_over_text,
                         (self.config.screen_width // 2 - game_over_text.get_width() // 2,
                          self.config.screen_height // 2 - 60))
        self.screen.blit(score_text,
                         (self.config.screen_width // 2 - score_text.get_width() // 2,
                          self.config.screen_height // 2))
        self.screen.blit(restart_text,
                         (self.config.screen_width // 2 - restart_text.get_width() // 2,
                          self.config.screen_height // 2 + 60))

        pygame.display.update()