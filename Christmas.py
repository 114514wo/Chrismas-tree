import pygame
import random
import math
import colorsys
from pygame import gfxdraw
import cv2
import numpy as np
import os
import shutil  # 用于检查ffmpeg是否存在

# 初始化Pygame
pygame.init()

# 设置窗口和视频参数
WIDTH = 1200  # 扩大宽度
HEIGHT = 800
FPS = 60
DURATION = 15  # 视频时长(秒)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("圣诞快乐")

# 颜色定义
DARK_BLUE = (5, 15, 25)
WHITE = (255, 255, 255)
LIGHT_BLUE = (140, 180, 200)
PINK = (200, 160, 170)
YELLOW = (255, 255, 180)
BROWN = (139, 69, 19)

class CalligraphyText:
    def __init__(self, text, target_y):
        self.text = text
        self.particles = []
        self.target_y = target_y
        self.trail_points = []  # 存储笔画轨迹点
        self.current_stroke = 0
        self.generate_text_path()
        
    def generate_text_path(self):
        # 定义"Merry Christmas"的笔画路径点
        text_paths = {
            'M': [(0,0), (0,50), (25,0), (50,50), (50,0)],
            'e': [(60,25), (85,25), (85,0), (60,0), (60,50), (85,50)],
            'r': [(95,0), (95,50), (120,25)],
            'r2': [(130,0), (130,50), (155,25)],
            'y': [(165,0), (165,25), (180,50), (165,25), (150,50)],
            'C': [(220,0), (195,0), (195,50), (220,50)],
            'h': [(230,0), (230,50), (255,25), (255,50)],
            'r3': [(265,0), (265,50), (290,25)],
            'i': [(300,0), (300,50)],
            's': [(310,0), (335,0), (335,25), (310,25), (310,50), (335,50)],
            't': [(345,25), (370,25), (357,0), (357,50)],
            'm': [(380,50), (380,0), (405,25), (430,0), (430,50)],
            'a': [(440,50), (465,50), (465,0), (440,0), (440,50)],
            's2': [(475,0), (500,0), (500,25), (475,25), (475,50), (500,50)]
        }
        
        # 缩放和定位路径点
        scale = 1.2
        base_x = WIDTH//2 - 250 * scale
        base_y = self.target_y
        
        for stroke, points in text_paths.items():
            scaled_points = [(base_x + x*scale, base_y + y*scale) for x, y in points]
            self.trail_points.append(scaled_points)
            
    def create_glow_particle(self, x, y):
        return {
            'pos': [x, y],
            'life': random.uniform(0.5, 1.0),
            'size': random.randint(2, 4),
            'alpha': random.randint(150, 255),
            'color': (255, 255, random.randint(200, 255))  # 略微泛黄的白色
        }
        
    def update(self, current_time):
        if self.current_stroke < len(self.trail_points):
            points = self.trail_points[self.current_stroke]
            for i in range(len(points)-1):
                start = points[i]
                end = points[i+1]
                # 在笔画路径上创建发光粒子
                steps = 10
                for t in range(steps):
                    x = start[0] + (end[0] - start[0]) * t/steps
                    y = start[1] + (end[1] - start[1]) * t/steps
                    # 添加主粒子和周围的光晕粒子
                    self.particles.append(self.create_glow_particle(x, y))
                    # 添加周围的光晕
                    for _ in range(3):
                        offset_x = random.uniform(-5, 5)
                        offset_y = random.uniform(-5, 5)
                        self.particles.append(self.create_glow_particle(x + offset_x, y + offset_y))
            self.current_stroke += 1
            
        # 更新现有粒子
        new_particles = []
        for p in self.particles:
            p['life'] -= 0.01
            if p['life'] > 0:
                p['alpha'] = int(p['alpha'] * p['life'])
                new_particles.append(p)
        self.particles = new_particles
        
    def draw(self, surface):
        # 绘制发光效果
        for p in self.particles:
            # 绘制主粒子
            color = (*p['color'][:3], p['alpha'])
            gfxdraw.filled_circle(surface, 
                                int(p['pos'][0]), 
                                int(p['pos'][1]), 
                                p['size'], color)
            # 绘制外层光晕
            glow_color = (*p['color'][:3], p['alpha']//3)
            gfxdraw.filled_circle(surface, 
                                int(p['pos'][0]), 
                                int(p['pos'][1]), 
                                p['size']*2, glow_color)

class Particle:
    def __init__(self, x, y, target_x, target_y, color, size, is_outer=False):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.color = color
        self.size = size
        self.alpha = random.randint(150, 255)
        self.speed = random.uniform(0.02, 0.05)
        self.is_outer = is_outer
        self.angle = random.uniform(0, 2*math.pi)
        self.orbit_radius = random.uniform(2, 5)
        self.reached_target = False
        
    def update(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if not self.reached_target and dist > 1:
            # 向目标位置移动
            self.x += dx * self.speed
            self.y += dy * self.speed
        else:
            self.reached_target = True
            if self.is_outer:
                # 外圈粒子围绕目标位置运动
                self.angle += 0.02
                self.x = self.target_x + math.cos(self.angle) * self.orbit_radius
                self.y = self.target_y + math.sin(self.angle) * self.orbit_radius
            else:
                # 内部粒子轻微摆动
                self.x += random.uniform(-0.2, 0.2)
                self.y += random.uniform(-0.2, 0.2)
            
        self.alpha = max(100, min(255, self.alpha + random.randint(-1, 1)))

    def draw(self, surface):
        color_with_alpha = (*self.color, self.alpha)
        gfxdraw.filled_circle(surface, int(self.x), int(self.y), 
                            self.size, color_with_alpha)

class SnowflakeStar:
    """替换原来的Star类，实现雪花状的星星"""
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.angle = 0
        self.alpha = 0  # 初始透明
        self.glow_size = size * 1.5
        self.branches = 6  # 六角雪花
        
    def draw(self, surface):
        # 绘制发光效果
        for glow_size in [self.glow_size * 2, self.glow_size * 1.5, self.glow_size]:
            for i in range(self.branches):
                angle = self.angle + (2 * math.pi * i) / self.branches
                
                # 主臂
                end_x = self.x + math.cos(angle) * glow_size
                end_y = self.y + math.sin(angle) * glow_size
                
                # 计算发光强度
                alpha = int(self.alpha * (self.glow_size - glow_size) / self.glow_size)
                glow_color = (255, 255, 200, alpha//4)
                
                # 绘制主臂
                pygame.draw.line(surface, glow_color, 
                               (self.x, self.y), 
                               (end_x, end_y), 
                               int(glow_size/4))
                
                # 绘制分支
                branch_size = glow_size * 0.5
                for offset in [-30, 30]:
                    branch_angle = angle + math.radians(offset)
                    mid_x = self.x + math.cos(angle) * (glow_size * 0.5)
                    mid_y = self.y + math.sin(angle) * (glow_size * 0.5)
                    branch_end_x = mid_x + math.cos(branch_angle) * branch_size
                    branch_end_y = mid_y + math.sin(branch_angle) * branch_size
                    pygame.draw.line(surface, glow_color,
                                   (mid_x, mid_y),
                                   (branch_end_x, branch_end_y),
                                   int(glow_size/6))

class Snowflake:
    def __init__(self):
        self.reset()
        self.y = random.randint(-50, HEIGHT//2)
        self.rotation = random.uniform(0, 360)
        self.rotate_speed = random.uniform(-2, 2)
        
    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = -50
        self.size = random.randint(5, 8)  # 增大雪花尺寸
        self.speed = random.uniform(1, 3)
        self.drift = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(150, 255)
        
    def draw_snowflake_shape(self, surface, x, y, size, color):
        # 绘制六角雪花
        for i in range(6):
            angle = math.radians(self.rotation + i * 60)
            end_x = x + math.cos(angle) * size
            end_y = y + math.sin(angle) * size
            
            # 主臂
            pygame.draw.line(surface, color, (x, y), (end_x, end_y), 2)
            
            # 分支
            branch_size = size * 0.5
            branch_angle1 = angle + math.radians(30)
            branch_angle2 = angle - math.radians(30)
            
            mid_x = x + math.cos(angle) * (size * 0.5)
            mid_y = y + math.sin(angle) * (size * 0.5)
            
            branch1_x = mid_x + math.cos(branch_angle1) * branch_size
            branch1_y = mid_y + math.sin(branch_angle1) * branch_size
            
            branch2_x = mid_x + math.cos(branch_angle2) * branch_size
            branch2_y = mid_y + math.sin(branch_angle2) * branch_size
            
            pygame.draw.line(surface, color, (mid_x, mid_y), (branch1_x, branch1_y), 1)
            pygame.draw.line(surface, color, (mid_x, mid_y), (branch2_x, branch2_y), 1)
            
    def update(self):
        self.y += self.speed
        self.x += self.drift
        self.rotation += self.rotate_speed
        if self.y > HEIGHT:
            self.reset()
            
    def draw(self, surface):
        # 绘制雪花的发光效果
        glow_color = (255, 255, 255, self.alpha//4)
        self.draw_snowflake_shape(surface, int(self.x), int(self.y), 
                                self.size*1.2, glow_color)
        # 绘制雪花主体
        main_color = (255, 255, 255, self.alpha)
        self.draw_snowflake_shape(surface, int(self.x), int(self.y), 
                                self.size, main_color)

class LightBeam:
    def __init__(self):
        self.y = HEIGHT  # 从底部开始
        # 创建两个光团的属性
        self.beam1 = {
            'angle': 0,
            'radius': 0,
            'particles': []
        }
        self.beam2 = {
            'angle': math.pi,  # 初始角度相差180度
            'radius': 0,
            'particles': []
        }
        self.particles = []  # 添加这行，用于存储所有粒子
        self.speed = 4
        self.revealed_particles = []
        self.tree_height = HEIGHT/2
        self.max_radius = self.tree_height/2
        self.reached_top = False
        self.final_y = HEIGHT/4
        self.snowflake_star = None  # 替换原来的star
        self.snowflakes = [Snowflake() for _ in range(200)]
        self.transition_progress = 0
        self.flash_alpha = 0
        self.merge_started = False
        self.merge_progress = 0
        self.merge_particles = []  # 用于存储合并时的粒子
        
    def create_light_particle(self, x, y, color=(255, 255, 200)):
        return {
            'pos': [x, y],
            'life': 1.0,
            'size': random.randint(3, 6),
            'alpha': random.randint(200, 255),
            'color': color
        }
        
    def update(self, tree_particles):
        # 更新雪花（始终进行）
        for snowflake in self.snowflakes:
            snowflake.update()
            if snowflake.y > HEIGHT:
                snowflake.reset()
            
        if not self.reached_top:
            # 更新两个光束的位置
            self.y -= self.speed
            
            # 第一个光束（顺时针）
            self.beam1['angle'] += 0.1
            progress = (HEIGHT - self.y) / (HEIGHT - self.final_y)
            self.beam1['radius'] = self.max_radius * math.sin(progress * math.pi)
            
            # 第二个光束（逆时针）
            self.beam2['angle'] -= 0.1
            self.beam2['radius'] = self.beam1['radius']
            
            # 计算两个光束的位置
            beam1_x = WIDTH//2 + math.cos(self.beam1['angle']) * self.beam1['radius']
            beam2_x = WIDTH//2 + math.cos(self.beam2['angle']) * self.beam2['radius']
            
            # 检查是否到达顶部
            if self.y <= self.final_y:
                self.reached_top = True
                self.merge_started = True
                self.flash_alpha = 255
                
            # 创建光束粒子
            for beam_x in [beam1_x, beam2_x]:
                particle = self.create_light_particle(beam_x, self.y)
                self.particles.append(particle)
                
                # 添加拖尾效果
                for _ in range(5):
                    offset_x = random.uniform(-10, 10)
                    offset_y = random.uniform(-10, 10)
                    self.particles.append(self.create_light_particle(
                        beam_x + offset_x, 
                        self.y + offset_y
                    ))
        
        elif self.merge_started:
            # 合并效果
            self.merge_progress = min(1, self.merge_progress + 0.01)
            
            if not self.snowflake_star:
                self.snowflake_star = SnowflakeStar(WIDTH//2, self.final_y, 30)
            
            # 更新雪花星星
            if self.snowflake_star:
                self.snowflake_star.alpha = int(255 * self.merge_progress)
                self.snowflake_star.angle += 0.01
            
            # 创建合并效果的粒子
            if self.merge_progress < 0.8:
                angles = [i * (2 * math.pi / 6) for i in range(6)]
                for angle in angles:
                    radius = (1 - self.merge_progress) * self.max_radius/2
                    x = WIDTH//2 + math.cos(angle) * radius
                    y = self.final_y + math.sin(angle) * radius
                    
                    for _ in range(2):
                        offset_x = random.uniform(-5, 5)
                        offset_y = random.uniform(-5, 5)
                        self.merge_particles.append({
                            'pos': [x + offset_x, y + offset_y],
                            'target_x': WIDTH//2,
                            'target_y': self.final_y,
                            'life': random.uniform(0.5, 1.0),
                            'speed': random.uniform(0.05, 0.1),
                            'size': random.randint(2, 4),
                            'alpha': random.randint(150, 255)
                        })
        
        # 更新所有粒子
        new_particles = []
        for p in self.particles:
            p['life'] -= 0.02
            if p['life'] > 0:
                p['alpha'] = int(p['alpha'] * p['life'])
                new_particles.append(p)
        self.particles = new_particles
        
        # 更新合并粒子
        new_merge_particles = []
        for p in self.merge_particles:
            dx = p['target_x'] - p['pos'][0]
            dy = p['target_y'] - p['pos'][1]
            p['pos'][0] += dx * p['speed']
            p['pos'][1] += dy * p['speed']
            p['life'] -= 0.02
            if p['life'] > 0:
                p['alpha'] = int(p['alpha'] * p['life'])
                new_merge_particles.append(p)
        self.merge_particles = new_merge_particles
        
        # 显现树的粒子
        reveal_range = 100
        for tree_particle in tree_particles:
            if tree_particle not in self.revealed_particles:
                if self.y - reveal_range < tree_particle.target_y < self.y + 20:
                    self.revealed_particles.append(tree_particle)
        
        return self.reached_top

    def draw(self, surface):
        # 先绘制雪花
        for snowflake in self.snowflakes:
            snowflake.draw(surface)
        
        # 绘制光束粒子
        for p in self.particles:
            color = (*p['color'], p['alpha'])
            # 主光点
            gfxdraw.filled_circle(surface, 
                                int(p['pos'][0]), 
                                int(p['pos'][1]), 
                                p['size'], color)
            # 光晕效果
            glow_color = (*p['color'], p['alpha']//3)
            gfxdraw.filled_circle(surface, 
                                int(p['pos'][0]), 
                                int(p['pos'][1]), 
                                p['size']*2, glow_color)
        
        # 绘制合并效果
        if self.merge_started:
            # 绘制合并粒子
            for p in self.merge_particles:
                color = (255, 255, 200, p['alpha'])
                gfxdraw.filled_circle(surface, 
                                    int(p['pos'][0]), 
                                    int(p['pos'][1]), 
                                    p['size'], color)
                glow_color = (255, 255, 200, p['alpha']//3)
                gfxdraw.filled_circle(surface, 
                                    int(p['pos'][0]), 
                                    int(p['pos'][1]), 
                                    p['size']*2, glow_color)
            
            # 绘制雪花星星
            if self.snowflake_star:
                self.snowflake_star.draw(surface)

class ChristmasTree:
    def __init__(self):
        self.particles = []
        self.light_beam = LightBeam()
        self.beam_completed = False
        self.generate_tree_points()
    
    def generate_tree_points(self):
        tree_points = []
        
        # 星星
        for _ in range(50):
            angle = random.uniform(0, 2*math.pi)
            radius = random.uniform(0, 15)
            x = WIDTH//2 + math.cos(angle) * radius
            y = HEIGHT//4 + math.sin(angle) * radius
            tree_points.append((x, y, WHITE, 2, False))
        
        # 树的主体
        for y in range(HEIGHT//4, HEIGHT*3//4, 5):
            width = (y - HEIGHT//4) * 0.5
            for i in range(int(width/3)):
                x = WIDTH//2 + random.uniform(-width, width)
                color = random.choice([LIGHT_BLUE, PINK, WHITE])
                size = random.randint(2, 4)
                # 最外圈的点标记为outer
                is_outer = abs(x - WIDTH//2) > width * 0.8
                tree_points.append((x, y, color, size, is_outer))
        
        # 装饰灯
        for _ in range(20):
            y = random.randint(HEIGHT//4, HEIGHT*3//4)
            width = (y - HEIGHT//4) * 0.4
            x = WIDTH//2 + random.uniform(-width, width)
            tree_points.append((x, y, YELLOW, 4, False))
            
        # 树根
        trunk_width = 40
        trunk_height = 80
        trunk_y = HEIGHT*3//4
        for y in range(trunk_y, trunk_y + trunk_height, 4):
            for x in range(WIDTH//2 - trunk_width//2, WIDTH//2 + trunk_width//2, 4):
                tree_points.append((x, y, BROWN, 3, False))
        
        # 为每个目标点创建粒子
        for x, y, color, size, is_outer in tree_points:
            start_x = random.choice([random.randint(0, WIDTH//4), 
                                   random.randint(WIDTH*3//4, WIDTH)])
            start_y = random.randint(0, HEIGHT)
            self.particles.append(Particle(start_x, start_y, x, y, color, size, is_outer))

    def update(self):
        if not self.beam_completed:
            # 更新光束并检查是否完成
            self.beam_completed = self.light_beam.update(self.particles)
        
        # 只更新已显现的粒子
        for particle in self.light_beam.revealed_particles:
            particle.update()
    
    def draw(self, surface):
        # 绘制已显现的粒子
        for particle in self.light_beam.revealed_particles:
            particle.draw(surface)
        # 绘制光束
        self.light_beam.draw(surface)

# 添加新的文字效果类
class GlowingText:
    def __init__(self):
        self.text = "Merry Christmas"
        self.font_size = 80
        self.font = pygame.font.Font(None, self.font_size)
        self.color = (255, 255, 255)
        self.glow_particles = []
        self.x = WIDTH * 0.3  # 文字位置
        self.y = HEIGHT * 0.7
        self.spiral_particles = []  # 用于螺旋光效
        self.time = 0
        
    def create_spiral_particle(self):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 4)
        return {
            'x': self.x + len(self.text) * 20,  # 从文字末尾开始
            'y': self.y,
            'angle': angle,
            'speed': speed,
            'radius': 0,
            'alpha': 255,
            'life': 1.0
        }
        
    def update(self):
        self.time += 0.05
        
        # 创建新的螺旋粒子
        if random.random() < 0.3:
            self.spiral_particles.append(self.create_spiral_particle())
        
        # 更新螺旋粒子
        new_particles = []
        for p in self.spiral_particles:
            p['radius'] += p['speed']
            p['angle'] += 0.1
            p['life'] -= 0.02
            
            if p['life'] > 0:
                p['alpha'] = int(255 * p['life'])
                new_particles.append(p)
                
        self.spiral_particles = new_particles
        
        # 创建文字周围的发光粒子
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=(self.x + text_surface.get_width()/2, self.y))
        
        # 在文字轮廓周围添加发光粒子
        for _ in range(2):
            x = text_rect.x + random.randint(0, text_rect.width)
            y = text_rect.y + random.randint(0, text_rect.height)
            self.glow_particles.append({
                'x': x,
                'y': y,
                'life': random.uniform(0.3, 0.7),
                'alpha': random.randint(100, 200),
                'size': random.randint(2, 4)
            })
            
        # 更新发光粒子
        new_glow = []
        for p in self.glow_particles:
            p['life'] -= 0.02
            if p['life'] > 0:
                p['alpha'] = int(p['alpha'] * p['life'])
                new_glow.append(p)
        self.glow_particles = new_glow

    def draw(self, surface):
        # 绘制螺旋光效
        for p in self.spiral_particles:
            x = self.x + len(self.text) * 20 + math.cos(p['angle']) * p['radius']
            y = self.y + math.sin(p['angle']) * p['radius']
            color = (255, 255, 200, int(p['alpha']))
            gfxdraw.filled_circle(surface, int(x), int(y), 2, color)
            
        # 绘制发光粒子
        for p in self.glow_particles:
            color = (255, 255, 255, p['alpha'])
            gfxdraw.filled_circle(surface, int(p['x']), int(p['y']), 
                                p['size'], color)
        
        # 绘制主文字
        text_surface = self.font.render(self.text, True, self.color)
        # 添加发光效果
        for offset in range(3, 0, -1):
            glow_surface = self.font.render(self.text, True, 
                                          (255, 255, 255, 100//offset))
            glow_rect = glow_surface.get_rect(center=(self.x + text_surface.get_width()/2, 
                                                     self.y))
            surface.blit(glow_surface, (glow_rect.x-offset, glow_rect.y))
            surface.blit(glow_surface, (glow_rect.x+offset, glow_rect.y))
        
        text_rect = text_surface.get_rect(center=(self.x + text_surface.get_width()/2, 
                                                 self.y))
        surface.blit(text_surface, text_rect)

# 修改主循环
def main():
    clock = pygame.time.Clock()
    tree = ChristmasTree()
    glowing_text = GlowingText()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 更新
        tree.update()
        glowing_text.update()
        
        # 绘制
        screen.fill(DARK_BLUE)
        tree.draw(screen)
        glowing_text.draw(screen)
        pygame.display.flip()
        
        clock.tick(60)
    
    pygame.quit()

# 注释掉视频生成相关代码
# def create_video():
#     ...

if __name__ == "__main__":
    main()
