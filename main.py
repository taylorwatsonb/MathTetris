
import pygame
import random
import sys
from pygame.locals import *

pygame.init()
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
BLOCKSIZE = 30
BOARDWIDTH = 10
BOARDHEIGHT = 20
BOARDX = (WINDOWWIDTH - BOARDWIDTH * BLOCKSIZE) // 2
BOARDY = WINDOWHEIGHT - (BOARDHEIGHT * BLOCKSIZE)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
GRAY = (128, 128, 128)

DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Advanced Math Tetris')
FPSCLOCK = pygame.time.Clock()
FPS = 60

SHAPES = [
    [[1, 1], [1, 1]],  # Square
    [[1, 1, 1, 1]],    # Line
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
]

COLORS = [BLUE, RED, GREEN, YELLOW, PURPLE]

class Block:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = BOARDWIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.numbers = [[random.randint(1, 9) if cell else None for cell in row] 
                       for row in self.shape]
        
    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))
        self.numbers = list(zip(*self.numbers[::-1]))
        
    def move_down(self):
        self.y += 1
        
    def move_left(self):
        self.x -= 1
            
    def move_right(self):
        self.x += 1
        
    def copy(self):
        new_block = Block()
        new_block.shape = self.shape
        new_block.color = self.color
        new_block.x = self.x
        new_block.y = self.y
        new_block.numbers = self.numbers
        return new_block

