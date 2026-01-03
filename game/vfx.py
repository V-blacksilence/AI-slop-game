import pygame
import math
from game.constants import *

class SlashVFX:
    """Visual effect for slash attacks"""
    def __init__(self, x, y, angle, color, size=60, duration=15):
        self.x = x
        self.y = y
        self.angle = angle
        self.color = color
        self.size = size
        self.duration = duration
        self.lifetime = duration
        self.active = True
        
        # Slash arc properties
        self.arc_width = math.pi / 3  # 60 degrees
        self.start_angle = angle - self.arc_width / 2
        self.end_angle = angle + self.arc_width / 2
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
    
    def draw(self, screen, camera_offset):
        if not self.active:
            return
        
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        # Calculate fade based on lifetime
        fade = self.lifetime / self.duration
        
        # Calculate current size (grows then shrinks)
        if fade > 0.5:
            size_mult = 1 + (1 - fade) * 0.5  # Grow in first half
        else:
            size_mult = 0.5 + fade  # Shrink in second half
        
        current_size = int(self.size * size_mult)
        
        # Calculate alpha
        alpha = int(255 * fade)
        
        # Create color with alpha
        color = (*self.color[:3], alpha) if len(self.color) == 3 else self.color
        
        # Draw slash arc
        points = []
        num_points = 8
        
        # Inner arc
        for i in range(num_points + 1):
            progress = i / num_points
            angle = self.start_angle + (self.end_angle - self.start_angle) * progress
            inner_radius = current_size * 0.3
            px = draw_x + math.cos(angle) * inner_radius
            py = draw_y + math.sin(angle) * inner_radius
            points.append((px, py))
        
        # Outer arc (reverse order to close polygon)
        for i in range(num_points, -1, -1):
            progress = i / num_points
            angle = self.start_angle + (self.end_angle - self.start_angle) * progress
            outer_radius = current_size
            px = draw_x + math.cos(angle) * outer_radius
            py = draw_y + math.sin(angle) * outer_radius
            points.append((px, py))
        
        # Draw the slash with transparency
        if len(points) > 2:
            # Create temporary surface for alpha blending
            temp_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surface, color, points)
            screen.blit(temp_surface, (0, 0))
            
            # Draw slash outline
            outline_color = (255, 255, 255, int(alpha * 0.8))
            pygame.draw.lines(temp_surface, outline_color, False, points[:num_points + 1], 3)
            screen.blit(temp_surface, (0, 0))


class WindUpVFX:
    """Visual effect for enemy wind-up before attack"""
    def __init__(self, x, y, target_x=None, target_y=None, duration=30, track_target=False, target_getter=None):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.duration = duration
        self.lifetime = duration
        self.active = True
        self.track_target = track_target
        self.target_getter = target_getter

        # Calculate initial direction
        if self.track_target and self.target_getter:
            tx, ty = self.target_getter()
            dx = tx - x
            dy = ty - y
        elif target_x is not None and target_y is not None:
            dx = target_x - x
            dy = target_y - y
        else:
            dx = 1
            dy = 0
        self.angle = math.atan2(dy, dx)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
    
    def draw(self, screen, camera_offset):
        if not self.active:
            return
        
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        # Update angle if tracking
        if self.track_target and self.target_getter:
            try:
                tx, ty = self.target_getter()
                dx = tx - self.x
                dy = ty - self.y
                self.angle = math.atan2(dy, dx)
            except Exception:
                tx, ty = (self.target_x, self.target_y)
        else:
            tx, ty = (self.target_x, self.target_y)

        # Calculate progress (0 to 1)
        progress = 1 - (self.lifetime / self.duration)

        # Draw a tracer line from the source to the target (fades with progress)
        if tx is not None and ty is not None:
            target_screen_x = tx - camera_offset[0]
            target_screen_y = ty - camera_offset[1]
            alpha = int(200 * progress)
            thickness = max(1, int(2 + progress * 3))
            tracer_color = (255, 80, 80, alpha)
            temp = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(temp, tracer_color, (int(draw_x), int(draw_y)), (int(target_screen_x), int(target_screen_y)), thickness)
            # Add a faint glow by drawing again with lower alpha and larger thickness
            glow_color = (255, 120, 120, int(alpha * 0.4))
            pygame.draw.line(temp, glow_color, (int(draw_x), int(draw_y)), (int(target_screen_x), int(target_screen_y)), max(1, thickness + 2))
            screen.blit(temp, (0, 0))
        
        # Pulsing red indicator
        intensity = int(100 + 155 * progress)
        color = (intensity, 0, 0)
        
        # Draw charging lines pointing at target
        num_lines = 3
        for i in range(num_lines):
            offset_angle = self.angle + (i - 1) * 0.3
            line_length = 30 + progress * 20
            
            # Start point (moves inward as it charges)
            start_dist = 40 - progress * 15
            start_x = draw_x + math.cos(offset_angle) * start_dist
            start_y = draw_y + math.sin(offset_angle) * start_dist
            
            # End point
            end_x = start_x + math.cos(offset_angle) * line_length
            end_y = start_y + math.sin(offset_angle) * line_length
            
            # Draw line with increasing thickness
            thickness = max(1, int(2 + progress * 2))
            pygame.draw.line(screen, color, (int(start_x), int(start_y)), 
                           (int(end_x), int(end_y)), thickness)
        
        # Draw warning symbol in front of enemy
        warning_dist = 50
        warning_x = draw_x + math.cos(self.angle) * warning_dist
        warning_y = draw_y + math.sin(self.angle) * warning_dist
        
        # Pulsing "!" symbol
        pulse_size = 1 + math.sin(progress * math.pi * 4) * 0.2
        font_size = int(30 * pulse_size)
        font = pygame.font.Font(None, font_size)
        warning_text = font.render('!', True, (255, 0, 0))
        text_rect = warning_text.get_rect(center=(int(warning_x), int(warning_y)))
        
        # Draw glow behind warning
        glow_radius = int(15 * pulse_size)
        pygame.draw.circle(screen, (100, 0, 0), (int(warning_x), int(warning_y)), glow_radius)
        pygame.draw.circle(screen, (255, 100, 100), (int(warning_x), int(warning_y)), glow_radius // 2)
        
        screen.blit(warning_text, text_rect)
        
        # Draw charge indicator (semicircle that fills up)
        if progress > 0.2:
            arc_rect = pygame.Rect(draw_x - 25, draw_y - 25, 50, 50)
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * progress)
            
            # Draw arc segments
            points = [(draw_x, draw_y)]
            for angle_step in range(int(progress * 100)):
                angle = start_angle + (end_angle - start_angle) * (angle_step / 100)
                px = draw_x + math.cos(angle) * 25
                py = draw_y + math.sin(angle) * 25
                points.append((px, py))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, (255, 50, 50, 100), points)
                pygame.draw.lines(screen, (255, 0, 0), False, points, 2)


