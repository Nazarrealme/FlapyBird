from pygame import *
from random import randint
import sounddevice as sd
import numpy as np
import json

#!! Звуки
#!!!! НЕ працює переход в меню після програшу!!!!!!!

with open("settings.json", "r", encoding="utf-8") as file:
    settings = json.load(file)

bird_skins = [
    "bird_.png",
    "bird.png"
]

backgrounds = [
    "back.jpg",
    "back2.jpg"
]

DIFF = {
    "easy": {
        "tube_speed": 3,
        "gap": 280,
        "gravity": 0.3,
        "impulse": -6.5
    },
    "normal": {
        "tube_speed": 5,
        "gap": 240,
        "gravity": 0.4,
        "impulse": -7.0
    },
    "hard": {
        "tube_speed": 8,
        "gap": 200,
        "gravity": 0.5,
        "impulse": -7.5
        
    }
}

diff_name = settings["difficulty"]
if diff_name not in DIFF:
    diff_name = "normal"

diff = DIFF[diff_name]
TUBE_SPEED = diff["tube_speed"]
GRAVITY = diff["gravity"]
JUMP_IMPULSE =  diff["impulse"]
GAP = diff["gap"]

skin_index = 0
background_index = 0

if settings["bird_skin"] in bird_skins:
    skin_index = bird_skins.index(settings["bird_skin"])

if settings["background"] in backgrounds:
    background_index = backgrounds.index(settings["background"])


def change_bird_skin():
    global bird
    skin_name = bird_skins[skin_index]
    bird = image.load(skin_name)
    bird = transform.scale(bird, (100, 100))

def change_background():
    global background
    background_name = backgrounds[background_index]
    background = image.load(background_name)
    background = transform.scale(background, window_size)

def save_settings():
    settings["bird_skin"] = bird_skins[skin_index]
    settings["background"] = backgrounds[background_index]

    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def apply_diff():
    global TUBE_SPEED, GRAVITY, JUMP_IMPULSE, GAP
    global gravity, IMPULSE
    diff = DIFF[diff_name]
    TUBE_SPEED = diff["tube_speed"]
    GRAVITY = diff["gravity"]
    JUMP_IMPULSE =  diff["impulse"]
    GAP = diff["gap"]
    gravity = GRAVITY
    IMPULSE = JUMP_IMPULSE

init()
window_size = (settings["window_width"], settings["window_height"])
window = display.set_mode(window_size)
display.set_caption("Flappy Bird")

clock = time.Clock()
FPS = settings["fps"]
#!!!                x    y    w    h
player_rect = Rect(150, 200, 100, 100)

background = image.load(settings["background"])
background = transform.scale(background, window_size)

bird = image.load(settings["bird_skin"])
bird = transform.scale(bird, (100, 100))

tube_top_image = image.load("tube_top.png")
tube_bottom_image = image.load("tube_bottom.png")

sr = 16000
block = 256
mic_level = 0.0

def audio_cb(indata, frames, time, status):
    global mic_level
    if status:
        return
    rms = float(np.sqrt(np.mean(indata ** 2)))
    mic_level = 0.85 * mic_level + 0.15 * rms

THRESH = 0.001
voice_cooldown = 0

def generate_tubes(count, 
                   tube_width = 140, 
                   gap = None, 
                   min_height = 50,
                   max_height = 320,
                   distance = 650):
    if gap is None:
        gap = GAP
    tubes = []
    start_x = window_size[0]
    for i in range(count):
        height = randint(min_height, max_height) # 120, 250
        top_tube = Rect(start_x, 0, tube_width, height)
        bottom_tube = Rect(start_x, 
                           height + gap, 
                           tube_width, 
                           window_size[1] - height - gap)
        tubes.extend([top_tube, bottom_tube])
        start_x += distance

    return tubes
    
game_state = "menu"

tubes = generate_tubes(150)

gravity = GRAVITY #!!!!!!!!!!!!!!!!
y_vel = 0.0 #!!!!!!!!!!!!!!!!
IMPULSE = JUMP_IMPULSE #!!!!!!!!!!!!!!!!

lose = False
score = 0
my_font = font.Font(None, 50)