class Game:
    def __init__(self):
        self.board = [[None for x in range(BOARDWIDTH)] for y in range(BOARDHEIGHT)]
        self.number_board = [[None for x in range(BOARDWIDTH)] for y in range(BOARDHEIGHT)]
        self.current_block = Block()
        self.next_block = Block()
        self.held_block = None
        self.can_hold = True
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.font = pygame.font.Font(None, 36)
        
    def draw(self):
        DISPLAYSURF.fill(BLACK)
        
        # Draw board
        pygame.draw.rect(DISPLAYSURF, WHITE, (BOARDX-2, BOARDY-2, 
                        BOARDWIDTH*BLOCKSIZE+4, BOARDHEIGHT*BLOCKSIZE+4), 2)
        
        if not self.paused:
            # Draw ghost piece
            ghost = self.current_block.copy()
            while self.can_move(dy=1, block=ghost):
                ghost.move_down()
            self.draw_shape(ghost, alpha=128)
            
            # Draw fallen blocks
            for y in range(BOARDHEIGHT):
                for x in range(BOARDWIDTH):
                    if self.board[y][x]:
                        self.draw_block(x, y, self.number_board[y][x], self.board[y][x])
            
            # Draw current block
            self.draw_shape(self.current_block)
            
            # Draw next block preview
            self.draw_next_block()
            
            # Draw held block
            self.draw_held_block()
        
        # Draw score and level
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        level_text = self.font.render(f'Level: {self.level}', True, WHITE)
        lines_text = self.font.render(f'Lines: {self.lines_cleared}', True, WHITE)
        DISPLAYSURF.blit(score_text, (10, 10))
        DISPLAYSURF.blit(level_text, (10, 50))
        DISPLAYSURF.blit(lines_text, (10, 90))
        
        if self.game_over:
            game_over_text = self.font.render('GAME OVER', True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2))
            DISPLAYSURF.blit(game_over_text, text_rect)
        elif self.paused:
            pause_text = self.font.render('PAUSED', True, WHITE)
            text_rect = pause_text.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2))
            DISPLAYSURF.blit(pause_text, text_rect)
        
    def draw_block(self, x, y, number, color, alpha=255):
        s = pygame.Surface((BLOCKSIZE-1, BLOCKSIZE-1))
        s.set_alpha(alpha)
        s.fill(color)
        DISPLAYSURF.blit(s, (BOARDX + x*BLOCKSIZE, BOARDY + y*BLOCKSIZE))
        
        if number is not None:
            number_text = self.font.render(str(number), True, BLACK)
            text_rect = number_text.get_rect(center=(BOARDX + x*BLOCKSIZE + BLOCKSIZE//2,
                                                   BOARDY + y*BLOCKSIZE + BLOCKSIZE//2))
            DISPLAYSURF.blit(number_text, text_rect)
            
    def draw_shape(self, block, alpha=255):
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell:
                    draw_x = block.x + x
                    draw_y = block.y + y
                    if 0 <= draw_y < BOARDHEIGHT:
                        self.draw_block(draw_x, draw_y, 
                                      block.numbers[y][x], block.color, alpha)
                        
    def draw_next_block(self):
        preview_x = BOARDX + BOARDWIDTH*BLOCKSIZE + 50
        preview_y = BOARDY + 50
        pygame.draw.rect(DISPLAYSURF, WHITE, 
                        (preview_x-2, preview_y-2, 5*BLOCKSIZE, 5*BLOCKSIZE), 2)
        
        for y, row in enumerate(self.next_block.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_block(x + (preview_x-BOARDX)//BLOCKSIZE,
                                  y + (preview_y-BOARDY)//BLOCKSIZE,
                                  self.next_block.numbers[y][x],
                                  self.next_block.color)
                    
    def draw_held_block(self):
        if self.held_block:
            hold_x = BOARDX - 6*BLOCKSIZE
            hold_y = BOARDY + 50
            pygame.draw.rect(DISPLAYSURF, WHITE, 
                           (hold_x-2, hold_y-2, 5*BLOCKSIZE, 5*BLOCKSIZE), 2)
            
            for y, row in enumerate(self.held_block.shape):
                for x, cell in enumerate(row):
                    if cell:
                        self.draw_block(x + (hold_x-BOARDX)//BLOCKSIZE,
                                      y + (hold_y-BOARDY)//BLOCKSIZE,
                                      self.held_block.numbers[y][x],
                                      self.held_block.color)
        
    def can_move(self, dx=0, dy=0, shape=None, block=None):
        if block is None:
            block = self.current_block
        if shape is None:
            shape = block.shape
            
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = block.x + x + dx
                    new_y = block.y + y + dy
                    if (new_x < 0 or new_x >= BOARDWIDTH or
                        new_y >= BOARDHEIGHT or
                        (new_y >= 0 and self.board[new_y][new_x])):
                        return False
        return True
        
    def can_rotate(self):
        rotated = list(zip(*self.current_block.shape[::-1]))
        return self.can_move(shape=rotated)
        
    def hard_drop(self):
        distance = 0
        while self.can_move(dy=1):
            self.current_block.move_down()
            distance += 1
        self.freeze_block()
        self.score += distance * 2  # Bonus points for hard drop
        
    def hold_piece(self):
        if self.can_hold:
            if self.held_block is None:
                self.held_block = self.current_block.copy()
                self.current_block = self.next_block
                self.next_block = Block()
            else:
                self.held_block, self.current_block = self.current_block.copy(), self.held_block.copy()
                self.current_block.x = BOARDWIDTH // 2 - len(self.current_block.shape[0]) // 2
                self.current_block.y = 0
            self.can_hold = False
        
    def freeze_block(self):
        for y, row in enumerate(self.current_block.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_y = self.current_block.y + y
                    board_x = self.current_block.x + x
                    if board_y >= 0:
                        self.board[board_y][board_x] = self.current_block.color
                        self.number_board[board_y][board_x] = self.current_block.numbers[y][x]
        
        self.check_lines()
        self.current_block = self.next_block
        self.next_block = Block()
        self.can_hold = True
        if not self.can_move():
            self.game_over = True
            
    def check_lines(self):
        lines_to_clear = []
        y = BOARDHEIGHT - 1
        while y >= 0:
            row = self.number_board[y]
            if all(cell is not None for cell in row):
                sum_numbers = sum(cell for cell in row if cell is not None)
                if sum_numbers % (10 + self.level) == 0:
                    lines_to_clear.append(y)
            y -= 1
            
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += (100 * len(lines_to_clear)) * self.level
            self.level = self.lines_cleared // 10 + 1
            
            for line in lines_to_clear:
                del self.board[line]
                del self.number_board[line]
                self.board.insert(0, [None for _ in range(BOARDWIDTH)])
                self.number_board.insert(0, [None for _ in range(BOARDWIDTH)])

def main():
    game = Game()
    fall_speed = 1000
    last_fall = pygame.time.get_ticks()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_p:
                    game.paused = not game.paused
                elif not game.game_over and not game.paused:
                    if event.key == K_LEFT and game.can_move(dx=-1):
                        game.current_block.move_left()
                    elif event.key == K_RIGHT and game.can_move(dx=1):
                        game.current_block.move_right()
                    elif event.key == K_DOWN and game.can_move(dy=1):
                        game.current_block.move_down()
                        last_fall = pygame.time.get_ticks()
                    elif event.key == K_UP and game.can_rotate():
                        game.current_block.rotate()
                    elif event.key == K_SPACE:
                        game.hard_drop()
                        last_fall = pygame.time.get_ticks()
                    elif event.key == K_c:
                        game.hold_piece()
        
        if not game.game_over and not game.paused:
            current_time = pygame.time.get_ticks()
            fall_speed = max(100, 1000 - (game.level - 1) * 100)
            
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
