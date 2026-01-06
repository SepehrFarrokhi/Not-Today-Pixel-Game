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
        self.spell_sheet = pygame.image.load("Graphic Designs/Abilities/9_brightfire_spritesheet.png").convert_alpha() # 64x64 frames
        self.nova_sheet = pygame.image.load("Graphic Designs/Abilities/7_firespin_spritesheet.png").convert_alpha()   # 128x128 frames
        self.hit_sheet = pygame.image.load("Graphic Designs/Abilities/5_magickahit_spritesheet.png").convert_alpha()  # 64x64 frames
        self.strike_sheet = pygame.image.load("Graphic Designs/Abilities/3_bluefire_spritesheet.png").convert_alpha() # 64x128 frames
        self.spell_frame_index = 0
        self.shield_frame_index = 0

    def get_frame(self, sheet, row, frame, w, h):
        rect = pygame.Rect(frame * w, row * h, w, h)
        image = pygame.Surface(rect.size, pygame.SRCALPHA)
        image.blit(sheet, (0, 0), rect)
        return image
    
    def draw_player(self, screen, pos, offset, state="idle"):
        # Map states to rows
        states = {"idle": 0, "run": 1, "attack": 2, "hurt": 4}
        row = states.get(state, 0)    
        self.frame_index += self.animation_speed
        if self.frame_index >= 8:
            self.frame_index = 0        
        current_image = self.get_frame(self.sheet, int(self.frame_index), row, self.frame_width, self.frame_height)

        '''Wobble Effect!!'''
        time = pygame.time.get_ticks()
        bob = math.sin(time / 300) * 8
        angle = math.cos(time / 400) * 4
        rotated_image = pygame.transform.rotate(current_image, angle) 

        '''Draw'''
        rect = rotated_image.get_rect(center=(pos.x + offset.x, pos.y + offset.y + bob))
        screen.blit(current_image, rect)

    def draw_shield(self, screen, pos, offset):
        self.shield_frame_index += 0.2
        if self.shield_frame_index >= 8:
            self.shield_frame_index = 0
        current_image = self.get_frame(self.sheet_shield, 0, int(self.spell_frame_index), 100, 100)
        rect = current_image.get_rect(center=(pos.x + offset.x, pos.y + offset.y))
        screen.blit(current_image, rect)
