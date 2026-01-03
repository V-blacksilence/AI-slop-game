import os
import pygame
import sys
import math
from game.constants import *
from game.player import Player
from game.enemy import Enemy
from game.level import Level
from game.items import MetaProgression
from game.ui import UI
from game.vfx import VFXManager
# Save folder and files
SAVE_DIR = os.path.join(os.getcwd(), 'saves')
os.makedirs(SAVE_DIR, exist_ok=True)

# full paths
SAVE_PATHS = {
    'meta_save.txt': os.path.join(SAVE_DIR, 'meta_save.txt'),
    'game_settings.txt': os.path.join(SAVE_DIR, 'game_settings.txt'),
    'settings.txt': os.path.join(SAVE_DIR, 'settings.txt'),
}

# quick existence check
save_files = {name: os.path.exists(path) for name, path in SAVE_PATHS.items()}
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Hack & Slash Roguelike')
        self.clock = pygame.time.Clock()
        
        #Settings
        self.auto_save = True
        self.show_hitboxes = False
        # Game state
        self.state = 'menu'  # menu, playing, game_over, level_transition
        self.running = True
        
        # Meta progression
        self.meta = MetaProgression()
        self.load_or_init_progress()
        
        # UI
        self.ui = UI()
        
        # Game session
        self.player = None
        self.level = None
        self.current_level_number = 1
        self.camera_offset = [0, 0]
        self.souls_earned = 0
        
        # Particles and effects
        self.particles = []
        # Visual effects manager
        self.vfx = VFXManager()
        
        # Load settings from file
        try:
            self._load_settings()
        except Exception as l:
            print(f"Error loading settings: {l}")
            # Use default settings if loading fails
            pass

        # Load meta progress if it exists
        if save_files['meta_save.txt']:
            try:
                self.meta.load()
                print("Loaded existing meta progress")
            except Exception as e:
                print(f"Error loading meta progress: {e}")
                self.meta.reset()
        else:
            print("No meta progress found, starting fresh")
            self.meta.reset()
        
        # Load settings if they exist
        if save_files['game_settings.txt'] or save_files['settings.txt']:
            try:
                self.load_settings()
                print("Loaded existing settings")
            except Exception as e:
                print(f"Error loading settings: {e}")
                # Use default settings
                self.auto_save = True
                self.show_hitboxes = False
        else:
            print("No settings found, using defaults")
            # Use default settings
            self.auto_save = True
            self.show_hitboxes = False
        
        # Display current state
        print("\n=== Current Game State ===")
        print(f"Souls: {self.meta.souls}")
        print(f"Total Runs: {self.meta.total_runs}")
        print(f"Best Level: {self.meta.best_level}")
        print(f"Upgrades: {self.meta.upgrades}")
        print(f"Auto Save: {self.auto_save}")
        print(f"Show Hitboxes: {self.show_hitboxes}")
        print("=======================\n")

    def load_settings(self):
        """Load game settings from file"""
        settings_file = 'game_settings.txt'
        
        # Check if file exists first
        if not os.path.exists(settings_file):
            # If no settings file, create one with defaults
            self.save_settings()
            return
            
        try:
            with open(settings_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        if key == 'auto_save':
                            self.auto_save = value.lower() == 'true'
                        elif key == 'show_hitboxes':
                            self.show_hitboxes = value.lower() == 'true'
        except Exception as s:
            print(f"Error loading settings: {s}")
            # Keep default values if loading fails

    def save_settings(self):
        """Save game settings to file"""
        settings_file = 'game_settings.txt'
        try:
            with open(settings_file, 'w') as f:
                f.write(f'auto_save={str(self.auto_save)}\n')
                f.write(f'show_hitboxes={str(self.show_hitboxes)}\n')
        except Exception as e:
            print(f"Error saving settings: {e}")
        try:
            with open('settings.txt', 'w') as f:
                f.write(f'auto_save={self.auto_save}\n')
                f.write(f'show_hitboxes={self.show_hitboxes}\n')
        except:
            pass     


    def reset_all_data(self):
        """Reset all game data and remove save files"""
        # Reset meta progression
        self.meta.reset()
        
        # Reset current session
        self.current_level_number = 1
        self.souls_earned = 0
        self.player = None
        self.level = None
        
        # Reset settings to default
        self.auto_save = True
        self.show_hitboxes = False
        
        # Delete all save files
        save_files = [
            'meta_save.txt',
            'game_settings.txt',
            'settings.txt'
        ]
        
        deleted_files = []
        for file in save_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    deleted_files.append(file)
            except Exception as e:
                print(f"Error deleting {file}: {e}")
        
        # Add message about deleted files
        if deleted_files:
            self.ui.add_message(f"Deleted save files: {', '.join(deleted_files)}")
        
        # Return to menu
        self.state = 'menu'
        self.ui.add_message('All data has been reset!')

    def load_or_init_progress(self):
        """Load meta progression from saves if present, otherwise init/reset it."""
        if save_files.get('meta_save.txt'):
            try:
                self.meta.load()
                print("Loaded existing meta progress (from load_or_init_progress)")
            except Exception as e:
                print(f"Error loading meta progress: {e}")
                self.meta.reset()
        else:
            self.meta.reset()


    def _load_settings(self):
        """Load settings from SAVE_PATHS (game_settings.txt or settings.txt) if present."""
        # Try preferred 'game_settings.txt' first, then fallback to 'settings.txt'
        for key in ('game_settings.txt', 'settings.txt'):
            path = SAVE_PATHS.get(key)
            if path and os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        for line in f:
                            if '=' in line:
                                k, v = line.strip().split('=', 1)
                                if k == 'auto_save':
                                    self.auto_save = v.lower() == 'true'
                                elif k == 'show_hitboxes':
                                    self.show_hitboxes = v.lower() == 'true'
                    print(f"Loaded settings from {path}")
                    return
                except Exception as e:
                    print(f"Error loading settings from {path}: {e}")
        # If no file found, keep defaults  


    def new_game(self):
        """Start a new game session"""
        self.current_level_number = 1
        self.souls_earned = 0
        self.player = Player(LEVEL_SIZE // 2, LEVEL_SIZE // 2)
        self.meta.apply_to_player(self.player)
        self.level = Level(self.current_level_number)
        self.state = 'playing'
        self.meta.total_runs += 1
        self.ui.add_message('Game Start!')
    
    def next_level(self):
        """Progress to next level"""
        self.current_level_number += 1
        if self.current_level_number > self.meta.best_level:
            self.meta.best_level = self.current_level_number
        
        self.level = Level(self.current_level_number)
        self.player.x = LEVEL_SIZE // 2
        self.player.y = LEVEL_SIZE // 2
        self.player.health = min(self.player.max_health, self.player.health + 20)
        self.ui.add_message(f'Level {self.current_level_number}')
        if self.level.is_boss_level:
            self.ui.add_message('BOSS INCOMING!')
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.auto_save:
                    self.meta.save()
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_SPACE:
                        self.new_game()
                    elif event.key == pygame.K_1:
                        self.meta.purchase_upgrade('max_health')
                        if self.auto_save:
                            self.meta.save()
                    elif event.key == pygame.K_2:
                        self.meta.purchase_upgrade('max_stamina')
                        if self.auto_save:
                            self.meta.save()                        
                    elif event.key == pygame.K_3:
                        self.meta.purchase_upgrade('damage')
                        if self.auto_save:
                            self.meta.save()                        
                    elif event.key == pygame.K_4:
                        self.meta.purchase_upgrade('speed')
                        if self.auto_save:
                            self.meta.save()             
                    elif event.key == pygame.K_o:
                        self.state = 'options'           
                
                elif self.state == 'playing':
                    if event.key == pygame.K_SPACE:
                        # Dodge based on movement direction
                        keys = pygame.key.get_pressed()
                        dx = 0
                        dy = 0
                        if keys[pygame.K_w] or keys[pygame.K_UP]:
                            dy = -1
                        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                            dy = 1
                        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                            dx = -1
                        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                            dx = 1
                        
                        if dx == 0 and dy == 0:
                            dx = 1  # Default forward
                        
                        self.player.dodge((dx, dy))
                        # small dodge VFX
                        if self.vfx:
                            self.vfx.create_impact(self.player.x, self.player.y, color=(100,200,255), size=12)
                    
                    elif event.key == pygame.K_TAB:
                        self.ui.toggle_stats()
                    
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'paused'
                        self.ui.add_message('Game Paused')
                    
                    elif event.key == pygame.K_h:
                        self.show_hitboxes = not self.show_hitboxes
                        self.save_settings()
                
                elif self.state == 'paused':
                    if event.key == pygame.K_ESCAPE:
                        self.ui.add_message('Game Resumed')
                        self.state = 'playing'
                    elif event.key == pygame.K_r:
                        if self.auto_save:
                            self.meta.save()
                            self.ui.add_message('Game saved!')
                        self.state = 'menu'
                    elif event.key == pygame.K_s:
                        self.meta.save()
                        self.ui.add_message('Game Saved!')
                        self.state = 'playing'
                    elif event.key == pygame.K_h:
                        self.show_hitboxes = not self.show_hitboxes
                

                elif self.state == 'options':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                    elif event.key == pygame.K_1:
                        self.auto_save = not self.auto_save
                    elif event.key == pygame.K_2:
                        self.show_hitboxes = not self.show_hitboxes
                    elif event.key == pygame.K_3:
                        self.state = 'reset_confirm'


                elif self.state == 'game_over':
                    if event.key == pygame.K_r:
                        self.new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                elif self.state == 'reset_confirm':
                    if event.key in (pygame.K_y, pygame.K_RETURN):
                        self.reset_all_data()
                        self.state = 'menu'
                    elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                        self.state = 'options'


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == 'playing' and event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x = mouse_x + self.camera_offset[0]
                    world_y = mouse_y + self.camera_offset[1]

                    if self.player is not None:
                        dx = world_x - self.player.x
                        dy = world_y - self.player.y
                        self.player.aim_angle = math.atan2(dy, dx)
                        
                        # Perform the attack and process hits
                        attack_angle = self.player.attack((world_x, world_y))
                        if attack_angle is not None:
                                # Create slash VFX for player's attack
                                if self.vfx:
                                    self.vfx.create_slash(self.player.x, self.player.y, attack_angle, color=YELLOW, size=64)
                                self._process_attack(attack_angle)

    def _process_attack(self, angle):
        """Process player attack"""
        # Check for hits
        for enemy in self.level.enemies:
            dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
            if dist <= ATTACK_RANGE:
                # Check angle
                enemy_angle = math.atan2(enemy.y - self.player.y, enemy.x - self.player.x)
                
                angle_diff = (angle - enemy_angle + math.pi) % (2 * math.pi) - math.pi
                if abs(angle_diff) < ATTACK_CONE_ANGLE:  # Hit cone
                    damage = self.player.damage
                    self.player.damage_dealt += damage
                    if self.vfx:
                        self.vfx.create_impact(enemy.x, enemy.y, color=enemy.color, size=24)
                    
                    if enemy.take_damage(damage):
                        # Enemy killed
                        self.player.kills += 1
                        souls = enemy.xp
                        self.souls_earned += souls
                        self.meta.add_souls(souls)
                        self.level.enemies.remove(enemy)
                        self.ui.add_message(f'+{souls} souls')
                        
                        if enemy.is_boss:
                            self.ui.add_message('BOSS DEFEATED!')
                        
                        # Create death particles
                        self._create_particles(enemy.x, enemy.y, enemy.color)

                        if self.auto_save:
                            self.meta.save()
    
    def _create_particles(self, x, y, color):
        """Create particle effect"""
        for _ in range(10):
            angle = math.radians(pygame.time.get_ticks() % 360 + _ * 36)
            speed = 5
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                'life': PRATICLE_LIFETIME   
            })
    
    def update(self):
        if self.state == 'playing':
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_x = mouse_pos[0] + self.camera_offset[0]
            world_mouse_y = mouse_pos[1] + self.camera_offset[1]
            
            # Update player
            self.player.update(keys, (world_mouse_x, world_mouse_y), 
                             (self.level.width, self.level.height))
            
            # Update level
            self.level.update(self.player)
            
            # Check item collection
            collected_items = self.level.check_item_collection(self.player)
            for item_type in collected_items:
                if item_type == 'health_potion':
                    self.player.heal(50)
                    self.ui.add_message('Health restored!')
                elif item_type == 'stamina_potion':
                    self.player.restore_stamina(50)
                    self.ui.add_message('Stamina restored!')
                elif item_type == 'weapon_upgrade':
                    self.player.upgrade_weapon()
                    self.ui.add_message(f'Weapon upgraded! Lv{self.player.weapon_level}')
                elif item_type == 'armor_upgrade':
                    self.player.upgrade_armor()
                    self.ui.add_message(f'Armor upgraded! Lv{self.player.armor_level}')
            
            # Update enemies
            for enemy in self.level.enemies:
                action = enemy.update(self.player, self.level.enemies, self.vfx)

                # Enemy attacks
                if action:
                    # If enemy locked a fixed attack target (non-boss), resolve attack at that point
                    if getattr(enemy, 'attack_target_fixed', False) and getattr(enemy, 'attack_target', None):
                        tx, ty = enemy.attack_target
                        # Show impact at the fixed target location
                        if self.vfx:
                            self.vfx.create_impact(tx, ty, color=enemy.color, size=24)

                        # Player is hit only if within small radius of the target
                        hit_dist = math.sqrt((self.player.x - tx)**2 + (self.player.y - ty)**2)
                        hit_radius = self.player.size + enemy.size + 10
                        if hit_dist <= hit_radius:
                            result = self.player.take_damage(enemy.damage, (tx, ty))
                        else:
                            result = None
                    else:
                        # Dynamic attack (bosses): resolve against player's current position
                        dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                        if dist <= enemy.attack_range + self.player.size + enemy.size:
                            # Show impact at player's current position
                            if self.vfx:
                                self.vfx.create_impact(self.player.x, self.player.y, color=enemy.color, size=24)
                            result = self.player.take_damage(enemy.damage, (enemy.x, enemy.y))
                        else:
                            result = None

                    if result == 'perfect_dodge':
                        self.player.perfect_dodges += 1
                        self.ui.add_message('PERFECT DODGE!')
                    elif result == 'perfect_block':
                        self.player.perfect_blocks += 1
                        self.ui.add_message('PERFECT BLOCK!')
                    elif result == 'hit':
                        self.ui.add_message('Hit!')
                    elif result == 'block':
                        self.ui.add_message('Blocked!')
            
            # Update camera
            self.camera_offset[0] = self.player.x - WINDOW_WIDTH // 2
            self.camera_offset[1] = self.player.y - WINDOW_HEIGHT // 2
            
            # Clamp camera
            if self.level.width > WINDOW_WIDTH:
                    self.camera_offset[0] = max(0, min(self.level.width - WINDOW_WIDTH, self.camera_offset[0]))
            else:
                    self.camera_offset[0] = (self.level.width - WINDOW_WIDTH) // 2
                
            if self.level.height > WINDOW_HEIGHT:
                    self.camera_offset[1] = max(0, min(self.level.height - WINDOW_HEIGHT, self.camera_offset[1]))
            else:
                    self.camera_offset[1] = (self.level.height - WINDOW_HEIGHT) // 2
            
            # Update particles
            for particle in self.particles:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 1
            self.particles = [p for p in self.particles if p['life'] > 0]
            # Update VFX
            if self.vfx:
                self.vfx.update()
            
            # Update UI
            self.ui.update()
            
            # Check for level completion
            if self.level.cleared and self.level.check_portal_enter(self.player):
                    self.next_level()
            
            # Check for game over
            if self.player.health <= 0:
                self.state = 'game_over'
                if self.auto_save:
                    self.meta.save()
    
    def draw(self):
        if self.state == 'menu':
            self.ui.draw_menu(self.screen, self.meta)
        elif self.state == 'options':
            self.ui.draw_options(self.screen, self.show_hitboxes, self.auto_save)
        elif self.state == 'reset_confirm':
            self.ui.draw_options(self.screen, self.show_hitboxes, self.auto_save)
            self.ui.draw_reset_confirmation(self.screen)
        elif self.state == 'playing' or self.state == 'paused':
            # Draw level
            self.level.draw(self.screen, self.camera_offset)

            # Draw particles
            for particle in self.particles:
                px = particle['x'] - self.camera_offset[0]
                py = particle['y'] - self.camera_offset[1]
                size = max(1, particle['life'] // 5)
                pygame.draw.circle(self.screen, particle['color'], (int(px), int(py)), size)
            
            # Draw wind-up VFX behind characters
            if self.vfx:
                for effect in list(self.vfx.windup_effects):
                    effect.draw(self.screen, self.camera_offset)

            # Draw enemies
            for enemy in self.level.enemies:
                enemy.draw(self.screen, self.camera_offset, self.show_hitboxes)
            
            # Draw player
            self.player.draw(self.screen, self.camera_offset, self.show_hitboxes)

            # Draw slashes and impacts on top
            if self.vfx:
                for effect in list(self.vfx.slash_effects):
                    effect.draw(self.screen, self.camera_offset)
                for effect in list(self.vfx.impact_effects):
                    effect.draw(self.screen, self.camera_offset)


            # Draw attack range if hitboxes enabled
            if self.show_hitboxes:
                player_screen_x = self.player.x - self.camera_offset[0]
                player_screen_y = self.player.y - self.camera_offset[1]
                pygame.draw.circle(self.screen, (255, 255, 0, 100), 
                                 (int(player_screen_x), int(player_screen_y)), 
                                 ATTACK_RANGE, 2)
                

            # Draw UI
            self.ui.draw_hud(self.screen, self.player, self.level)
            self.ui.draw_stats(self.screen, self.player)

            if self.state == 'paused':
               self.ui.draw_pause(self.screen)
        
        elif self.state == 'game_over':
            # Draw last frame
            self.level.draw(self.screen, self.camera_offset)
            for enemy in self.level.enemies:
                enemy.draw(self.screen, self.camera_offset, self.show_hitboxes)
            self.player.draw(self.screen, self.camera_offset, self.show_hitboxes)
            
            # Draw game over overlay
            self.ui.draw_game_over(self.screen, self.player, self.current_level_number, 
                                  self.souls_earned)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
