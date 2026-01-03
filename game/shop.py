import pygame
from game.constants import *

class Shop:
    def __init__(self):
        self.items = list(SHOP_ITEMS.keys())
        self.purchases = {
            'damage_reduction': 0,
            'range_increase': 0,
            'shield_on_kills': 0,
            'attack_prediction': 0
        }
        self.purchased_this_shop = False
        
    def can_purchase(self, item_name, player_souls):
        # Check if player can purchase item
        if self.purchased_this_shop:
            return False, f'Already purschased'
        
        item = SHOP_ITEMS[item_name]
        if player_souls < item['cost']:
            return False, f'Not enough souls'
        
        return True
    
    def purchase(self, item_name, player):
        # Purchase an item
        can_buy, message = self.can_purchase(item_name, player.souls)
        if not can_buy:
            return False, message
        
        item = SHOP_ITEMS[item_name]
        player.souls -= item['cost']
        self.purchases[item_name] += 1
        self.purchased_this_shop = True
        
        # Apply effect immediately\n        self._apply_effect(item_name, player)
        
        return True, f'Bought {item['name']}!'
    
    def _apply_effect(self, item_name, player):
        # Apply item effect to player
        item = SHOP_ITEMS[item_name]
        
        if item_name == 'damage_reduction':
            player.damage_reduction += item['effect']
        elif item_name == 'range_increase':
            player.range_bonus += item['effect']
        elif item_name == 'shield_on_kills':
            player.shield_per_kills += item['effect']
        elif item_name == 'attack_prediction':
            player.prediction_bonus += item['effect']
    
    def reset_shop(self):
        # Reset for next shop visit
        self.purchased_this_shop = False
    
    def get_item_info(self, item_name):
        # Get item information
        item = SHOP_ITEMS[item_name]
        times_bought = self.purchases[item_name]
        
        return {
            'name': item['name'],
            'description': item['description'],
            'cost': item['cost'],
            'times_bought': times_bought
        }
