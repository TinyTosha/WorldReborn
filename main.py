import os
import pygame
import sys
import logging
from datetime import datetime
import random
import time

options_path = 'config/Game.cfg'
lang_dir = 'config/lang'
debug_mode = False
chat_open = False
version_fordebug = 'dev_07-demo'
default_version = 'dev_07-demo'
default_playername = 'Player'
default_lang = 'eng'
default_tick = 60
default_scene_name = 'Loading...'
default_secret= 'null'
default_render_mode = 'Legacy'

if not os.path.exists('config'):
    os.makedirs('config')
    if not os.path.exists('config/lang'):
        os.makedirs('config/lang')
if not os.path.exists('config/lang/eng.lang'):
    with open('config/lang/eng.lang', 'w') as f:
        f.write(f'menu.title=World: Reborn\nmenu.button.play=Play')
if not os.path.exists('config/.temp'):
    os.makedirs('config/.temp')
if not os.path.exists('config/Secret.cfg'):
    with open('config/Secret.cfg', 'w') as f:
        f.write(f'Data={default_secret}')
    SECRET = default_secret
else:
    with open('config/Secret.cfg', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('Data='):
                SECRET = line.strip().split('=')[1]
if not os.path.exists('config/Render.cfg'):
    with open('config/Render.cfg', 'w') as f:
        f.write(f'Data={default_render_mode}\n# ---=== Render Types: ===---\n#"Legacy" - Classic render, no camera, can use block\n#"BetaNew" - Render with camera, can`t use block')
    RENDER_MODE = default_render_mode
else:
    with open('config/Render.cfg', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('Data='):
                RENDER_MODE = line.strip().split('=')[1]

with open('config/.temp/scenename.cfg', 'w') as f:
    f.write(f'data={default_scene_name}')
SCENE_NAME = default_scene_name
with open('config/.temp/scenename.cfg', 'w') as f:
    f.write(f'data=Menu')
with open('config/.temp/scenename.cfg', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('data='):
                VERSION = line.strip().split('=')[1]
SCENE_NAME = 'Menu'
if RENDER_MODE == "Legacy":
    RENDER_MODE_VERSION = 'Alpha 0.1'
elif RENDER_MODE == "BetaNew":
    RENDER_MODE_VERSION = 'dev 0.1'
else:
    RENDER_MODE_VERSION = 'Unnamed'

if not os.path.exists(options_path):
    with open(options_path, 'w') as f:
        f.write(f'version={default_version}\nlang={default_lang}\ntick={default_tick}\nplayername={default_playername}')
    VERSION = default_version
    LANG = default_lang
    TICK_CFG = default_tick
    PLR_NAME = default_playername
else:
    with open(options_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('version='):
                VERSION = line.strip().split('=')[1]
            elif line.startswith('lang='):
                LANG = line.strip().split('=')[1]
            elif line.startswith('tick='):
                TICK_CFG = int(line.strip().split('=')[1])
            elif line.startswith('playername='):
                PLR_NAME = line.strip().split('=')[1]

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

pygame.init()
logging.info(f'World: Reborn - {version_fordebug} launched!')
logging.info(f'Loggined: {PLR_NAME}! Enjoy the game!')
logging.info('')
logging.info(f'Render Type loaded: "{RENDER_MODE}"')
if PLR_NAME == 'TinyTosha':
    logging.error("Don't lie!")
    quit()
texture_dir = 'resources/textures'
icon_path = os.path.join(texture_dir, 'icon.png')
try:
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
    icon_path = icon_path.replace("\\", "/")
    logging.info(f'Icon found: {icon_path}')
except FileNotFoundError:
    icon_path = icon_path.replace("\\", "/")
    logging.error(f'Icon not found: {icon_path}')
    sys.exit(1)
if RENDER_MODE == 'Legacy':
    screen = pygame.display.set_mode((800, 600))
if RENDER_MODE == 'BetaNew':
    screen = pygame.display.set_mode((1500, 600))
pygame.display.set_caption(f'World Reborn - {VERSION} - {SCENE_NAME}')

os.remove('config/.temp/scenename.cfg')

font_path = 'resources/font/font1.ttf'
try:
    font = pygame.font.Font(font_path, 24)
    font_path = font_path.replace("\\", "/")
    logging.info(f'Font found: {font_path}')
except FileNotFoundError:
    font_path = font_path.replace("\\", "/")
    logging.error(f'Font not found: {icon_path}')
    sys.exit(1)

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
                    path = os.path.join(root, filename).replace("\\", "/")
                    logging.info(f'Loaded texture: "{texture_id}" {path}')
                except pygame.error as e:
                    lpath = os.path.join(root, filename).replace("\\", "/")
                    logging.info(f'Loaded error texture: "{texture_id}" {path}')
                    textures[texture_id] = error_texture
    return textures

textures = load_textures(texture_dir)

def load_language(lang_code):
    lang_path = os.path.join(lang_dir, f'{lang_code}.lang')
    lang_data = {}
    try:
        with open(lang_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    lang_data[key] = value
        logging.info(f'Loaded language: {lang_code}')
    except FileNotFoundError:
        if lang_code != default_lang:
            logging.error(f'Language file not found: {lang_path}. Falling back to default language.')
            return load_language(default_lang)
        else:
            logging.critical(f'Default language file not found: {lang_path}.')
            show_error_message()
            sys.exit(1)
    return lang_data

def show_error_message():
    error_font = pygame.font.Font(font_path, 30)
    error_text = error_font.render("Install eng.lang please:", True, (255, 0, 0))
    error_text2 = error_font.render("github.com/TinyTosha/WorldReborn", True, (255, 0, 0))
    while True:
        screen.fill((0, 0, 0))
        screen.blit(error_text, (100, 250))
        screen.blit(error_text2, (100, 300))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

lang_data = load_language(LANG)

def handle_chat_input(event, chat_active, chat_text):
    if event.type == pygame.KEYDOWN:
        if chat_active:
            if event.key == pygame.K_RETURN:  # Enter key
                if chat_text.startswith("/"):
                    process_command(chat_text)
                else:
                    logging.info(f'<{PLR_NAME}> {chat_text}')
                chat_text = ""
                chat_active = False
            elif event.key == pygame.K_BACKSPACE:
                chat_text = chat_text[:-1]
            else:
                chat_text += event.unicode
        elif event.key == pygame.K_t:  # Open chat
            chat_active = True
    return chat_active, chat_text

TILE_SIZE = 40
PLAYER_SIZE = 30
PLAYER_SPEED = 5
JUMP_HEIGHT = 10
GRAVITY = 0.5
REACH_DISTANCE = TILE_SIZE * 3

# World Generators Secret
if SECRET == 'SkyBlock':
    WORLD_LAYOUT = [
        "  000               ",
        "   1                ",
        "                    ",
        "                    ",
        "                    ",
        "                    ",
        "                    "
    ]
    logging.info('World by coconut31')
elif SECRET == 'BigTest':
    WORLD_LAYOUT = [
        
        "                                                                                    000000000",
        "                                                                                   01422222410",
        "                                                                                  0142222222410",
        "                                                                                 014222222222410",
        "                                                                                01422222222222410",
        "                                                                               0142222222222222410",
        "                l                                                             014222222222222222410",
        " pppppppp      lll                                                           01422222222222222222410",
        " gwwwwwwp                                                                   0142222222222222222222410",
        " pwwwwwww       t                                                          014222222222222222222222410",
        "0[[[[[[[[0000000000    000000000000000000000000000000000000000000000000000011422222222222222222222241100000000000000000000",
        "111111111111111111111        111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
        "44444444444444444444444       44444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444",
        "22252222222222222222222222      222266622222222222222222222222222222222222222222222222222222222222222222222222222222222222",
        "25555222222222622222222222222222266666622222222222222222222222222222222222222222222222222222222222222222222222222222222222",
        "22222225522222262262222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222",
        "333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333"
    ]
    if not RENDER_MODE  == 'BetaNew':
        logging.error(f'For "{SECRET}" need to activate the render mode "BetaNew" in the "BetaFeatures.cfg"')
    SPAWN_TREE = random.randint(1, 1)
    SPAWN_HOUSE = random.randint(1, 1)      
else:
    WORLD_LAYOUT = [
        "                l   ",
        " pppppppp      lll  ",
        " g      p       t   ",
        " p              t   ",
        "0[[[[[[[[00000000000",
        "11111111111111111111",
        "44444444444444444444",
        "22252222222222222222",
        "25555222222222622222",
        "22222225522222262262",
        "33333333333333333333"
    ]
    SPAWN_TREE = random.randint(0, 1)
    SPAWN_HOUSE = random.randint(0, 10)



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

class Block(pygame.sprite.Sprite):
    def __init__(self, texture_id, x, y):
        super().__init__()
        texture = textures.get(texture_id, textures['error_block'])
        self.image = pygame.transform.scale(texture, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

def create_world(layout):
    logging.info('Creating new world... %10')
    if SPAWN_TREE == 1:
        logging.info('Structure created: "structures/tree/" resources/textures/structures/tree/')
    if SPAWN_HOUSE == 1:
        logging.info('Structure created: "structures/house/" resources/textures/structures/house/')
    logging.info('Creating new world... %50')
    blocks = pygame.sprite.Group()
    y_offset = 600 - len(layout) * TILE_SIZE
    if RENDER_MODE == 'BetaNew':
        logging.warn(f'You use the Render Type: {RENDER_MODE}. Block placement and breaking disible!')
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
            elif tile == '5':
                block_type = 'stone' if random.choice([True, False]) else 'ores/coal'
                blocks.add(Block(block_type, x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == '6':
                block_type = 'stone' if random.choice([True, False]) else 'ores/iron'
                blocks.add(Block(block_type, x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == 't':
                if SPAWN_TREE == 1:
                    blocks.add(Block('structures/tree/log', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == 'l':
                if SPAWN_TREE == 1:
                    blocks.add(Block('structures/tree/leaves', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == '[':
                if SPAWN_HOUSE == 1:
                    blocks.add(Block('structures/house/planks', x * TILE_SIZE, y * TILE_SIZE + y_offset))
                else:
                    blocks.add(Block('grass_block', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == 'p':
                if SPAWN_HOUSE == 1:
                    blocks.add(Block('structures/house/planks', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == 'g':
                if SPAWN_HOUSE == 1:
                    blocks.add(Block('structures/house/glass', x * TILE_SIZE, y * TILE_SIZE + y_offset))
            elif tile == 'w':
                if SPAWN_HOUSE ==1:
                    blocks.add(Block('structures/house/wall', x * TILE_SIZE, y * TILE_SIZE + y_offset))
    logging.info('Creating new world... %100')
    return blocks

def main_menu():
    title_text = font.render(lang_data.get('menu.title', 'World: Reborn'), True, (255, 255, 255))
    play_text = font.render(lang_data.get('menu.button.play', 'Play'), True, (255, 255, 255))

    title_rect = title_text.get_rect(center=(400, 200))
    play_rect = play_text.get_rect(center=(400, 300))

    while True:
        screen.fill((0, 0, 0))
        screen.blit(title_text, title_rect)
        screen.blit(play_text, play_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    with open('config/.temp/scenename.cfg', 'w') as f:
                        f.write(f'data=World')
                    return
                
                    

def show_pause_screen():
    pause_text = font.render("Paused", True, (255, 255, 255))
    pause_rect = pause_text.get_rect(center=(400, 300))
    screen.blit(pause_text, pause_rect)
    pygame.display.flip()

def create_hotbar():
    hotbar = []
    random_number = random.randint(0, 9)
    slot_texture_path = os.path.join(texture_dir, 'ui', 'slot.png')
    slot_texture = pygame.image.load(slot_texture_path).convert_alpha()
    slot_texture = pygame.transform.scale(slot_texture, (TILE_SIZE * 2, TILE_SIZE))
    for i in range(10):
        slot = slot_texture.copy()
        hotbar.append(slot)
    return hotbar

def draw_hotbar(hotbar, selected_slot):
    for i, slot in enumerate(hotbar):
        x = 10 + i * (TILE_SIZE * 2 + 10)
        y = 10
        if i == selected_slot:
            slot = pygame.transform.scale(slot, (TILE_SIZE * 2 + 10, TILE_SIZE + 10))
            x -= 5
            y -= 5
        screen.blit(slot, (x, y))

def in_reach(player, block):
    player_x, player_y = player.rect.center
    block_x, block_y = block.rect.center
    distance = ((player_x - block_x) ** 2 + (player_y - block_y) ** 2) ** 0.5
    return distance <= REACH_DISTANCE

def draw_debug_info(player):
    debug_font = pygame.font.Font(font_path, 20)
    
    version_text = debug_font.render(f'World: Reborn - {version_fordebug}', True, (255, 0, 0))
    ticks_text = debug_font.render(f'Ticks: {TICK_CFG}', True, (255, 0, 0))
    coords_text = debug_font.render(f'X, Y: ({int(player.rect.x)}, {int(player.rect.y)})', True, (255, 0, 0))
    secretcode_text = debug_font.render(f'Secret: {SECRET}', True, (255, 0, 0))
    RENDER_MODE_text = debug_font.render(f'RenderType: {RENDER_MODE} - {RENDER_MODE_VERSION}', True, (255, 0, 0))

    screen.blit(version_text, (10, 10))
    screen.blit(ticks_text, (10, 130))
    screen.blit(coords_text, (10, 70))
    screen.blit(secretcode_text, (10, 100))
    screen.blit(RENDER_MODE_text, (10, 40))

def process_command(command):
    if command == "/world_layout":
        logging.info(f'World Layout: {WORLD_LAYOUT}')
    else:
        logging.info(f'Unknown command: {command}')


def draw_chat_input(chat_text):
    chat_font = pygame.font.Font(font_path, 20)
    chat_surface = chat_font.render(chat_text, True, (255, 255, 255))
    screen.blit(chat_surface, (10, 550))


def game_loop():
    global blocks, debug_mode
    player = Player(100, 100)
    blocks = create_world(WORLD_LAYOUT)
    all_sprites = pygame.sprite.Group(player)
    blocks.add(*blocks.sprites())

    hotbar = create_hotbar()
    selected_slot = 0
    inventory = {}

    camera_offset_x = 0
    camera_offset_y = 0

    last_generation_time = pygame.time.get_ticks()
    paused = False

    chat_active = False
    chat_text = ""

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if chat_active:
                    chat_active, chat_text = handle_chat_input(event, chat_active, chat_text)
                else:
                    if event.key == pygame.K_f:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        block_x = (mouse_x // TILE_SIZE) * TILE_SIZE
                        block_y = (mouse_y // TILE_SIZE) * TILE_SIZE
                        for block in blocks:
                            if block.rect.topleft == (block_x, block_y) and in_reach(player, block):
                              blocks.remove(block)
                            block_type = block.image.get_at((0, 0))
                            block_type = block_type[:3]
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
                    elif event.key == pygame.K_F3:
                        debug_mode = not debug_mode
                    elif event.key in range(pygame.K_1, pygame.K_0 + 1):
                        selected_slot = (event.key - pygame.K_1) % 10
                    elif event.key == pygame.K_t:
                        chat_active = True
            elif event.type == pygame.MOUSEBUTTONDOWN and not chat_active:
                if event.button == 4:
                    selected_slot = (selected_slot - 1) % 10
                elif event.button == 5:
                    selected_slot = (selected_slot + 1) % 10
                elif event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    block_x = (mouse_x // TILE_SIZE) * TILE_SIZE
                    block_y = (mouse_y // TILE_SIZE) * TILE_SIZE
                    for block in blocks:
                        if block.rect.topleft == (block_x, block_y) and in_reach(player, block):
                            blocks.remove(block)
                            block_type = block.image.get_at((0, 0))
                            block_type = block_type[:3]
                            block_type = next((k for k, v in textures.items() if v.get_at((0, 0)) == block_type), 'error_block')
                            if block_type not in inventory:
                                inventory[block_type] = 0
                            inventory[block_type] += 1
                            break
                elif event.button == 3:
                    x, y = pygame.mouse.get_pos()
                    block_x = x // TILE_SIZE * TILE_SIZE
                    block_y = y // TILE_SIZE * TILE_SIZE
                    if not any(block.rect.collidepoint(x, y) for block in blocks):
                        block_type = 'grass_block'
                        if block_type in inventory and inventory[block_type] > 0:
                            new_block = Block(block_type, block_x, block_y)
                            blocks.add(new_block)
                            inventory[block_type] -= 1

                elif event.key == pygame.K_ESCAPE:
                    if not paused:
                        show_pause_screen()
                        paused = True
                    else:
                        paused = False
                elif event.key == pygame.K_F3:
                    debug_mode = not debug_mode  # Переключаем режим отладки
                elif event.key in range(pygame.K_1, pygame.K_0 + 1):
                    selected_slot = (event.key - pygame.K_1) % 10
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    selected_slot = (selected_slot - 1) % 10
                elif event.button == 5:
                    selected_slot = (selected_slot + 1) % 10
                elif event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    block_x = (mouse_x // TILE_SIZE) * TILE_SIZE
                    block_y = (mouse_y // TILE_SIZE) * TILE_SIZE
                    for block in blocks:
                        if block.rect.topleft == (block_x, block_y) and in_reach(player, block):
                            blocks.remove(block)
                            block_type = block.image.get_at((0, 0))
                            block_type = block_type[:3]
                            block_type = next((k for k, v in textures.items() if v.get_at((0, 0)) == block_type), 'error_block')
                            if block_type not in inventory:
                                inventory[block_type] = 0
                            inventory[block_type] += 1
                            break
                elif event.button == 3:
                    x, y = pygame.mouse.get_pos()
                    block_x = x // TILE_SIZE * TILE_SIZE
                    block_y = y // TILE_SIZE * TILE_SIZE
                    if not any(block.rect.collidepoint(x, y) for block in blocks):
                        block_type = 'grass_block'
                        if block_type in inventory and inventory[block_type] > 0:
                            new_block = Block(block_type, block_x, block_y)
                            blocks.add(new_block)
                            inventory[block_type] -= 1

        if not paused:
            current_time = pygame.time.get_ticks()
            if current_time - last_generation_time > 5 * 60 * 1000:
                blocks.empty()
                blocks = create_world(WORLD_LAYOUT)
                last_generation_time = current_time

            keys = pygame.key.get_pressed()
            player.update(keys, blocks, paused)

            screen.fill((135, 206, 235))

            camera_offset_x = player.rect.centerx - 800 // 2
            camera_offset_y = player.rect.centery - 600 // 2

            if RENDER_MODE == 'BetaNew':

                player_draw_rect = player.rect.move(-camera_offset_x, -camera_offset_y)
                screen.blit(player.image, player_draw_rect)
                for block in blocks:
                    block_draw_rect = block.rect.move(-camera_offset_x, -camera_offset_y)
                    screen.blit(block.image, block_draw_rect)
            elif RENDER_MODE == 'Legacy':
                
                blocks.update()

                blocks.draw(screen)
                all_sprites.draw(screen)

            draw_hotbar(hotbar, selected_slot)

            if debug_mode:
                draw_debug_info(player)

            

            if chat_active:
                draw_chat_input(chat_text)

            pygame.display.flip()
            clock.tick(TICK_CFG)


if __name__ == "__main__":
    while True:
        main_menu()
        game_loop()