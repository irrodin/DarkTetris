import pygame
import random
import sys

# No images, only code :D



pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30


DARK_THEME = {
    'background': (10, 10, 20),
    'grid': (30, 30, 40),
    'text': (200, 200, 200),
    'highlight': (80, 80, 100),
    'border': (60, 60, 80)
}


COLORS = [
    (0, 0, 0),      
    (255, 85, 85),  
    (100, 200, 115),  
    (65, 105, 225),   
    (255, 140, 50),   
    (255, 215, 0),    
    (138, 43, 226),   
    (0, 255, 255)     
]

# Фигуры и их вращения
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],     # I
    [[4, 5, 9, 10], [2, 6, 5, 9]],     # Z
    [[6, 7, 9, 10], [1, 5, 6, 10]],    # S
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # L
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # J
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],     # T
    [[1, 2, 5, 6]],  # O
]

class Piece:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(SHAPES) - 1)
        self.color = random.randint(1, len(COLORS) - 1)
        self.rotation = 0
        self.shadow_y = 0
        
    def image(self):
        return SHAPES[self.type][self.rotation]
    
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(SHAPES[self.type])

class TetrisGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.level = 1
        self.score = 0
        self.lines = 0
        self.state = "start"
        self.field = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.piece = None
        self.next_piece = Piece(3, 0)
        self.new_piece()
        self.game_over = False
        self.paused = False
        self.hold_piece = None
        self.can_hold = True
        
    def new_piece(self):
        self.piece = self.next_piece
        self.next_piece = Piece(3, 0)
        self.can_hold = True
        self.calculate_shadow()
        
    def calculate_shadow(self):
        self.piece.shadow_y = self.piece.y
        while not self.check_collision(self.piece.x, self.piece.shadow_y + 1, self.piece.rotation):
            self.piece.shadow_y += 1
    
    def check_collision(self, x=None, y=None, rotation=None):
        if x is None: x = self.piece.x
        if y is None: y = self.piece.y
        if rotation is None: rotation = self.piece.rotation
        
        for i in range(4):
            for j in range(4):
                if i * 4 + j in SHAPES[self.piece.type][rotation]:
                    if (x + j < 0 or x + j >= GRID_WIDTH or 
                        y + i >= GRID_HEIGHT or 
                        (y + i >= 0 and self.field[y + i][x + j] > 0)):
                        return True
        return False
    
    def freeze_piece(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.piece.image():
                    if self.piece.y + i >= 0:
                        self.field[self.piece.y + i][self.piece.x + j] = self.piece.color
        
        self.clear_lines()
        self.new_piece()
        
        if self.check_collision():
            self.state = "gameover"
    
    def clear_lines(self):
        lines_cleared = 0
        for i in range(GRID_HEIGHT):
            if all(self.field[i]):
                lines_cleared += 1
                for j in range(i, 0, -1):
                    self.field[j] = self.field[j-1][:]
                self.field[0] = [0 for _ in range(GRID_WIDTH)]
        
        if lines_cleared > 0:
            self.lines += lines_cleared
            self.score += (lines_cleared ** 2) * 100 * self.level
            self.level = 1 + self.lines // 10
    
    def hold_current_piece(self):
        if not self.can_hold:
            return
            
        if self.hold_piece is None:
            self.hold_piece = Piece(3, 0)
            self.hold_piece.type = self.piece.type
            self.hold_piece.color = self.piece.color
            self.new_piece()
        else:
            self.hold_piece.type, self.piece.type = self.piece.type, self.hold_piece.type
            self.hold_piece.color, self.piece.color = self.piece.color, self.hold_piece.color
            self.piece.x, self.piece.y = 3, 0
            if self.check_collision():
                self.state = "gameover"
        
        self.can_hold = False
    
    def move(self, dx):
        if not self.check_collision(self.piece.x + dx, self.piece.y):
            self.piece.x += dx
            self.calculate_shadow()
    
    def rotate_piece(self):
        old_rotation = self.piece.rotation
        self.piece.rotate()
        if self.check_collision():
            self.piece.rotation = old_rotation
        self.calculate_shadow()
    
    def drop_piece(self):
        while not self.check_collision(self.piece.x, self.piece.y + 1):
            self.piece.y += 1
        self.freeze_piece()
    
    def step(self):
        if not self.check_collision(self.piece.x, self.piece.y + 1):
            self.piece.y += 1
        else:
            self.freeze_piece()

class TetrisApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dark Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.big_font = pygame.font.SysFont('Arial', 50, bold=True)
        self.game = TetrisGame()
        self.fps = 60
        self.counter = 0
        self.pressing_down = False
        self.grid_x = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
        self.grid_y = SCREEN_HEIGHT - (GRID_HEIGHT + 2) * BLOCK_SIZE
    
    def draw_block(self, x, y, color, shadow=False):
        
        pygame.draw.rect(self.screen, color, 
                        (x+1, y+1, BLOCK_SIZE-2, BLOCK_SIZE-2))
        
      
        if not shadow:
           
            pygame.draw.line(self.screen, 
                           (min(color[0]+60, 255), min(color[1]+60, 255), min(color[2]+60, 255)), 
                           (x+1, y+1), (x+BLOCK_SIZE-2, y+1), 2)
            pygame.draw.line(self.screen, 
                           (min(color[0]+60, 255), min(color[1]+60, 255), min(color[2]+60, 255)), 
                           (x+1, y+1), (x+1, y+BLOCK_SIZE-2), 2)
            
           
            pygame.draw.line(self.screen, 
                           (max(color[0]-60, 0), max(color[1]-60, 0), max(color[2]-60, 0)), 
                           (x+1, y+BLOCK_SIZE-2), (x+BLOCK_SIZE-2, y+BLOCK_SIZE-2), 2)
            pygame.draw.line(self.screen, 
                           (max(color[0]-60, 0), max(color[1]-60, 0), max(color[2]-60, 0)), 
                           (x+BLOCK_SIZE-2, y+1), (x+BLOCK_SIZE-2, y+BLOCK_SIZE-2), 2)
    
    def draw_grid(self):
       
        pygame.draw.rect(self.screen, DARK_THEME['grid'], 
                        (self.grid_x, self.grid_y, 
                         GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
        
    
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, DARK_THEME['border'], 
                               (self.grid_x + j * BLOCK_SIZE, 
                                self.grid_y + i * BLOCK_SIZE, 
                                BLOCK_SIZE, BLOCK_SIZE), 1)
                
                if self.game.field[i][j] > 0:
                    self.draw_block(self.grid_x + j * BLOCK_SIZE, 
                                  self.grid_y + i * BLOCK_SIZE, 
                                  COLORS[self.game.field[i][j]])
    
    def draw_current_piece(self):
        if self.game.piece:
            
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in self.game.piece.image():
                        self.draw_block(self.grid_x + (self.game.piece.x + j) * BLOCK_SIZE, 
                                          self.grid_y + (self.game.piece.shadow_y + i) * BLOCK_SIZE, 
                                          COLORS[self.game.piece.color], shadow=True)
            
           
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in self.game.piece.image():
                        self.draw_block(self.grid_x + (self.game.piece.x + j) * BLOCK_SIZE, 
                                      self.grid_y + (self.game.piece.y + i) * BLOCK_SIZE, 
                                      COLORS[self.game.piece.color])
    
    def draw_next_piece(self):
        if self.game.next_piece:
           
            text = self.font.render("NEXT:", True, DARK_THEME['text'])
            self.screen.blit(text, (self.grid_x + GRID_WIDTH * BLOCK_SIZE + 30, 30))
            
            
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in SHAPES[self.game.next_piece.type][0]:
                        self.draw_block(self.grid_x + GRID_WIDTH * BLOCK_SIZE + 50 + j * BLOCK_SIZE, 
                                     100 + i * BLOCK_SIZE, 
                                     COLORS[self.game.next_piece.color])
    
    def draw_hold_piece(self):
   
        text = self.font.render("HOLD:", True, DARK_THEME['text'])
        self.screen.blit(text, (30, 30))
        
        if self.game.hold_piece:
          
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in SHAPES[self.game.hold_piece.type][0]:
                        self.draw_block(50 + j * BLOCK_SIZE, 
                                     100 + i * BLOCK_SIZE, 
                                     COLORS[self.game.hold_piece.color])
    
    def draw_info_panel(self):
       
        score_text = self.font.render(f"SCORE: {self.game.score}", True, DARK_THEME['text'])
        self.screen.blit(score_text, (30, 250))
        
        
        level_text = self.font.render(f"LEVEL: {self.game.level}", True, DARK_THEME['text'])
        self.screen.blit(level_text, (30, 300))
        
      
        lines_text = self.font.render(f"LINES: {self.game.lines}", True, DARK_THEME['text'])
        self.screen.blit(lines_text, (30, 350))
        
        
        controls_text = [
            "CONTROLS:",
            "← → - Move",
            "↑ - Rotate",
            "↓ - Soft Drop",
            "SPACE - Hard Drop",
            "C - Hold",
            "P - Pause",
            "R - Restart"
        ]
        
        for i, text in enumerate(controls_text):
            control = self.font.render(text, True, DARK_THEME['text'] if i > 0 else DARK_THEME['highlight'])
            self.screen.blit(control, (30, 400 + i * 25))
    
    def draw_game_over(self):
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
      
        text = self.big_font.render("GAME OVER", True, (255, 85, 85))
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(text, text_rect)
        
        restart = self.font.render("Press R to restart", True, DARK_THEME['text'])
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(restart, restart_rect)
    
    def draw_pause_screen(self):
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
      
        text = self.big_font.render("PAUSED", True, DARK_THEME['highlight'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(text, text_rect)
        
        restart = self.font.render("Press P to continue", True, DARK_THEME['text'])
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(restart, restart_rect)
    
    def run(self):
        running = True
        while running:
            self.counter += 1
            if self.counter > 100000:
                self.counter = 0
            
           
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r and self.game.state == "gameover":
                        self.game.reset()
                    if event.key == pygame.K_p:
                        self.game.paused = not self.game.paused
                    if not self.game.paused and self.game.state == "start":
                        if event.key == pygame.K_UP:
                            self.game.rotate_piece()
                        if event.key == pygame.K_DOWN:
                            self.pressing_down = True
                        if event.key == pygame.K_LEFT:
                            self.game.move(-1)
                        if event.key == pygame.K_RIGHT:
                            self.game.move(1)
                        if event.key == pygame.K_SPACE:
                            self.game.drop_piece()
                        if event.key == pygame.K_c:
                            self.game.hold_current_piece()
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.pressing_down = False
            
           
            if not self.game.paused and self.game.state == "start":
                if self.counter % (self.fps // (self.game.level + 3)) == 0 or self.pressing_down:
                    self.game.step()
            
            
            self.screen.fill(DARK_THEME['background'])
            
            
            self.draw_grid()
            self.draw_current_piece()
            
            
            self.draw_next_piece()
            self.draw_hold_piece()
            self.draw_info_panel()
            
         
            if self.game.state == "gameover":
                self.draw_game_over()
            elif self.game.paused:
                self.draw_pause_screen()
            
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = TetrisApp()
    app.run()

