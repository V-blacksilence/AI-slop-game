import pygame
import math
from game.constants import *

class Projectile:
    def __init__(self, x, y, angle, damage, weapon_type):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = damage
        self.weapon_type = weapon_type
        self.speed = WEAPONS[weapon_type]['projectile_speed']
        self.active = True
        self.distance_traveled = 0
        self.max_distance = WEAPONS[weapon_type]['range']
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.distance_traveled += self.speed
        
        if self.distance_traveled >= self.max_distance:
            self.active = False
    
    def check_collision(self, enemy):
        dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
        return dist < enemy.size
    
    def draw(self, screen, camera_offset):
        if self.active:
            draw_x = self.x - camera_offset[0]
            draw_y = self.y - camera_offset[1]
            
            # Draw arrow
            end_x = draw_x + math.cos(self.angle) * 20
            end_y = draw_y + math.sin(self.angle) * 20
            pygame.draw.line(screen, YELLOW, (draw_x, draw_y), (end_x, end_y), 3)
            pygame.draw.circle(screen, ORANGE, (int(end_x), int(end_y)), 4)


class WeaponSystem:
    def __init__(self):
        self.unlocked_weapons = ['fists']
        self.current_weapon = 'fists'
        self.projectiles = []
        
        # Counter/Parry state
        self.counter_window = 0
        self.parry_ready = False
        
    def unlock_weapon(self, weapon_name):
        if weapon_name not in self.unlocked_weapons:
            self.unlocked_weapons.append(weapon_name)
            return True
        return False
    
    def equip_weapon(self, weapon_name):
        if weapon_name in self.unlocked_weapons:
            self.current_weapon = weapon_name
            return True
        return False
    
    def get_weapon_stats(self):
        return WEAPONS[self.current_weapon]
    
    def activate_counter(self):
        #Activate counter stance for katana
        if WEAPONS[self.current_weapon].get('can_counter', False):
            self.counter_window = WEAPONS[self.current_weapon]['counter_window']
            return True
        return False
    
    def is_counter_active(self):
        return self.counter_window > 0
    
    def update_counter(self):
        if self.counter_window > 0:
            self.counter_window -= 1
    
    def can_parry(self):
        return WEAPONS[self.current_weapon].get('can_parry', False)
    
    def create_projectile(self, x, y, angle):
        #Create projectile for ranged weapons
        weapon = WEAPONS[self.current_weapon]
        if weapon.get('projectile', False):
            proj = Projectile(x, y, angle, weapon['damage'], self.current_weapon)
            self.projectiles.append(proj)
            return proj
        return None
    
    def update_projectiles(self, enemies):
        #Update all projectiles and check for hits
        hits = []
        for proj in self.projectiles[:]:
            proj.update()
            
            if not proj.active:
                self.projectiles.remove(proj)
                continue
            
            # Check collision with enemies
            for enemy in enemies:
                if proj.check_collision(enemy):
                    hits.append((enemy, proj.damage))
                    proj.active = False
                    self.projectiles.remove(proj)
                    break
        
        return hits
    
    def draw_projectiles(self, screen, camera_offset):
        for proj in self.projectiles:
            proj.draw(screen, camera_offset)
    
    def reset_for_run(self):
        # Reset projectiles and states for new run
        self.projectiles = []
        self.counter_window = 0
        self.parry_ready = False
