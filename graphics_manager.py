import pygame
import math

class GraphicManager:
    def __init__(self):
        self.sheet = pygame.image.load("Graphic Designs/Player/Necromancer_creativekind-Sheet.png").convert_alpha()
        self.frame_width = 160
        self.frame_height = 128
        self.frame_index = 0
        self.animation_speed = 0.15 

        '''Abilities'''
        # all abilities is here (Or maybe add someday but Not Today!!!)
        self.sheet_shield = pygame.image.load("Graphic Designs/Abilities/8_protectioncircle_spritesheet.png").convert_alpha()
        self.spell_sheet = pygame.image.load("Graphic Designs/Abilities/16_sunburn_spritesheet.png").convert_alpha() # 64x64 frames
        self.nova_sheet = pygame.image.load("Graphic Designs/Abilities/7_firespin_spritesheet.png").convert_alpha()   # 128x128 frames
        self.hit_sheet = pygame.image.load("Graphic Designs/Abilities/5_magickahit_spritesheet.png").convert_alpha()  # 64x64 frames
        self.strike_sheet = pygame.image.load("Graphic Designs/Abilities/3_bluefire_spritesheet.png").convert_alpha() # 64x128 frames
        # self.spell_frame_index = 0
        self.shield_frame_index = 0

    def get_frame(self, sheet, row, frame, w, h):
        rect = pygame.Rect(frame * w, row * h, w, h)
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(sheet, (0, 0), rect)
        return image
    
    def draw_player(self, screen, pos, offset, state="idle"):
        # Map states to rows
        states = {"idle": 0, "run": 1, "attack": 2, "hurt": 4}
        row = states.get(state, 0)    
        self.frame_index += self.animation_speed
        if self.frame_index >= 8:
            self.frame_index = 0        
        current_image = self.get_frame(self.sheet, row, int(self.frame_index), self.frame_width, self.frame_height)

        '''Wobble Effect!!'''
        time = pygame.time.get_ticks()
        bob = math.sin(time / 300) * 8
        angle = math.cos(time / 400) * 4
        rotated_image = pygame.transform.rotate(current_image, angle) 

        '''Draw'''
        rect = rotated_image.get_rect(center=(pos.x + offset.x, pos.y + offset.y + bob))
        screen.blit(rotated_image, rect)

    def draw_shield(self, screen, pos, offset):
        self.shield_frame_index += 0.2
        if self.shield_frame_index >= 8:
            self.shield_frame_index = 0
        current_image = self.get_frame(self.sheet_shield, 0, int(self.shield_frame_index), 64, 64)

        big_fire = pygame.transform.scale(current_image, (120, 120))
        rect = big_fire.get_rect(center=(pos.x + offset.x, pos.y + offset.y))
        screen.blit(big_fire, rect)

class GameBackground:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.phases = []
        self.current_phase_index = 0
        
        self._load_images()

    def _load_images(self):
        for i in range(1, 11):
            path = f"Graphic Designs/Background/phase{i}.png"
            try:
                img = pygame.image.load(path).convert()
                # Scale +20px to prevent black edges during screen shake
                img = pygame.transform.scale(img, (self.width + 20, self.height + 20))
                self.phases.append(img)
            except pygame.error:
                print(f"Warning: Could not load {path}. Creating placeholder.")
                placeholder = pygame.Surface((self.width + 20, self.height + 20))
                placeholder.fill((20, 20, 30)) # Dark space color
                self.phases.append(placeholder)

    def update(self, game_phase):
        """Updates the internal phase index based on game difficulty."""
        # Ensure the index stays between 0 and 9
        self.current_phase_index = max(0, min(game_phase - 1, 9))

    def draw(self, screen, offset_x=0, offset_y=0):
        screen.blit(self.phases[self.current_phase_index], (-10 + offset_x, -10 + offset_y))

    