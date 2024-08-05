import os
import pygame
import sys
import logging
from datetime import datetime
import random

# Путь к конфигурационному файлу
options_path = 'options.txt'

# Проверка существования конфигурационного файла и загрузка версии
if not os.path.exists(options_path):
    with open(options_path, 'w') as f:
        f.write('version=dev_01-notdemo')
    VERSION = 'dev_01-notdemo'
else:
    with open(options_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('version='):
                VERSION = line.strip().split('=')[1]

# Настройка логирования
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = f'log.{datetime.now().strftime("%d%m%y.%H%M")}.txt'
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s, "%(levelname)s"] %(message)s',
                    datefmt='%H:%M:%S',
                    handlers=[
                        logging.FileHandler(os.path.join(log_dir, log_filename)),
                        logging.StreamHandler(sys.stdout)
                    ])

# Инициализация Pygame
pygame.init()

# Путь к директории текстур
texture_dir = 'resources/textures'

# Настройка иконки
icon_path = os.path.join(texture_dir, 'icon.png')
try:
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
    logging.info(f'Loaded icon: {icon_path.replace("\\", "/")}')
except FileNotFoundError:
    logging.error(f'Icon not found: {icon_path.replace("\\", "/")}')
    sys.exit(1)

# Настройка экрана
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption(f'World Reborn - {VERSION}')

# Загрузка шрифта
font_path = 'resources/font/font1.ttf'
try:
    font = pygame.font.Font(font_path, 24)
    logging.info(f'Loaded font: {font_path.replace("\\", "/")}')
except FileNotFoundError:
    logging.error(f'Font not found: {font_path.replace("\\", "/")}')
    sys.exit(1)

# Функция для загрузки текстур
def load_textures(directory):
    textures = {}
    error_texture_path = os.path.join(directory, 'error_block.png')
    error_texture = pygame.image.load(error_texture_path).convert_alpha()
    textures['error_block'] = error_texture

    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            texture_id = filename[:-4]
            try:
                texture = pygame.image.load(os.path.join(directory, filename)).convert_alpha()
                textures[texture_id] = texture
                logging.info(f'Loaded texture: "{texture_id}" {os.path.join(directory, filename).replace("\\", "/")}')
            except pygame.error as e:
                logging.error(f'Failed to load texture: "{texture_id}" {os.path.join(directory, filename).replace("\\", "/")} - {e}')
                textures[texture_id] = error_texture
    return textures

# Загрузка текстур
textures = load_textures(texture_dir)

# Игровые параметры
TILE_SIZE = 40
PLAYER_WIDTH = 33  # Увеличен для большей визуальной ширины
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = 10
GRAVITY = 0.5

# Генерация мира
WORLD_LAYOUT = [
    "00000000000000000000",
    "11111111111111111111",
    "44444444444444444444",
    "22222222222222222222",
    "22222222222222222222",
    "22222222222222222222",
    "33333333333333333333"
]

# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(textures['player_right'], (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

    def update(self, keys, blocks):
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * PLAYER_SPEED
        if keys[pygame.K_a]:
            self.image = pygame.transform.scale(textures['player_left'], (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.facing_right = False
        elif keys[pygame.K_d]:
            self.image = pygame.transform.scale(textures['player_right'], (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.facing_right = True
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -JUMP_HEIGHT
        
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0
        
        self.rect.x += dx
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if dx > 0:
                    self.rect.right = block.rect.left
                elif dx < 0:
                    self.rect.left = block.rect.right

# Класс блока
class Block(pygame.sprite.Sprite):
    def __init__(self, texture_id, x, y):
        super().__init__()
        texture = textures.get(texture_id, textures['error_block'])
        self.image = pygame.transform.scale(texture, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Создание мира
def create_world(layout):
    blocks = pygame.sprite.Group()
    y_offset = 600 - len(layout) * TILE_SIZE
    for y, row in enumerate(layout):
        for x, tile in enumerate(row):
            if tile == '0':
                blocks.add(Block('grass_block', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == '1':
                blocks.add(Block('dirt', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == '2':
                blocks.add(Block('stone', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == '3':
                blocks.add(Block('bedrock', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == '4':
                block_type = 'stone' if random.choice([True, False]) else 'dirt'
                blocks.add(Block(block_type, x * TILE_SIZE, y * TILE_SIZE + y_offset))
    return blocks

# Создание игрока и мира
player = Player(100, 100)
blocks = create_world(WORLD_LAYOUT)
all_sprites = pygame.sprite.Group(player)
blocks.add(*blocks.sprites())

# Основной игровой цикл
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                # Ломание блока
                for block in blocks:
                    if player.rect.colliderect(block.rect):
                        blocks.remove(block)
                        break

    keys = pygame.key.get_pressed()
    player.update(keys, blocks)

    # Очистка экрана
    screen.fill((135, 206, 235))  # Цвет фона, например, голубое небо

    # Отображение блоков и игрока
    blocks.draw(screen)
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)  # Увеличение FPS до 60

pygame.quit()
