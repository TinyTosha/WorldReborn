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
        f.write('version=dev_02-notdemo')
    VERSION = 'dev_02-notdemo'
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

# Функция для загрузки текстур из директории и подкаталогов
def load_textures(directory):
    textures = {}
    error_texture_path = os.path.join(directory, 'error_block.png')
    error_texture = pygame.image.load(error_texture_path).convert_alpha()
    textures['error_block'] = error_texture

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.png'):
                texture_id = os.path.relpath(os.path.join(root, filename), directory)[:-4].replace('\\', '/')
                try:
                    texture = pygame.image.load(os.path.join(root, filename)).convert_alpha()
                    textures[texture_id] = texture
                    logging.info(f'Loaded texture: "{texture_id}" {os.path.join(root, filename).replace("\\", "/")}')
                except pygame.error as e:
                    logging.error(f'Failed to load texture: "{texture_id}" {os.path.join(root, filename).replace("\\", "/")} - {e}')
                    textures[texture_id] = error_texture
    return textures

# Загрузка текстур
textures = load_textures(texture_dir)

# Игровые параметры
TILE_SIZE = 40
PLAYER_SIZE = 30  # Размер игрока чуть меньше, чем размер блока
PLAYER_SPEED = 5
JUMP_HEIGHT = 10
GRAVITY = 0.5
REACH_DISTANCE = TILE_SIZE * 3

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
        self.image = pygame.transform.scale(textures['player_right'], (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

    def update(self, keys, blocks, paused):
        if paused:
            return

        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * PLAYER_SPEED
        if keys[pygame.K_a]:
            self.image = pygame.transform.scale(textures['player_left'], (PLAYER_SIZE, PLAYER_SIZE))
            self.facing_right = False
        elif keys[pygame.K_d]:
            self.image = pygame.transform.scale(textures['player_right'], (PLAYER_SIZE, PLAYER_SIZE))
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

    def update(self):
        pass

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

# Класс кнопки
class Button(pygame.sprite.Sprite):
    def __init__(self, text, x, y):
        super().__init__()
        self.font = pygame.font.Font(font_path, 30)
        self.text = text
        self.image = self.font.render(text, True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Функция для отображения главного меню
def main_menu():
    menu_running = True
    background_color = (50, 50, 50)  # Цвет фона меню
    menu_buttons = pygame.sprite.Group()

    title_font = pygame.font.Font(font_path, 60)
    title_text = title_font.render("World: Reborn", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(400, 100))

    play_button = Button("Play", 350, 300)
    menu_buttons.add(play_button)

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_clicked(event.pos):
                    menu_running = False

        screen.fill(background_color)
        screen.blit(title_text, title_rect)
        menu_buttons.draw(screen)
        pygame.display.flip()

# Функция для отображения экрана паузы
def show_pause_screen():
    pause_font = pygame.font.Font(font_path, 50)
    pause_text = pause_font.render("Pause", True, (255, 255, 255))
    pause_rect = pause_text.get_rect(center=(400, 300))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Возвращаемся к игре

        screen.fill((0, 0, 0))  # Черный фон для экрана паузы
        screen.blit(pause_text, pause_rect)
        pygame.display.flip()

# Функция для создания хотбара
def create_hotbar():
    hotbar = []
    slot_texture_path = os.path.join(texture_dir, 'ui', 'slot.png')
    slot_texture = pygame.image.load(slot_texture_path).convert_alpha()
    slot_texture = pygame.transform.scale(slot_texture, (TILE_SIZE * 2, TILE_SIZE))
    for i in range(10):
        slot = slot_texture.copy()
        hotbar.append(slot)
    return hotbar

# Функция для отображения хотбара
def draw_hotbar(hotbar, selected_slot):
    for i, slot in enumerate(hotbar):
        x = 10 + i * (TILE_SIZE * 2 + 10)
        y = 10
        if i == selected_slot:
            slot = pygame.transform.scale(slot, (TILE_SIZE * 2 + 10, TILE_SIZE + 10))
            x -= 5
            y -= 5
        screen.blit(slot, (x, y))

# Функция проверки, находится ли игрок в пределах досягаемости блока
def in_reach(player, block):
    player_x, player_y = player.rect.center
    block_x, block_y = block.rect.center
    distance = ((player_x - block_x) ** 2 + (player_y - block_y) ** 2) ** 0.5
    return distance <= REACH_DISTANCE

# Основной игровой цикл
def game_loop():
    global blocks
    player = Player(100, 100)
    blocks = create_world(WORLD_LAYOUT)
    all_sprites = pygame.sprite.Group(player)
    blocks.add(*blocks.sprites())

    hotbar = create_hotbar()
    selected_slot = 0
    inventory = {}

    last_generation_time = pygame.time.get_ticks()
    paused = False

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # Ломание блока
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    block_x = (mouse_x // TILE_SIZE) * TILE_SIZE
                    block_y = (mouse_y // TILE_SIZE) * TILE_SIZE
                    for block in blocks:
                        if block.rect.topleft == (block_x, block_y) and in_reach(player, block):
                            blocks.remove(block)
                            block_type = block.image.get_at((0, 0))  # Получаем цвет пикселя как идентификатор блока
                            block_type = block_type[:3]  # Получаем только RGB
                            block_type = next((k for k, v in textures.items() if v.get_at((0, 0)) == block_type), 'error_block')
                            if block_type not in inventory:
                                inventory[block_type] = 0
                            inventory[block_type] += 1
                            break
                elif event.key == pygame.K_ESCAPE:
                    if not paused:
                        show_pause_screen()
                        paused = True
                    else:
                        paused = False
                elif event.key in range(pygame.K_1, pygame.K_0 + 1):
                    selected_slot = (event.key - pygame.K_1) % 10
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Прокрутка вверх
                    selected_slot = (selected_slot - 1) % 10
                elif event.button == 5:  # Прокрутка вниз
                    selected_slot = (selected_slot + 1) % 10
                elif event.button == 3:  # Правая кнопка мыши
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    block_x = (mouse_x // TILE_SIZE) * TILE_SIZE
                    block_y = (mouse_y // TILE_SIZE) * TILE_SIZE
                    for block in blocks:
                        if block.rect.topleft == (block_x, block_y) and in_reach(player, block):
                            blocks.remove(block)
                            block_type = block.image.get_at((0, 0))  # Получаем цвет пикселя как идентификатор блока
                            block_type = block_type[:3]  # Получаем только RGB
                            block_type = next((k for k, v in textures.items() if v.get_at((0, 0)) == block_type), 'error_block')
                            if block_type not in inventory:
                                inventory[block_type] = 0
                            inventory[block_type] += 1
                            break
                elif event.button == 1:  # Левая кнопка мыши
                    x, y = pygame.mouse.get_pos()
                    block_x = x // TILE_SIZE * TILE_SIZE
                    block_y = y // TILE_SIZE * TILE_SIZE
                    if not any(block.rect.collidepoint(x, y) for block in blocks):
                        block_type = 'grass_block'  # Пример блока, который ставится
                        if block_type in inventory and inventory[block_type] > 0:
                            new_block = Block(block_type, block_x, block_y)
                            blocks.add(new_block)
                            inventory[block_type] -= 1

        if not paused:
            current_time = pygame.time.get_ticks()
            if current_time - last_generation_time > 5 * 60 * 1000:  # 5 минут
                blocks.empty()
                blocks = create_world(WORLD_LAYOUT)
                last_generation_time = current_time

            keys = pygame.key.get_pressed()
            player.update(keys, blocks, paused)

            # Очистка экрана
            screen.fill((135, 206, 235))  # Цвет фона, например, голубое небо

            # Обновление блоков
            blocks.update()

            # Отображение блоков и игрока
            blocks.draw(screen)
            all_sprites.draw(screen)

            # Отображение хотбара
            draw_hotbar(hotbar, selected_slot)

            pygame.display.flip()
            clock.tick(60)  # Увеличение FPS до 60

# Запуск программы
if __name__ == "__main__":
    while True:
        main_menu()
        game_loop()
