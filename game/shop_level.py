import pygame
import math
from game.constants import *

class ShopLevel:
    """Shop level - special level for purchasing items with grave souls"""
    
    def __init__(self):
        self.width = 1000
        self.height = 800
        
        # Exit portal position (center-bottom)
        self.exit_portal = {
            'x': self.width // 2,
            'y': self.height - 150,
            'active': True
        }
        self.exit_portal_radius = 40
        
        # Shop display positions
        self.shop_items_positions = {
            'damage_reduction': {'x': 250, 'y': 250},
            'range_increase': {'x': 750, 'y': 250},
            'shield_on_kills': {'x': 250, 'y': 500},
            'attack_prediction': {'x': 750, 'y': 500}
        }
        self.item_radius = 60
        
    def check_exit_portal_enter(self, player):
        """Check if player entered the exit portal"""
        dist = math.sqrt((player.x - self.exit_portal['x'])**2 + 
                        (player.y - self.exit_portal['y'])**2)
        return dist < self.exit_portal_radius
    
    def check_item_hover(self, player):
        """Check if player is hovering over any shop item"""
        for item_name, pos in self.shop_items_positions.items():
            dist = math.sqrt((player.x - pos['x'])**2 + (player.y - pos['y'])**2)
            if dist < self.item_radius:
                return item_name
        return None
    
    def draw(self, screen, camera_offset, shop, meta):
        """Draw shop level"""
        # Draw background (darker, mystical theme)
        for y in range(0, WINDOW_HEIGHT, 10):
            color_value = int(10 + (y / WINDOW_HEIGHT) * 30)
            pygame.draw.rect(screen, (color_value, color_value // 2, color_value + 20), 
                           (0, y, WINDOW_WIDTH, 10))
        
        # Draw floor
        floor_rect = pygame.Rect(100 - camera_offset[0], 100 - camera_offset[1], 
                                self.width - 200, self.height - 200)
        pygame.draw.rect(screen, (30, 25, 40), floor_rect)
        pygame.draw.rect(screen, (60, 50, 80), floor_rect, 3)
        
        # Draw title
        font_title = pygame.font.Font(None, 64)
        title = font_title.render('GRAVE SOULS SHOP', True, (200, 150, 255))
        title_x = WINDOW_WIDTH // 2 - title.get_width() // 2
        screen.blit(title, (title_x, 30))
        
        # Draw grave souls balance
        font_balance = pygame.font.Font(None, 36)
        balance_text = f'Grave Souls: {meta.grave_souls} 💀'
        balance = font_balance.render(balance_text, True, (255, 200, 100))
        balance_x = WINDOW_WIDTH // 2 - balance.get_width() // 2
        screen.blit(balance, (balance_x, 90))
        
        # Draw shop items
        font_name = pygame.font.Font(None, 28)
        font_desc = pygame.font.Font(None, 20)
        font_cost = pygame.font.Font(None, 24)
        
        for item_name, pos in self.shop_items_positions.items():
            item_x = pos['x'] - camera_offset[0]
            item_y = pos['y'] - camera_offset[1]
            
            info = shop.get_item_info(item_name)
            purchased = info['purchased']
            
            # Draw item circle
            if purchased:
                # Grayed out if purchased
                pygame.draw.circle(screen, DARK_GRAY, (int(item_x), int(item_y)), self.item_radius)
                pygame.draw.circle(screen, GRAY, (int(item_x), int(item_y)), self.item_radius, 3)
            else:
                # Pulsing effect for available items
                pulse = abs(math.sin(pygame.time.get_ticks() / 500)) * 0.2 + 0.8
                radius = int(self.item_radius * pulse)
                pygame.draw.circle(screen, (111, 66, 193), (int(item_x), int(item_y)), radius)
                pygame.draw.circle(screen, (200, 150, 255), (int(item_x), int(item_y)), radius, 3)
            
            # Draw item name
            name_text = font_name.render(info['name'], True, WHITE if not purchased else GRAY)
            name_rect = name_text.get_rect(center=(item_x, item_y - self.item_radius - 25))
            screen.blit(name_text, name_rect)
            
            # Draw description
            desc_text = font_desc.render(info['description'], True, LIGHT_GRAY if not purchased else GRAY)
            desc_rect = desc_text.get_rect(center=(item_x, item_y + self.item_radius + 15))
            screen.blit(desc_text, desc_rect)
            
            # Draw cost or status
            if purchased:
                status_text = font_cost.render('OWNED', True, GREEN)
            else:
                status_text = font_cost.render(f'{info["cost"]} Grave Soul', True, (255, 200, 100))
            status_rect = status_text.get_rect(center=(item_x, item_y + self.item_radius + 35))
            screen.blit(status_text, status_rect)
        
        # Draw exit portal
        portal_x = self.exit_portal['x'] - camera_offset[0]
        portal_y = self.exit_portal['y'] - camera_offset[1]
        
        time = pygame.time.get_ticks()
        pulse = abs(math.sin(time / 300)) * 0.3 + 0.7
        
        # Portal effect (cyan/return theme)
        glow_radius = int(self.exit_portal_radius * 1.5 * pulse)
        for i in range(3):
            alpha_radius = glow_radius - i * 10
            pygame.draw.circle(screen, (50, 150, 150), 
                             (int(portal_x), int(portal_y)), alpha_radius, 2)
        
        pygame.draw.circle(screen, CYAN, 
                         (int(portal_x), int(portal_y)), int(self.exit_portal_radius * pulse))
        pygame.draw.circle(screen, (100, 200, 200), 
                         (int(portal_x), int(portal_y)), int(self.exit_portal_radius * pulse * 0.6))
        
        # Draw "EXIT" text
        font = pygame.font.Font(None, 28)
        exit_text = font.render('EXIT', True, WHITE)
        exit_rect = exit_text.get_rect(center=(portal_x, portal_y - self.exit_portal_radius - 20))
        screen.blit(exit_text, exit_rect)
        
        # Draw instructions at bottom
        font_inst = pygame.font.Font(None, 24)
        inst_text = 'Walk to an item to purchase • Enter EXIT portal to continue adventure'
        inst = font_inst.render(inst_text, True, LIGHT_GRAY)
        inst_rect = inst.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        screen.blit(inst, inst_rect)
