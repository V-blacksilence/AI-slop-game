import pygame
import math
import random
from game.constants import *

class Enemy:
    def __init__(self, x, y, enemy_type='grunt', is_boss=False, level_number = 1):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.is_boss = is_boss
        self.show_hitboxes = False
        self.level_number = level_number
        # Get base stats from enemy type
        stats = ENEMY_TYPES[enemy_type].copy()

        # Apply level scaling
        if level_number > 1:
            scale = level_number - 1
            stats['health'] *= (DIFFICULTY_SCALING['enemy_health'] ** scale)
            stats['damage'] *= (DIFFICULTY_SCALING['enemy_damage'] ** scale)
            stats['speed'] *= (DIFFICULTY_SCALING['enemy_speed'] ** scale)
            stats['xp'] *= (DIFFICULTY_SCALING['soul_bonus'] ** scale)
               
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
        self.xp = int(stats['xp'])
        
        # AI state
        self.state = 'idle'  # idle, chase, attack, retreat
        self.attack_cooldown = 0
        self.attack_range = 60 if not is_boss else 100
        self.aggro_range = 400 if not is_boss else 600
        self.retreat_threshold = 0.3  # Retreat at 30% health
        self.wind_up_duration = 30 if not is_boss else 50  # frames # Wind-up attacks
        self.wind_up_timer = 0
        self.attack_warning = 0

        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.target_x = x
        self.target_y = y
        
        # Patterns for bosses
        self.pattern_timer = 0
        self.pattern_phase = 0
        # Pending attack used during wind-up to store attack type for bosses
        self.pending_attack = None
        # Whether we've spawned a wind-up VFX for the current wind-up
        self.windup_vfx_spawned = False
        # Fixed attack target for non-boss attacks (set at wind-up start)
        self.attack_target = None
        self.attack_target_fixed = False
        
    def update(self, player, enemies, vfx=None):
        distance_to_player = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update wind-up effect
        if self.wind_up_timer > 0:
            # spawn windup vfx once when wind_up_timer active
            if vfx and self.pending_attack and not self.windup_vfx_spawned:
                # If this was a fixed attack target (non-boss), create windup pointing to fixed target
                if self.attack_target_fixed and self.attack_target:
                    tx, ty = self.attack_target
                    vfx.create_windup(self.x, self.y, tx, ty, duration=self.wind_up_duration)
                else:
                    # Boss or tracking attacks: create a tracking windup that follows the player
                    try:
                        vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration, track_target=True, target_getter=lambda p=player: (p.x, p.y))
                    except TypeError:
                        # fallback for older signature
                        vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration)
                self.windup_vfx_spawned = True

            self.wind_up_timer -= 1
            if self.wind_up_timer <= 0:
                self.state = 'attack'
                # Set cooldown based on pending attack type
                if self.pending_attack == 'ranged attack':
                    self.attack_cooldown = 20
                elif self.pending_attack == 'aoe attack':
                    self.attack_cooldown = 30
                else:
                    self.attack_cooldown = 60
                action = self.pending_attack or 'attack'
                self.pending_attack = None
                self.windup_vfx_spawned = False
                return action
            
        #Update warning
        if self.attack_warning > 0:
            self.attack_warning -= 1
        

        # AI behavior
        action = None
        if self.is_boss:
            action = self._boss_ai(player, distance_to_player, vfx)
        else:
            action = self._normal_ai(player, distance_to_player, vfx)
        
        # Apply movement during windup
        if self.wind_up_timer > 0:
            self.velocity_x *= 0.3
            self.velocity_y *= 0.3
        
        # Apply movement
        self.x += self.velocity_x
        self.y += self.velocity_y
    
        self.x = max(self.size, min(LEVEL_SIZE - self.size, self.x))
        self.y = max(self.size, min(LEVEL_SIZE - self.size, self.y))
        return action
    def _normal_ai(self, player, distance, vfx=None):
        #Don't change state during windup
        if self.wind_up_timer > 0:
            self.state = 'windup'
            return None
        
        # State transitions
        if distance > self.aggro_range:
            self.state = 'idle'
        elif distance <= self.attack_range * 1.5 and self.attack_cooldown <= 0:
            self.state = 'windup'
            self.wind_up_timer = self.wind_up_duration
            self.pending_attack = 'attack'
            # For non-boss, lock attack target now
            if not self.is_boss:
                self.attack_target = (player.x, player.y)
                self.attack_target_fixed = True
            else:
                self.attack_target = None
                self.attack_target_fixed = False
            if vfx and not self.windup_vfx_spawned:
                if self.attack_target_fixed and self.attack_target:
                    tx, ty = self.attack_target
                    vfx.create_windup(self.x, self.y, tx, ty, duration=self.wind_up_duration)
                else:
                    try:
                        vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration, track_target=True, target_getter=lambda p=player: (p.x, p.y))
                    except TypeError:
                        vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration)
                self.windup_vfx_spawned = True
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
            # Slow movement during windup, face player
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.atan2(dy, dx)
            self.velocity_x = math.cos(angle) * self.speed * 0.2
            self.velocity_y = math.sin(angle) * self.speed * 0.2
        
        
        elif self.state == 'retreat':
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.atan2(dy, dx) + math.pi  # Opposite direction
            
            self.velocity_x = math.cos(angle) * self.speed * 1.5
            self.velocity_y = math.sin(angle) * self.speed * 1.5
        
        return None
    
    def _boss_ai(self, player, distance, vfx=None):
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
            
            if distance <= self.attack_range and self.attack_cooldown <= 0:
                self.state = 'windup'
                self.wind_up_timer = self.wind_up_duration
                self.pending_attack = 'attack'
                # Boss: don't fix target, allow tracking
                self.attack_target = None
                self.attack_target_fixed = False
                if vfx and not self.windup_vfx_spawned:
                    try:
                        vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration, track_target=True, target_getter=lambda p=player: (p.x, p.y))
                    except TypeError:
                        vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration)
                    self.windup_vfx_spawned = True
        
        elif self.pattern_phase == 1:
            # Circle and attack
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.atan2(dy, dx) + math.pi/4
            self.velocity_x = math.cos(angle) * self.speed * 1.2
            self.velocity_y = math.sin(angle) * self.speed * 1.2
            
            if self.attack_cooldown <= 0 :
                self.state = 'windup'
                self.wind_up_timer = self.wind_up_duration
                self.pending_attack = 'ranged attack'
                # range attack: boss can track
                self.attack_target = None
                self.attack_target_fixed = False
                if vfx and not self.windup_vfx_spawned:
                    try:
                        vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration, track_target=True, target_getter=lambda p=player: (p.x, p.y))
                    except TypeError:
                        vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration)
                    self.windup_vfx_spawned = True
        
        else:
            # Enrage mode (low health)
            if self.health < self.max_health * 0.5:
                dx = player.x - self.x
                dy = player.y - self.y
                angle = math.atan2(dy, dx)
                self.velocity_x = math.cos(angle) * self.speed * 1.5
                self.velocity_y = math.sin(angle) * self.speed * 1.5
                
                if distance <= self.attack_range * 1.5 and self.attack_cooldown <= 0:
                    self.state = 'windup'
                    self.wind_up_timer = self.wind_up_duration
                    self.pending_attack = 'aoe attack'
                    # enrage aoe should track boss target (player)
                    self.attack_target = None
                    self.attack_target_fixed = False
                    if vfx and not self.windup_vfx_spawned:
                        try:
                            vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration, track_target=True, target_getter=lambda p=player: (p.x, p.y))
                        except TypeError:
                            vfx.create_windup(self.x, self.y, player.x, player.y, duration=self.wind_up_duration)
                        self.windup_vfx_spawned = True
            else:
                self.velocity_x *= 0.9
                self.velocity_y *= 0.9
        
        return None
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

    def get_hitbox(self):
        """Get visible hitbox rectangle"""
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)        

    
    def draw(self, screen, camera_offset, show_hitbox=True, prediction_bonus=0):
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        # Draw hitbox
        if show_hitbox:
            hitbox = self.get_hitbox()
            hitbox_screen = pygame.Rect(
                hitbox.x - camera_offset[0],
                hitbox.y - camera_offset[1],
                hitbox.width,
                hitbox.height
            )
            pygame.draw.rect(screen, RED, hitbox_screen, 2)
        
        # Draw attack warning with prediction bonus
        warning_threshold = 30 + prediction_bonus
        if self.attack_warning > 0 and self.attack_warning <= warning_threshold:
            # Pulsing red indicator for incoming attack
            intensity = int((1 - self.attack_warning / warning_threshold) * 150) + 105
            indicator_radius = self.size//2 + 10
            pygame.draw.circle(screen, (intensity, 0, 0), (int(draw_x), int(draw_y)), indicator_radius, 3)
            
            # Draw warning text
            if self.attack_warning <= 15:
                font = pygame.font.Font(None, 20)
                text = font.render('!', True, RED)
                screen.blit(text, (draw_x - 5, draw_y - self.size - 15))        
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
