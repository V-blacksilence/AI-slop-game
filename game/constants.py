# Game Constants
import pygame

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 53, 69)
GREEN = (40, 167, 69)
BLUE = (0, 123, 255)
YELLOW = (255, 193, 7)
ORANGE = (253, 126, 20)
PURPLE = (111, 66, 193)
GRAY = (108, 117, 125)
DARK_GRAY = (52, 58, 64)
LIGHT_GRAY = (173, 181, 189)
CYAN = (23, 162, 184)
PINK = (232, 62, 140)

# Player settings
PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_STAMINA = 100
PLAYER_STAMINA_REGEN = 1
PLAYER_SIZE = 40
PLAYER_DAMAGE = 20

# Combat settings
DODGE_COST = 25
BLOCK_COST_PER_FRAME = 0.8
DODGE_DURATION = 15  # frames
DODGE_DISTANCE = 150
BLOCK_DAMAGE_REDUCTION = 0.7
PERFECT_DODGE_WINDOW = 8  # frames before hit
PERFECT_BLOCK_WINDOW = 5  # frames of block start
ATTACK_COOLDOWN = 30  # frames
ATTACK_RANGE = 100


# Weapon configurations
WEAPONS = {
    'fists': {
        'name': 'Fists',
        'damage': 20,
        'range': 100,
        'cooldown': 30,
        'speed_modifier': 1.0,
        'can_counter': False,
        'can_parry': False,
        'projectile': False,
        'description': 'Basic melee attack'
    },
    'bow': {
        'name': 'Bow',
        'damage': 15,
        'range': 400,
        'cooldown': 45,
        'speed_modifier': 1.0,
        'can_counter': False,
        'can_parry': False,
        'projectile': True,
        'projectile_speed': 12,
        'description': 'Ranged weapon, shoots arrows'
    },
    'spear': {
        'name': 'Spear',
        'damage': 25,
        'range': 180,
        'cooldown': 35,
        'speed_modifier': 0.95,
        'can_counter': False,
        'can_parry': False,
        'projectile': False,
        'description': 'Long reach melee weapon'
    },
    'katana': {
        'name': 'Katana',
        'damage': 30,
        'range': 120,
        'cooldown': 25,
        'speed_modifier': 1.1,
        'can_counter': True,
        'can_parry': True,
        'counter_window': 10,  # frames
        'parry_multiplier': 2.0,
        'projectile': False,
        'description': 'Fast weapon with counter & parry'
    },
    'greatsword': {
        'name': 'Greatsword',
        'damage': 50,
        'range': 140,
        'cooldown': 60,
        'speed_modifier': 0.85,
        'can_counter': False,
        'can_parry': False,
        'projectile': False,
        'aoe': True,
        'aoe_range': 80,
        'description': 'Heavy damage, slow attacks, AOE'
    }
}

# Weapon unlock bosses
WEAPON_UNLOCK_LEVELS = {
    3: 'bow',
    6: 'spear',
    9: 'katana',
    12: 'greatsword'
}

# Shop items (Grave Souls - One-time purchases)
SHOP_ITEMS = {
    'damage_reduction': {
        'name': 'Armor Plate',
        'description': 'Reduce damage taken by 10%',
        'cost': 1,  # 1 grave soul
        'stack': False,  # One-time purchase
        'effect': 0.10  # 10% reduction
    },
    'range_increase': {
        'name': 'Range Extender',
        'description': 'Increase attack range by 25',
        'cost': 1,  # 1 grave soul
        'stack': False,  # One-time purchase
        'effect': 25  # +25 range
    },
    'shield_on_kills': {
        'name': 'Kill Shield',
        'description': 'Shield activates every 3 kills (50 HP)',
        'cost': 1,  # 1 grave soul
        'stack': False,  # One-time purchase
        'effect': 50  # Shield HP
    },
    'attack_prediction': {
        'name': 'Danger Sense',
        'description': 'See enemy attack warnings earlier',
        'cost': 1,  # 1 grave soul
        'stack': False,  # One-time purchase
        'effect': 15  # +15 frames of warning
    }
}

# Grave souls - special currency from bosses
GRAVE_SOULS_PER_BOSS = 1

# Enemy settings
ENEMY_TYPES = {
    'grunt': {
        'health': 50,
        'damage': 10,
        'speed': 2,
        'color': RED,
        'size': 35,
        'xp': 10
    },
    'brute': {
        'health': 100,
        'damage': 20,
        'speed': 1.5,
        'color': ORANGE,
        'size': 45,
        'xp': 25
    },
    'assassin': {
        'health': 40,
        'damage': 15,
        'speed': 4,
        'color': PURPLE,
        'size': 30,
        'xp': 20
    }
}

BOSS_MULTIPLIER = 3  # Boss stats multiplier

# Level settings
LEVEL_SIZE = 2000
ROOM_MIN_SIZE = 400
ROOM_MAX_SIZE = 800
ENEMIES_PER_LEVEL = 8
BOSS_LEVEL_INTERVAL = 3

# Progressive difficulty scaling
DIFFICULTY_SCALING = {
    'enemy_health': 1.15,  # +15% per level
    'enemy_damage': 1.1,   # +10% per level
    'enemy_speed': 1.05,   # +5% per level
    'enemy_count': 1,      # +1 enemy per level
    'soul_bonus': 1.2      # +20% souls per level
}

# Item drop rates
DROP_RATES = {
    'health_potion': 0.3,
    'weapon_upgrade': 0.15,
    'armor_upgrade': 0.1
}

# Meta progression
META_CURRENCY_NAME = 'souls'
META_UPGRADES = {
    'max_health': {'cost': 10, 'increment': 10},
    'max_stamina': {'cost': 8, 'increment': 10},
    'damage': {'cost': 15, 'increment': 5},
    'speed': {'cost': 12, 'increment': 0.5}
}

LEVEL_HEAL_AMOUNT = 20
PARTICLE_COUNT = 10
ITEM_COLLECTION_RANGE = 50
ATTACK_CONE_ANGLE = 0.5  
PRATICLE_LIFETIME = 30  

# Save systems
MAX_SAVE_SLOTS = 6
SAVE_DIR = 'save/'