class ImpactVFX:
    """Visual effect for successful hits"""
    def __init__(self, x, y, color=(255, 255, 255), size=20):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = 10
        self.active = True
        self.particles = []
        
        # Create impact particles
        for i in range(8):
            angle = (i / 8) * math.pi * 2
            speed = 3 + (i % 2) * 2
            self.particles.append({
                'angle': angle,
                'speed': speed,
                'distance': 0
            })
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
        
        # Update particles
        for particle in self.particles:
            particle['distance'] += particle['speed']
            particle['speed'] *= 0.9
    
    def draw(self, screen, camera_offset):
        if not self.active:
            return
        
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        fade = self.lifetime / 10
        alpha = int(255 * fade)
        
        # Draw center flash
        flash_size = int(self.size * (1 + (1 - fade) * 0.5))
        pygame.draw.circle(screen, (*self.color[:3], alpha), 
                         (int(draw_x), int(draw_y)), flash_size)
        pygame.draw.circle(screen, (255, 255, 255, int(alpha * 0.8)), 
                         (int(draw_x), int(draw_y)), flash_size // 2)
        
        # Draw impact particles
        for particle in self.particles:
            px = draw_x + math.cos(particle['angle']) * particle['distance']
            py = draw_y + math.sin(particle['angle']) * particle['distance']
            particle_size = max(1, int(4 * fade))
            pygame.draw.circle(screen, (*self.color[:3], alpha), 
                             (int(px), int(py)), particle_size)


class VFXManager:
    """Manages all visual effects"""
    def __init__(self):
        self.slash_effects = []
        self.windup_effects = []
        self.impact_effects = []
    
    def create_slash(self, x, y, angle, color=YELLOW, size=60):
        """Create a slash effect"""
        vfx = SlashVFX(x, y, angle, color, size)
        self.slash_effects.append(vfx)
        return vfx
    
    def create_windup(self, x, y, target_x, target_y, duration=30):
        """Create a wind-up effect"""
        vfx = WindUpVFX(x, y, target_x, target_y, duration)
        self.windup_effects.append(vfx)
        return vfx
    
    def create_impact(self, x, y, color=(255, 255, 255), size=20):
        """Create an impact effect"""
        vfx = ImpactVFX(x, y, color, size)
        self.impact_effects.append(vfx)
        return vfx
    
    def update(self):
        """Update all effects"""
        # Update and remove inactive effects
        for effect_list in [self.slash_effects, self.windup_effects, self.impact_effects]:
            for effect in effect_list[:]:
                effect.update()
                if not effect.active:
                    effect_list.remove(effect)
    
    def draw(self, screen, camera_offset):
        """Draw all effects"""
        # Draw wind-ups first (behind characters)
        for effect in self.windup_effects:
            effect.draw(screen, camera_offset)
        
        # Draw slashes
        for effect in self.slash_effects:
            effect.draw(screen, camera_offset)
        
        # Draw impacts on top
        for effect in self.impact_effects:
            effect.draw(screen, camera_offset)
    
    def clear(self):
        """Clear all effects"""
        self.slash_effects.clear()
        self.windup_effects.clear()
        self.impact_effects.clear()
