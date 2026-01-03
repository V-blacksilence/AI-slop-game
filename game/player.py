import pygame
import math
from game.constants import *
from game.weapons import WeaponSystem
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
        self.souls = 0

        # Weapon system
        self.weapon_system = WeaponSystem()

        # Shop upgrades
        self.damage_reduction = 0
        self.range_bonus = 0
        self.shield_per_kills = 0
        self.prediction_bonus = 0

        # Shield systems
        self.shield = 0
        self.kills_since_shield = 0
        self.shield_active = False
        
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
        
        # Update weapon system
        self.weapon_system.update_counter()

        # Get speed with weapon modifier
        weapon_stats = self.weapon_system.get_weapon_stats()
        current_speed = self.speed * weapon_stats['speed_modifier']
        
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

        # Counter stance
        if keys[pygame.K_c]:
            self.weapon_system.activate_counter()

        
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
            weapon_stats = self.weapon_system.get_weapon_stats()
            self.attack_cooldown = weapon_stats['cooldown']
            
            # Calculate attack direction
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            angle = math.atan2(dy, dx)
            
            # Handle projectile weapons
            if weapon_stats.get('projectile', False):
                self.weapon_system.create_projectile(self.x, self.y, angle)
            return angle
        return None

    def get_attack_range(self):
        weapon_stats = self.weapon_system.get_weapon_stats()
        return weapon_stats['range'] + self.range_bonus
    
    def get_attack_damage(self):
        weapon_stats = self.weapon_system.get_weapon_stats()
        base_damage = weapon_stats['damage'] + self.damage
        return base_damage
    

    def take_damage(self, damage, enemy_pos):
        # Check shield first
        if self.shield_active and self.shield > 0:
            self.shield -= damage
            if self.shield <= 0:
                overflow = abs(self.shield)
                self.shield = 0
                self.shield_active = False
                # Apply overflow damage
                if overflow > 0:
                    return self._apply_damage_to_health(overflow, enemy_pos)
            return 'shield'
        
        return self._apply_damage_to_health(damage, enemy_pos)
    
    def _apply_damage_to_health(self, damage, enemy_pos):
        if self.invulnerable:
            return 'perfect_dodge'
        
        # Check for counter (katana)
        if self.weapon_system.is_counter_active():
            return 'counter'
        
        if self.is_blocking:
            if self.block_timer <= PERFECT_BLOCK_WINDOW:
                self.perfect_blocks += 1
                # Parry check (katana)
                if self.weapon_system.can_parry():
                    return 'parry'
                return 'perfect_block'
            else:
                # Apply damage reduction from shop + block
                total_reduction = BLOCK_DAMAGE_REDUCTION + self.damage_reduction
                total_reduction = min(0.9, total_reduction)  # Cap at 90%
                damage *= (1 - total_reduction)
                self.health -= damage
                self.damage_taken += damage
                return 'block'
        
        # Apply damage reduction from shop
        if self.damage_reduction > 0:
            damage *= (1 - min(0.9, self.damage_reduction))
        
        self.health -= damage
        self.damage_taken += damage
        return 'hit'
    
    def on_kill(self):
        """Called when player kills an enemy"""
        self.kills += 1
        self.kills_since_shield += 1
        
        # Check for shield activation
        if self.shield_per_kills > 0 and self.kills_since_shield >= 3:
            self.kills_since_shield = 0
            # Shield ready but not active yet
            return 'shield_ready'
        return None
    
    def activate_shield(self):
        """Activate the earned shield"""
        if self.shield_per_kills > 0:
            self.shield = self.shield_per_kills
            self.shield_active = True
            return True
        return False
    
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
    
    def get_hitbox(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

    def draw(self, screen, camera_offset, show_hitbox=True):
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
            pygame.draw.rect(screen, CYAN, hitbox_screen, 2)
        # Draw player
        color = BLUE
        if self.is_dodging:
            color = YELLOW
        elif self.is_blocking:
            color = LIGHT_GRAY
        elif self.weapon_system.is_counter_active():
            color = PINK
        
        pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), self.size//2)
        
        # Draw direction indicator
        if not self.is_dodging:
            pygame.draw.circle(screen, WHITE, (int(draw_x), int(draw_y)), self.size//2, 2)
        #Draw shield indicator
        if self.shield_active and self.shield >0:
            pygame.draw.circle(screen, CYAN, (int(draw_x), int(draw_y)), self.size//2 + 5, 3)

        # Draw weapon indicator
        weapon_name = self.weapon_system.current_weapon
        if weapon_name != 'fists':
            font = pygame.font.Font(None, 18)
            text = font.render(weapon_name[:3].upper(), True, YELLOW)
            screen.blit(text, (draw_x - 10, draw_y + self.size//2 + 5))
        
        