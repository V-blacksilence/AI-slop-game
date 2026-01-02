import pygame
import math
import random
from game.constants import *

class Enemy:
    def __init__(self, x, y, enemy_type='grunt', is_boss=False):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.is_boss = is_boss
        self.show_hitboxes = False
        # Get base stats from enemy type
        stats = ENEMY_TYPES[enemy_type].copy()
        
        # Apply boss multiplier
        if is_boss:
            stats['health'] *= BOSS_MULTIPLIER
            stats['damage'] *= BOSS_MULTIPLIER
            stats['speed'] *= 1.5
            stats['size'] *= 1.5
            stats['xp'] *= BOSS_MULTIPLIER * 2
        
        self.max_health = stats['health']
        self.health = self.max_health
        self.damage = stats['damage']
        self.speed = stats['speed']
        self.color = stats['color']
        self.size = int(stats['size'])
        self.xp = stats['xp']
        
        # AI state
        self.state = 'idle'  # idle, chase, attack, retreat
        self.attack_cooldown = 0
        self.attack_range = 60 if not is_boss else 100
        self.aggro_range = 400 if not is_boss else 600
        self.retreat_threshold = 0.3  # Retreat at 30% health
        
        # Wind-up attacks
        self.wind_up_duration = 30 if not is_boss else 50  # frames
        self.wind_up_timer = 0
        self.is_winding_up = False
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.target_x = x
        self.target_y = y
        
        # Patterns for bosses
        self.pattern_timer = 0
        self.pattern_phase = 0
        
    def update(self, player, enemies):
        distance_to_player = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update wind-up effect
        if self.is_winding_up:
            self.wind_up_timer -= 1
            if self.wind_up_timer <= 0:
                self.is_winding_up = False
                self.state = 'attack'
        # AI behavior
        action = None
        if self.is_boss:
            action = self._boss_ai(player, distance_to_player)
        else:
            action = self._normal_ai(player, distance_to_player)
        
        # Apply movement
        self.x += self.velocity_x
        self.y += self.velocity_y
    
        self.x = max(self.size, min(LEVEL_SIZE - self.size, self.x))
        self.y = max(self.size, min(LEVEL_SIZE - self.size, self.y))
        return action
    def _normal_ai(self, player, distance):
        # State transitions
        if distance > self.aggro_range:
            self.state = 'idle'
        elif distance <= self.attack_range * 1.5 and self.attack_cooldown <= 0:
            self.state = 'attack'
        elif self.health < self.max_health * self.retreat_threshold:
            self.state = 'retreat'
        else:
            self.state = 'chase'
        
        # Execute state behavior
        if self.state == 'idle':
            self.velocity_x = 0
            self.velocity_y = 0
        
        elif self.state == 'chase':
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.atan2(dy, dx)
            
            # Type-specific behavior
            if self.type == 'assassin':
                # Circle around player
                angle += math.sin(pygame.time.get_ticks() / 500) * 0.5
            
            self.velocity_x = math.cos(angle) * self.speed
            self.velocity_y = math.sin(angle) * self.speed
        
        elif self.state == 'wind_up':
            # Stop moving during wind-up
            self.velocity_x = 0
            self.velocity_y = 0
    
            # Execute attack after wind-up
            if self.wind_up_timer <= 0:
                self.is_winding_up = False
                self.attack_cooldown = 45
                return 'attack'
        
        elif self.state == 'attack':
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.atan2(dy, dx)
            self.velocity_x = math.cos(angle) * 0.5 * self.speed
            self.velocity_y = math.sin(angle) * 0.5 * self.speed
            self.attack_cooldown = 60
            return 'attack'
        
        elif self.state == 'retreat':
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.atan2(dy, dx) + math.pi  # Opposite direction
            
            self.velocity_x = math.cos(angle) * self.speed * 1.5
            self.velocity_y = math.sin(angle) * self.speed * 1.5
        
        return None
    
    def _boss_ai(self, player, distance):
        self.pattern_timer += 1
        
        # Boss patterns change every 3 seconds
        if self.pattern_timer > 180:
            self.pattern_timer = 0
            self.pattern_phase = (self.pattern_phase + 1) % 3
        
        if self.pattern_phase == 0:
            # Aggressive chase
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.atan2(dy, dx)
            self.velocity_x = math.cos(angle) * self.speed
            self.velocity_y = math.sin(angle) * self.speed
            
            if distance <= self.attack_range and self.attack_cooldown <= 0 and not self.is_winding_up:
                self.is_winding_up = True
                self.wind_up_timer = self.wind_up_duration
        
        elif self.pattern_phase == 1:
            # Circle and attack
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.atan2(dy, dx) + math.pi/4
            self.velocity_x = math.cos(angle) * self.speed * 1.2
            self.velocity_y = math.sin(angle) * self.speed * 1.2
            
            if self.attack_cooldown <= 0 and not self.is_winding_up:
                self.is_winding_up = True
                self.wind_up_timer = self.wind_up_duration
        
        else:
            # Enrage mode (low health)
            if self.health < self.max_health * 0.5:
                dx = player.x - self.x
                dy = player.y - self.y
                angle = math.atan2(dy, dx)
                self.velocity_x = math.cos(angle) * self.speed * 1.5
                self.velocity_y = math.sin(angle) * self.speed * 1.5
                
                if distance <= self.attack_range * 1.5 and self.attack_cooldown <= 0 and not self.is_winding_up:
                    self.is_winding_up = True
                    self.wind_up_timer = self.wind_up_duration
            else:
                self.velocity_x *= 0.9
                self.velocity_y *= 0.9
        
        return None
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

    def draw_wind_up_effect(self, screen, camera_offset):
        """Draw visual effect during wind-up"""
        if not self.is_winding_up:
            return
        
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        # Pulsing aura effect
        progress = 1 - (self.wind_up_timer / self.wind_up_duration)
        aura_size = self.size // 2 + int(15 * progress)
        
        # Flash color intensity
        flash_intensity = int(255 * (1 - progress))
        aura_color = (flash_intensity, 0, 0)  # Red for warning
        
        pygame.draw.circle(screen, aura_color, (int(draw_x), int(draw_y)), aura_size, 3)
        
        # Add warning indicator text/icon
        warning_size = 3 + int(5 * progress)
        pygame.draw.circle(screen, RED, (int(draw_x), int(draw_y - self.size//2 - 20)), warning_size)
    
    
    def draw(self, screen, camera_offset, show_hitboxes=False):
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        # Draw enemy
        color = self.color
        if self.is_boss:
            # Boss glow effect
            glow_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color[:3], 100), 
                            (self.size, self.size), self.size)
            screen.blit(glow_surface, 
                    (draw_x - self.size, draw_y - self.size))
        
        pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), self.size//2)
        
        # Draw wind-up effect
        self.draw_wind_up_effect(screen, camera_offset)
        
        # Draw hitboxes if enabled
        if self.show_hitboxes:
            # Attack range
            pygame.draw.circle(screen, RED, (int(draw_x), int(draw_y)), 
                            self.attack_range, 1)
            # Detection range
            pygame.draw.circle(screen, YELLOW, (int(draw_x), int(draw_y)), 
                            self.aggro_range, 1)
            # Collision box
            rect = self.get_rect()
            rect.x -= camera_offset[0]
            rect.y -= camera_offset[1]
            pygame.draw.rect(screen, GREEN, rect, 1)
        # Draw health bar
        bar_width = self.size
        bar_height = 5
        bar_x = draw_x - bar_width//2
        bar_y = draw_y - self.size//2 - 10
        
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        # Health
        health_width = (self.health / self.max_health) * bar_width
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Boss indicator
        if self.is_boss:
            font = pygame.font.Font(None, 24)
            text = font.render('BOSS', True, YELLOW)
            text_rect = text.get_rect(center=(draw_x, draw_y - self.size//2 - 25))
            screen.blit(text, text_rect)
