
import pygame
import random
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
BLOCKSIZE = 30
BOARDWIDTH = 10
BOARDHEIGHT = 20
BOARDX = (WINDOWWIDTH - BOARDWIDTH * BLOCKSIZE) // 2
BOARDY = WINDOWHEIGHT - (BOARDHEIGHT * BLOCKSIZE)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Initialize display
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Math Tetris')
FPSCLOCK = pygame.time.Clock()
FPS = 30

class Block:
    def __init__(self):
        self.x = BOARDWIDTH // 2 - 1
        self.y = 0
        self.number = random.randint(1, 20)
        self.color = BLUE
        
    def move_down(self):
        self.y += 1
        
    def move_left(self):
        if self.x > 0:
            self.x -= 1
            
    def move_right(self):
        if self.x < BOARDWIDTH - 1:
            self.x += 1

class Game:
    def __init__(self):
        self.board = [[None for x in range(BOARDWIDTH)] for y in range(BOARDHEIGHT)]
        self.current_block = Block()
        self.game_over = False
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        
    def draw(self):
        DISPLAYSURF.fill(BLACK)
        
        # Draw board
        pygame.draw.rect(DISPLAYSURF, WHITE, (BOARDX-2, BOARDY-2, 
                        BOARDWIDTH*BLOCKSIZE+4, BOARDHEIGHT*BLOCKSIZE+4), 2)
        
        # Draw fallen blocks
        for y in range(BOARDHEIGHT):
            for x in range(BOARDWIDTH):
                if self.board[y][x]:
                    self.draw_block(x, y, self.board[y][x])
        
        # Draw current block
        self.draw_block(self.current_block.x, self.current_block.y, 
                       self.current_block.number, self.current_block.color)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        DISPLAYSURF.blit(score_text, (10, 10))
        
    def draw_block(self, x, y, number, color=WHITE):
        pygame.draw.rect(DISPLAYSURF, color,
                        (BOARDX + x*BLOCKSIZE, BOARDY + y*BLOCKSIZE,
                         BLOCKSIZE-1, BLOCKSIZE-1))
        number_text = self.font.render(str(number), True, BLACK)
        text_rect = number_text.get_rect(center=(BOARDX + x*BLOCKSIZE + BLOCKSIZE//2,
                                               BOARDY + y*BLOCKSIZE + BLOCKSIZE//2))
        DISPLAYSURF.blit(number_text, text_rect)
        
    def can_move(self, dx=0, dy=0):
        new_x = self.current_block.x + dx
        new_y = self.current_block.y + dy
        return (0 <= new_x < BOARDWIDTH and 
                new_y < BOARDHEIGHT and 
                (new_y < 0 or self.board[new_y][new_x] is None))
        
    def freeze_block(self):
        self.board[self.current_block.y][self.current_block.x] = self.current_block.number
        self.check_lines()
        self.current_block = Block()
        if not self.can_move():
            self.game_over = True
            
    def check_lines(self):
        y = BOARDHEIGHT - 1
        while y >= 0:
            row = self.board[y]
            if all(cell is not None for cell in row):
                sum_numbers = sum(cell for cell in row)
                if sum_numbers % 10 == 0:  # Clear line if sum is divisible by 10
                    self.score += 100
                    del self.board[y]
                    self.board.insert(0, [None for _ in range(BOARDWIDTH)])
                else:
                    y -= 1
            else:
                y -= 1

def main():
    game = Game()
    fall_time = 0
    fall_speed = 1000  # Time in milliseconds before block falls
    last_fall = pygame.time.get_ticks()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if not game.game_over:
                    if event.key == K_LEFT:
                        if game.can_move(dx=-1):
                            game.current_block.move_left()
                    elif event.key == K_RIGHT:
                        if game.can_move(dx=1):
                            game.current_block.move_right()
                    elif event.key == K_DOWN:
                        if game.can_move(dy=1):
                            game.current_block.move_down()
                            last_fall = pygame.time.get_ticks()
        
        # Handle block falling
        if not game.game_over:
            current_time = pygame.time.get_ticks()
            if current_time - last_fall > fall_speed:
                if game.can_move(dy=1):
                    game.current_block.move_down()
                else:
                    game.freeze_block()
                last_fall = current_time
        
        game.draw()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    main()
