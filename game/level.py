import pygame
import random
import math
from game.constants import *
from game.enemy import Enemy

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.width = LEVEL_SIZE
        self.height = LEVEL_SIZE
        self.is_boss_level = (level_number % BOSS_LEVEL_INTERVAL == 0)
        
        # Generate rooms
        self.rooms = self._generate_rooms()
        self.spawn_point = (self.width // 2, self.height // 2)
        
        # Generate enemies
        self.enemies = []
        self._spawn_enemies()
        
        # Items
        self.items = []
        
        # Level cleared
        self.cleared = False
        
    def _generate_rooms(self):
        """Generate procedural rooms"""
        rooms = []
        num_rooms = random.randint(4, 8)
        
        for _ in range(num_rooms):
            room_width = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            room_height = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            room_x = random.randint(100, self.width - room_width - 100)
            room_y = random.randint(100, self.height - room_height - 100)
            
            rooms.append(pygame.Rect(room_x, room_y, room_width, room_height))
        
        return rooms
    
    def _spawn_enemies(self):
        """Spawn enemies in the level"""
        if self.is_boss_level:
            # Spawn boss
            boss_type = random.choice(['grunt', 'brute', 'assassin'])
            boss_x = random.randint(200, self.width - 200)
            boss_y = random.randint(200, self.height - 200)
            self.enemies.append(Enemy(boss_x, boss_y, boss_type, is_boss=True))
            
            # Spawn fewer regular enemies
            num_enemies = ENEMIES_PER_LEVEL // 2
        else:
            num_enemies = ENEMIES_PER_LEVEL + (self.level_number - 1)
        
        # Spawn regular enemies
        for _ in range(num_enemies):
            enemy_type = random.choice(list(ENEMY_TYPES.keys()))
            
            # Find valid spawn position (not too close to center)
            while True:
                x = random.randint(100, self.width - 100)
                y = random.randint(100, self.height - 100)
                dist_from_center = math.sqrt((x - self.width//2)**2 + (y - self.height//2)**2)
                if dist_from_center > 300:
                    break
            
            self.enemies.append(Enemy(x, y, enemy_type))
    
    def update(self, player):
        """Update level state"""
        # Check if level is cleared
        if not self.cleared and len(self.enemies) == 0:
            self.cleared = True
            self._spawn_rewards()
    
    def _spawn_rewards(self):
        """Spawn rewards when level is cleared"""
        # Spawn items based on drop rates
        for item_type, drop_rate in DROP_RATES.items():
            if random.random() < drop_rate:
                x = random.randint(200, self.width - 200)
                y = random.randint(200, self.height - 200)
                self.items.append({
                    'type': item_type,
                    'x': x,
                    'y': y,
                    'collected': False
                })
    
    def check_item_collection(self, player):
        """Check if player collected any items"""
        collected = []
        for item in self.items:
            if not item['collected']:
                dist = math.sqrt((player.x - item['x'])**2 + (player.y - item['y'])**2)
                if dist < 50:
                    item['collected'] = True
                    collected.append(item['type'])
        return collected
    
    def draw(self, screen, camera_offset):
        """Draw level elements"""
        # Draw background gradient
        for y in range(0, WINDOW_HEIGHT, 10):
            color_value = int(20 + (y / WINDOW_HEIGHT) * 40)
            pygame.draw.rect(screen, (color_value, color_value, color_value + 10), 
                           (0, y, WINDOW_WIDTH, 10))
        
        # Draw rooms
        for room in self.rooms:
            room_x = room.x - camera_offset[0]
            room_y = room.y - camera_offset[1]
            
            # Room floor
            pygame.draw.rect(screen, (40, 40, 45), 
                           (room_x, room_y, room.width, room.height))
            # Room border
            pygame.draw.rect(screen, (60, 60, 65), 
                           (room_x, room_y, room.width, room.height), 2)
        
        # Draw items
        for item in self.items:
            if not item['collected']:
                item_x = item['x'] - camera_offset[0]
                item_y = item['y'] - camera_offset[1]
                
                # Draw item with color based on type
                if item['type'] == 'health_potion':
                    color = RED
                elif item['type'] == 'stamina_potion':
                    color = GREEN
                elif item['type'] == 'weapon_upgrade':
                    color = ORANGE
                else:
                    color = PURPLE
                
                pygame.draw.circle(screen, color, (int(item_x), int(item_y)), 15)
                pygame.draw.circle(screen, WHITE, (int(item_x), int(item_y)), 15, 2)
