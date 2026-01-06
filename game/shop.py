import pygame
from game.constants import *

class Shop:
    def __init__(self, meta_progression):
        self.items = list(SHOP_ITEMS.keys())
        self.meta = meta_progression  # Reference to meta progression for persistent purchases
        
    def can_purchase(self, item_name):
        """Check if player can purchase item (has grave souls and hasn't purchased before)"""
        # Check if already purchased (one-time only)
        if self.meta.shop_purchases.get(item_name, False):
            return False, 'Already purchased'
        
        # Check if player has enough grave souls
        item = SHOP_ITEMS[item_name]
        if self.meta.grave_souls < item['cost']:
            return False, 'Not enough grave souls'
        
        return True, 'Can purchase'
    
    def purchase(self, item_name, player):
        """Purchase an item with grave souls"""
        can_buy, message = self.can_purchase(item_name)
        if not can_buy:
            return False, message
        
        item = SHOP_ITEMS[item_name]
        
        # Deduct grave souls
        self.meta.grave_souls -= item['cost']
        
        # Mark as purchased
        self.meta.shop_purchases[item_name] = True
        
        # Apply effect immediately
        self._apply_effect(item_name, player)
        
        return True, f'Purchased {item["name"]}!'
    
    def _apply_effect(self, item_name, player):
        """Apply item effect to player"""
        item = SHOP_ITEMS[item_name]
        
        if item_name == 'damage_reduction':
            player.damage_reduction += item['effect']
        elif item_name == 'range_increase':
            player.range_bonus += item['effect']
        elif item_name == 'shield_on_kills':
            player.shield_per_kills += item['effect']
        elif item_name == 'attack_prediction':
            player.prediction_bonus += item['effect']
    
    def get_item_info(self, item_name):
        """Get item information"""
        item = SHOP_ITEMS[item_name]
        purchased = self.meta.shop_purchases.get(item_name, False)
        
        return {
            'name': item['name'],
            'description': item['description'],
            'cost': item['cost'],
            'purchased': purchased
        }