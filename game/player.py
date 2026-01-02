import pygame
import math
from game.constants import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.show_hitbox = False
        
        # Stats
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.max_stamina = PLAYER_MAX_STAMINA
        self.stamina = self.max_stamina
        self.damage = PLAYER_DAMAGE
        
        # Combat state
        self.is_dodging = False
        self.dodge_timer = 0
        self.dodge_direction = (0, 0)
        self.is_blocking = False
        self.block_timer = 0
        self.attack_cooldown = 0
        self.invulnerable = False
        
        # Stats tracking
        self.kills = 0
        self.perfect_dodges = 0
        self.perfect_blocks = 0
        self.damage_taken = 0
        self.damage_dealt = 0
        
        # Equipment
        self.weapon_level = 1
        self.armor_level = 1
        
        # Aiming
        self.aim_angle = 0
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        
    def update(self, keys, mouse_pos, level_bounds):
        # Stamina regeneration
        if not self.is_blocking and self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + PLAYER_STAMINA_REGEN)
        
        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Dodge mechanics
        if self.is_dodging:
            self.dodge_timer -= 1
            if self.dodge_timer <= 0:
                self.is_dodging = False
                self.invulnerable = False
            else:
                # Move in dodge direction
                speed = DODGE_DISTANCE / DODGE_DURATION
                self.x += self.dodge_direction[0] * speed
                self.y += self.dodge_direction[1] * speed
                self.invulnerable = True
        else:
            # Normal movement
            self.velocity_x = 0
            self.velocity_y = 0
            
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.velocity_y = -self.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.velocity_y = self.speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.velocity_x = -self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.velocity_x = self.speed
            
            # Normalize diagonal movement
            if self.velocity_x != 0 and self.velocity_y != 0:
                self.velocity_x *= 0.707
                self.velocity_y *= 0.707
            
            self.x += self.velocity_x
            self.y += self.velocity_y
        
        # Keep player in bounds
        self.x = max(self.size, min(level_bounds[0] - self.size, self.x))
        self.y = max(self.size, min(level_bounds[1] - self.size, self.y))
        
        # Blocking
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if self.stamina > 0 and not self.is_dodging:
                self.is_blocking = True
                self.block_timer += 1
                self.stamina = max(0, self.stamina - BLOCK_COST_PER_FRAME)
            else:
                self.is_blocking = False
                self.block_timer = 0
        else:
            self.is_blocking = False
            self.block_timer = 0
    
    def dodge(self, direction):
        if self.stamina >= DODGE_COST and not self.is_dodging:
            self.is_dodging = True
            self.dodge_timer = DODGE_DURATION
            self.stamina -= DODGE_COST
            
            # Normalize direction
            length = math.sqrt(direction[0]**2 + direction[1]**2)
            if length > 0:
                self.dodge_direction = (direction[0] / length, direction[1] / length)
            else:
                self.dodge_direction = (1, 0)
    
    def attack(self, mouse_pos):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = ATTACK_COOLDOWN
            # Calculate attack direction
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            angle = math.atan2(dy, dx)
            return angle
        return None
    
    def take_damage(self, damage, enemy_pos):
        if self.invulnerable:
            # Check if this is within perfect window
            frames_into_dodge = DODGE_DURATION - self.dodge_timer
            if frames_into_dodge <= PERFECT_DODGE_WINDOW:
                return 'perfect_dodge'
            return 'dodged'  # Normal dodge, not perfect
            
        if self.is_blocking:
            if self.block_timer <= PERFECT_BLOCK_WINDOW:
                self.perfect_blocks += 1
                return 'perfect_block'
            else:
                damage *= (1 - BLOCK_DAMAGE_REDUCTION)
                self.health -= damage
                self.damage_taken += damage
                return 'block'
        
        self.health -= damage
        self.damage_taken += damage
        return 'hit'
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def restore_stamina(self, amount):
        self.stamina = min(self.max_stamina, self.stamina + amount)
    
    def upgrade_weapon(self):
        self.weapon_level += 1
        self.damage += 5
    
    def upgrade_armor(self):
        self.armor_level += 1
        self.max_health += 10
        self.health += 10
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

    def draw_arrow(self, screen, camera_offset):
        """Draw aiming arrow pointing to mouse"""
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        arrow_length = 60
        arrow_width = 8
        arrow_head_size = 15
        
        # Calculate arrow end point
        end_x = draw_x + math.cos(self.aim_angle) * arrow_length
        end_y = draw_y + math.sin(self.aim_angle) * arrow_length
        
        # Draw arrow shaft
        pygame.draw.line(screen, YELLOW, (draw_x, draw_y), (end_x, end_y), arrow_width)
        
        # Draw arrow head (triangle)
        arrow_angle_offset = math.pi / 6  # 30 degrees
        
        left_x = end_x + math.cos(self.aim_angle + math.pi - arrow_angle_offset) * arrow_head_size
        left_y = end_y + math.sin(self.aim_angle + math.pi - arrow_angle_offset) * arrow_head_size
        
        right_x = end_x + math.cos(self.aim_angle + math.pi + arrow_angle_offset) * arrow_head_size
        right_y = end_y + math.sin(self.aim_angle + math.pi + arrow_angle_offset) * arrow_head_size
        
        pygame.draw.polygon(screen, YELLOW, [(end_x, end_y), (left_x, left_y), (right_x, right_y)])
    
    
    def draw(self, screen, camera_offset, show_hitbox=False):
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        # Draw player
        color = BLUE
        if self.is_dodging:
            color = YELLOW
        elif self.is_blocking:
            color = LIGHT_GRAY
        
        pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), self.size//2)
        
        # Draw direction indicator
        if not self.is_dodging:
            pygame.draw.circle(screen, WHITE, (int(draw_x), int(draw_y)), self.size//2, 2)

        # Draw aiming arrow
        self.draw_arrow(screen, camera_offset)
        
        # Draw hitbox
        if self.show_hitbox:
            # Collision circle
            pygame.draw.circle(screen, (0, 255, 0), (int(draw_x), int(draw_y)), self.size//2, 2)
            
            # Draw rect hitbox
            rect = self.get_rect()
            rect_x = rect.x - camera_offset[0]
            rect_y = rect.y - camera_offset[1]
            pygame.draw.rect(screen, (0, 255, 0), (rect_x, rect_y, rect.width, rect.height), 1)
            
            # Draw center point
            pygame.draw.circle(screen, (255, 0, 0), (int(draw_x), int(draw_y)), 3)