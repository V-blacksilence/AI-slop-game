import pygame
from game.constants import *

class UI:
    def __init__(self):
        self.show_stats = False
        self.messages = []  # [(message, timer), ...]
        self.message_duration = 120  # frames
        
        # Fonts
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        self.font_huge = pygame.font.Font(None, 72)  
    
    def update(self):
        # Update messages
        self.messages = [(msg, timer - 1) for msg, timer in self.messages if timer > 1]
    
    def add_message(self, message):
        self.messages.append((message, self.message_duration))
    
    def toggle_stats(self):
        self.show_stats = not self.show_stats
    
    def draw_hud(self, screen, player, level):
        # Health bar
        self._draw_bar(screen, 20, 20, 200, 20, player.health, player.max_health, 
                      RED, 'HP')
        
        # Stamina bar
        self._draw_bar(screen, 20, 50, 200, 20, player.stamina, player.max_stamina, 
                      GREEN, 'Stamina')
        
        # Level info
        level_text = self.font_small.render(f'Level {level.level_number}', True, WHITE)
        screen.blit(level_text, (20, 80))
        
        if level.is_boss_level:
            boss_text = self.font_medium.render('BOSS LEVEL', True, YELLOW)
            screen.blit(boss_text, (WINDOW_WIDTH // 2 - boss_text.get_width() // 2, 20))
        
        # Enemy count
        enemy_text = self.font_small.render(f'Enemies: {len(level.enemies)}', True, WHITE)
        screen.blit(enemy_text, (20, 110))

        # Level cleared indicator
        if level.cleared:
            cleared_text = self.font_medium.render('LEVEL CLEARED!', True, GREEN)
            screen.blit(cleared_text, (WINDOW_WIDTH // 2 - cleared_text.get_width() // 2, 60))
            if len(level.items) > 0:
                collect_text = self.font_small.render('Collect your rewards or move to next area', True, WHITE)
                screen.blit(collect_text, (WINDOW_WIDTH // 2 - collect_text.get_width() // 2, 95))
        
        # Combat indicators
        if player.is_dodging:
            dodge_text = self.font_medium.render('DODGE!', True, YELLOW)
            screen.blit(dodge_text, (WINDOW_WIDTH // 2 - dodge_text.get_width() // 2, WINDOW_HEIGHT - 100))
        elif player.is_blocking:
            block_text = self.font_medium.render('BLOCKING', True, LIGHT_GRAY)
            screen.blit(block_text, (WINDOW_WIDTH // 2 - block_text.get_width() // 2, WINDOW_HEIGHT - 100))


        # Attack cooldown indicator
        if player.attack_cooldown > 0:
            cooldown_ratio = player.attack_cooldown / ATTACK_COOLDOWN
            cooldown_width = 100
            cooldown_x = WINDOW_WIDTH - cooldown_width - 20
            cooldown_y = WINDOW_HEIGHT - 40
            
            # Background
            pygame.draw.rect(screen, DARK_GRAY, (cooldown_x, cooldown_y, cooldown_width, 10))
            # Cooldown progress
            pygame.draw.rect(screen, ORANGE, (cooldown_x, cooldown_y, 
                                             cooldown_width * (1 - cooldown_ratio), 10))
            pygame.draw.rect(screen, WHITE, (cooldown_x, cooldown_y, cooldown_width, 10), 1)            
        

        # Messages
        y_offset = WINDOW_HEIGHT - 150
        for message, timer in self.messages:
            alpha = min(255, timer * 2)
            text = self.font_small.render(message, True, YELLOW)
            text.set_alpha(alpha)
            screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset -= 30
    
    def draw_stats(self, screen, player):
        if not self.show_stats:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((400, 500))
        overlay.set_alpha(200)
        overlay.fill(DARK_GRAY)
        screen.blit(overlay, (WINDOW_WIDTH - 420, 20))
        
        x = WINDOW_WIDTH - 400
        y = 40
        
        # Title
        title = self.font_large.render('STATS', True, YELLOW)
        screen.blit(title, (x, y))
        y += 60
        
        # Player stats
        stats = [
            f'Health: {int(player.health)}/{player.max_health}',
            f'Stamina: {int(player.stamina)}/{player.max_stamina}',
            f'Damage: {player.damage}',
            f'Speed: {player.speed}',
            '',
            f'Weapon Level: {player.weapon_level}',
            f'Armor Level: {player.armor_level}',
            '',
            f'Kills: {player.kills}',
            f'Perfect Dodges: {player.perfect_dodges}',
            f'Perfect Blocks: {player.perfect_blocks}',
            f'Damage Dealt: {int(player.damage_dealt)}',
            f'Damage Taken: {int(player.damage_taken)}',
        ]
        
        for stat in stats:
            if stat:
                text = self.font_small.render(stat, True, WHITE)
                screen.blit(text, (x, y))
            y += 30

    def draw_pause(self, screen):
        """Draw pause menu overlay"""
        # Semi-transparent dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(160)  # Slightly transparent
        screen.blit(overlay, (0, 0))
        
        # Pause title
        title = self.font_huge.render('PAUSED', True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Menu options
        options = [
            ('ESC - Resume', WHITE),
            ('S - Save Game', GREEN),
            ('R - Return to Menu', ORANGE),
            ('H - Toggle Hitboxes', BLUE)
        ]
        
        y = 300
        for text, color in options:
            text_surface = self.font_medium.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, y))
            screen.blit(text_surface, text_rect)
            y += 50
        
        # Warning message
        if len(self.messages) == 0:  # Only show if no other messages
            warning = self.font_small.render('Game progress will be saved when returning to menu', 
                                        True, GRAY)
            warning_rect = warning.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
            screen.blit(warning, warning_rect)
    def draw_options(self, screen, show_hitboxes, auto_save):
        """Draw options menu"""
        screen.fill((20, 20, 30))
        
        # Title
        title = self.font_huge.render('OPTIONS', True, YELLOW)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))
        
        # Options
        y = 220
        
        # Auto-save option
        auto_save_text = 'ON' if auto_save else 'OFF'
        auto_save_color = GREEN if auto_save else RED
        option1 = self.font_medium.render(f'1. Auto-Save: ', True, WHITE)
        option1_value = self.font_medium.render(auto_save_text, True, auto_save_color)
        screen.blit(option1, (WINDOW_WIDTH // 2 - 200, y))
        screen.blit(option1_value, (WINDOW_WIDTH // 2 + 20, y))
        y += 60
        
        # Show hitboxes option
        hitbox_text = 'ON' if show_hitboxes else 'OFF'
        hitbox_color = GREEN if show_hitboxes else RED
        option2 = self.font_medium.render(f'2. Show Hitboxes: ', True, WHITE)
        option2_value = self.font_medium.render(hitbox_text, True, hitbox_color)
        screen.blit(option2, (WINDOW_WIDTH // 2 - 200, y))
        screen.blit(option2_value, (WINDOW_WIDTH // 2 + 20, y))
        y += 80
        
        # Reset data option
        option3 = self.font_medium.render('3. Reset All Data', True, RED)
        screen.blit(option3, (WINDOW_WIDTH // 2 - option3.get_width() // 2, y))
        warning = self.font_small.render('(This will delete all progress!)', True, ORANGE)
        screen.blit(warning, (WINDOW_WIDTH // 2 - warning.get_width() // 2, y + 35))
        y += 100
        
        # Instructions
        y = WINDOW_HEIGHT - 150
        instructions = [
            'Press 1-3 to toggle options',
            'Press ESC to return to menu',
        ]
        
        for instruction in instructions:
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 35

    def draw_reset_confirmation(self, screen):
        """Draw reset confirmation dialog"""
        # Dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Warning box
        box_width = 500
        box_height = 200
        box_x = WINDOW_WIDTH // 2 - box_width // 2
        box_y = WINDOW_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(screen, DARK_GRAY, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, RED, (box_x, box_y, box_width, box_height), 2)
        
        # Warning text
        warning = self.font_medium.render('Are you sure you want to reset ALL data?', True, RED)
        warning_rect = warning.get_rect(center=(WINDOW_WIDTH // 2, box_y + 50))
        screen.blit(warning, warning_rect)
        
        sub_text = self.font_small.render('This will delete all progress and cannot be undone!', True, YELLOW)
        sub_rect = sub_text.get_rect(center=(WINDOW_WIDTH // 2, box_y + 90))
        screen.blit(sub_text, sub_rect)
        
        # Options
        y = box_y + 140
        options = [
            ('Y - Yes, reset everything', RED),
            ('N - No, keep my data', GREEN)
        ]
        
        for text, color in options:
            text_surface = self.font_medium.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, y))
            screen.blit(text_surface, text_rect)
            y += 30       
        
    def _draw_bar(self, screen, x, y, width, height, current, maximum, color, label):
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height))
        
        # Fill
        fill_width = (current / maximum) * width
        pygame.draw.rect(screen, color, (x, y, fill_width, height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)
        
        # Label
        text = self.font_small.render(f'{label}: {int(current)}/{int(maximum)}', True, WHITE)
        screen.blit(text, (x + 5, y + 1))
    
    def draw_game_over(self, screen, player, level_reached, souls_earned):
        # Dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        title = self.font_large.render('YOU DIED', True, RED)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 150))
        
        # Stats
        y = 250
        stats = [
            f'Level Reached: {level_reached}',
            f'Kills: {player.kills}',
            f'Damage Dealt: {int(player.damage_dealt)}',
            f'Perfect Dodges: {player.perfect_dodges}',
            f'Perfect Blocks: {player.perfect_blocks}',
            '',
            f'Souls Earned: {souls_earned}',
        ]
        
        for stat in stats:
            if stat:
                text = self.font_medium.render(stat, True, WHITE)
                screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 40
        
        # Instructions
        restart_text = self.font_small.render('Press R to restart or ESC for menu', True, LIGHT_GRAY)
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT - 100))
    
    def draw_menu(self, screen, meta):
        screen.fill((20, 20, 30))
        
        # Title
        title = self.font_large.render('HACK & SLASH', True, YELLOW)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Meta stats
        y = 200
        stats = [
            f'Souls: {meta.souls}',
            f'Total Runs: {meta.total_runs}',
            f'Best Level: {meta.best_level}',
        ]
        
        for stat in stats:
            text = self.font_medium.render(stat, True, WHITE)
            screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 40
        
        # Upgrades
        y += 40
        upgrade_title = self.font_medium.render('UPGRADES (Press 1-4)', True, YELLOW)
        screen.blit(upgrade_title, (WINDOW_WIDTH // 2 - upgrade_title.get_width() // 2, y))
        y += 50
        
        upgrades = [
            ('1. Max Health', 'max_health'),
            ('2. Max Stamina', 'max_stamina'),
            ('3. Damage', 'damage'),
            ('4. Speed', 'speed'),
        ]
        
        for label, upgrade_name in upgrades:
            level = meta.upgrades[upgrade_name]
            cost = META_UPGRADES[upgrade_name]['cost'] * (level + 1)
            can_afford = meta.souls >= cost
            color = GREEN if can_afford else GRAY
            
            text = self.font_small.render(f'{label}: Lv {level} (Cost: {cost} souls)', True, color)
            screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 35
        
        # Instructions
        y = WINDOW_HEIGHT - 100
        instructions = [
            'Press SPACE to start',
            'Controls: WASD/Arrows=Move, Mouse=Aim, Click=Attack, Space=Dodge, Shift=Block, Tab=Stats, O=Options'
        ]
        
        for instruction in instructions:
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 30