with sd.InputStream(
    samplerate=sr,
    channels=1,
    blocksize=block,
    callback=audio_cb
):

    while 1:
        for e in event.get():
            if e.type == QUIT:
                quit()
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1 and game_state == "ready":
                    game_state = "playing"
            if e.type == KEYDOWN and game_state == "menu":
                if e.key == K_RETURN :
                    game_state = "ready"
                elif e.key == K_LEFT:
                    skin_index = (skin_index - 1) % len(bird_skins)
                    change_bird_skin()
                    save_settings()
                elif e.key == K_RIGHT:
                    skin_index = (skin_index + 1) % len(bird_skins)
                    change_bird_skin()
                    save_settings()
                elif e.key == K_a:
                    background_index = (background_index - 1) % len(backgrounds)
                    change_background()
                    save_settings()
                elif e.key == K_d:
                    background_index = (background_index + 1) % len(backgrounds)
                    change_background()
                    save_settings()
                elif e.key == K_1:
                    diff_name = "easy"
                    apply_diff()
                    settings["difficulty"] = diff_name
                    save_settings()
                elif e.key == K_2:
                    diff_name = "normal"
                    apply_diff()
                    settings["difficulty"] = diff_name
                    save_settings()
                elif e.key == K_3:
                    diff_name = "hard"
                    apply_diff()
                    settings["difficulty"] = diff_name
                    save_settings()


            if e.type == KEYDOWN:
                if e.key == K_m and game_state == "game_over":
                    game_state = "menu"
                    player_rect.x = 150
                    player_rect.y = 200

                    y_vel = 0
                    score = 0
                    tubes = generate_tubes(150)
                    voice_cooldown = 0


        if voice_cooldown > 0:
            voice_cooldown -= 1

        if mic_level > THRESH and game_state == "playing" and voice_cooldown == 0:
            y_vel = IMPULSE
            voice_cooldown = 7

        if game_state == "playing":
            y_vel += gravity 
            player_rect.y += int(y_vel)

        keys = key.get_pressed()
        if keys[K_UP] or keys[K_w]: 
            if not lose:
                y_vel = IMPULSE 

        if keys[K_r] and game_state == "game_over":
            game_state = "ready"
            score = 0
            tubes = generate_tubes(150)
            player_rect.x = 150
            player_rect.y = 200
            y_vel = 0
            voice_cooldown = 0

        # if keys[K_ESCAPE] and game_state == "game_over":
        #     game_state = "menu"
        #if keys[K_DOWN] or keys[K_s]: y_vel = 5
        if game_state == "playing":
            if player_rect.bottom >= window_size[1]:
                player_rect.bottom = window_size[1]
                game_state = "game_over"
                y_vel = 0 #!!!!!

            if player_rect.top <= 0:
                player_rect.top = 0
                game_state = "game_over"
                y_vel = 0 #!!!!!
        
        #window.fill("sky blue")
        window.blit(background, (0, 0))
        for tube in tubes[:]: 
            if game_state == "playing": #!!!!!!
                tube.x -= TUBE_SPEED #!!!!!!
            if tube.right < 0:
                tubes.remove(tube)
                score += 0.5
                continue
            #draw.rect(window, (0, 255, 0), tube)
            if tube.y == 0:
                pipe_image = tube_top_image
            else:
                pipe_image = tube_bottom_image
            pipe = transform.scale(pipe_image, (tube.width, tube.height))
            window.blit(pipe, tube)
            if player_rect.colliderect(tube) and game_state == "playing": #!!!!!!!
                game_state = "game_over"
                y_vel = 0 #!!!!!!!

        if game_state == "playing" and len(tubes) < 8:
            tubes += generate_tubes(150)
        
        #draw.rect(window, (0, 255, 0), player_rect)
        window.blit(bird, player_rect)
        if game_state == "ready":
            start_text = my_font.render("CLICK TO START", True, "black")
            window.blit(start_text, (250, 250))
        score_text = my_font.render(f"Score: {int(score)}", True, "black")
        #!!!!                     x   y
        window.blit(score_text, (20, 20))


        if game_state == "menu":
            overlay = Surface(window_size, SRCALPHA)
            overlay.fill((0,0,0,160))
            window.blit(overlay, (0, 0))
            title_font = font.Font(None, 100)
            title_text = title_font.render("FLAPPY BIRD", True, "white")
            window.blit(title_text, (190, 150))
            skin_text = my_font.render("LEFT/RIGHT - SKIN", True, "white")
            background_text = my_font.render("A / D - BACKGROUND", True, "white")

            window.blit(skin_text, (220, 390))
            window.blit(background_text, (220, 440))
            diff_text = my_font.render(f"DIFFICULTY - {diff_name.upper()}", True, "white")
            window.blit(diff_text, (250, 490))
            controls_text = my_font.render("1 - EASY, 2 - NORMAL, 3 - HARD", True, "white")
            window.blit(controls_text, (130, 540))
            menu_text = my_font.render("PRESS ENTER", True, "white")
            window.blit(menu_text, (280, 330))
        if game_state == "game_over":
            lose_text = my_font.render("GAME OVER!", True, "red")
            window.blit(lose_text, (280, 250))

            #!! Додати повідомлення - PRESS R TO RESTART
            #!! Додати повідомлення - PRESS M TO MENU
            restart_button = my_font.render("PRESS R TO RESTART!", True, "red")
            window.blit(restart_button, (280, 300))
            menu_button = my_font.render("PRESS M TO GO MENU!", True, "red")
            window.blit(menu_button, (280, 350))
        display.update()
        clock.tick(FPS)