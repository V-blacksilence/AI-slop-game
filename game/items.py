import pygame
import random
from game.constants import *

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.collected = False
        self.size = 15
        
    def apply_effect(self, player):
        """Apply item effect to player"""
        if self.type == 'health_potion':
            player.heal(50)
            return 'Restored 50 HP'
        elif self.type == 'weapon_upgrade':
            player.upgrade_weapon()
            return f'Weapon upgraded to level {player.weapon_level}'
        elif self.type == 'armor_upgrade':
            player.upgrade_armor()
            return f'Armor upgraded to level {player.armor_level}'
        return ''
    
    def draw(self, screen, camera_offset):
        if not self.collected:
            draw_x = self.x - camera_offset[0]
            draw_y = self.y - camera_offset[1]
            
            # Pulsing effect
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
            size = self.size + int(pulse * 5)
            
            # Color based on type
            if self.type == 'health_potion':
                color = RED
            elif self.type == 'weapon_upgrade':
                color = ORANGE
            else:
                color = PURPLE
            
            pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), size)
            pygame.draw.circle(screen, WHITE, (int(draw_x), int(draw_y)), size, 2)


class MetaProgression:
    def __init__(self):
        self.souls = 0  # Currency for meta upgrades
        self.upgrades = {
            'max_health': 0,
            'max_stamina': 0,
            'damage': 0,
            'speed': 0
        }
        self.total_runs = 0
        self.best_level = 0
        
    def add_souls(self, amount):
        self.souls += amount
    
    def can_upgrade(self, upgrade_name):
        cost = META_UPGRADES[upgrade_name]['cost'] * (self.upgrades[upgrade_name] + 1)
        return self.souls >= cost
    
    def purchase_upgrade(self, upgrade_name):
        cost = META_UPGRADES[upgrade_name]['cost'] * (self.upgrades[upgrade_name] + 1)
        if self.souls >= cost:
            self.souls -= cost
            self.upgrades[upgrade_name] += 1
            return True
        return False
    def reset(self):
        """Reset all meta progression data"""
        self.souls = 0
        self.upgrades = {
            'max_health': 0,
            'max_stamina': 0,
            'damage': 0,
            'speed': 0
        }
        self.total_runs = 0
        self.best_level = 0    
    def apply_to_player(self, player):
        """Apply meta upgrades to player"""
        if self.upgrades['max_health'] > 0:
            bonus = META_UPGRADES['max_health']['increment'] * self.upgrades['max_health']
            player.max_health += bonus
            player.health = player.max_health
        
        if self.upgrades['max_stamina'] > 0:
            bonus = META_UPGRADES['max_stamina']['increment'] * self.upgrades['max_stamina']
            player.max_stamina += bonus
            player.stamina = player.max_stamina
        
        if self.upgrades['damage'] > 0:
            bonus = META_UPGRADES['damage']['increment'] * self.upgrades['damage']
            player.damage += bonus
        
        if self.upgrades['speed'] > 0:
            bonus = META_UPGRADES['speed']['increment'] * self.upgrades['speed']
            player.speed += bonus
    
    def save(self, filename='meta_save.txt'):
        """Save meta progression to file"""
        try:
            with open(filename, 'w') as f:
                f.write(f"{self.souls}\n")
                f.write(f"{self.total_runs}\n")
                f.write(f"{self.best_level}\n")
                for upgrade, level in self.upgrades.items():
                    f.write(f"{upgrade}:{level}\n")
        except:
            pass
    
    def load(self):
        """Load meta progression from file"""
        try:
            with open('meta_save.txt', 'r') as f:
                self.souls = int(f.readline().strip())
                self.total_runs = int(f.readline().strip())
                self.best_level = int(f.readline().strip())
                for line in f:
                    upgrade, level = line.strip().split(':')
                    if upgrade in self.upgrades:
                        self.upgrades[upgrade] = int(level)
        except FileNotFoundError:
            print("No meta save file found, using default values")
        except Exception as e:
            print(f"Error loading meta progress: {e}")
            print("Using default values")