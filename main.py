import pygame
import sys
import random
import time
import csv
import math

pygame.init()

# properties
WIDTH, HEIGHT = 600, 600
FPS = 60

# colors
WHITE = (255, 255, 255)
GRAY = (122, 122, 122)
BLACK = (0, 0, 0)
YELLOW = (230, 213, 30)
GREEN = (39, 194, 0)
RED = (255, 77, 0)
ORANGE = (232, 166, 0)

# screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lemon Slicer")


# load assets
cut = pygame.mixer.Sound("assets/cut.wav")
cut1 = pygame.mixer.Sound("assets/cut1.wav")
cut2 = pygame.mixer.Sound("assets/cut2.wav")
cut3 = pygame.mixer.Sound("assets/cut3.wav")
cutmega = pygame.mixer.Sound("assets/cutmega.wav")
cuthoney = pygame.mixer.Sound("assets/honey.mp3")
death = pygame.mixer.Sound("assets/death.wav")
explosion = pygame.mixer.Sound("assets/explosion.mp3")
woosh = pygame.mixer.Sound("assets/woosh.wav")
pygame.mixer.music.load('assets/lemonjuice.ogg')
pygame.mixer.music.set_volume(0.88)
pygame.mixer.music.play(-1)


bomb_expanded_image = pygame.image.load("assets/bombexpanded.png")
background = pygame.image.load("assets/background.png")
shadow = pygame.image.load("assets/shadow.png")
pause_image = pygame.image.load("assets/pause.png")
tutorial_image = pygame.image.load("assets/tutorial.png")
player_image = pygame.image.load("assets/player.png")
normal_player_image = pygame.image.load("assets/player.png")
honey_player_image = pygame.image.load("assets/honeyplayer.png")
lemon_image = pygame.image.load("assets/lemon.png")
pygame.display.set_icon(lemon_image)
mega_lemon_image = pygame.image.load("assets/megalemon.png")
honey_lemon_image = pygame.image.load("assets/honeylemon.png")
rock_image = pygame.image.load("assets/rock.png")
bomb_image = pygame.image.load("assets/bomb.png")
start_image = pygame.image.load("assets/start.png")
start_key = pygame.image.load("assets/startkey.png")
player_rect = player_image.get_rect()
player_speed = 5
dash_speed = 15 # pixels to travel per frame
dash_rotation_speed = -30  # rotation speed during dash
normal_rotation_speed = -5  # rotation speed when not dashing
dash_duration = 12  # number of frames the dash will last
dash_cooldown = 35  # number of frames to wait before dashing again
dash_timer = 0
cooldown_timer = 0
is_dashing = False
last_score = 0
score_count = 0
explode_radius = 100

# lemon and rock settings
honey_covered = False
lemon_speed = 4
rock_speed = 6
speed_multiplier = 0.75
lemon_chance = 5
mega_lemon_chance = 2
honey_lemon_chance = 2
rock_chance = 1
lemons = []
rocks = []
bombs = []
mega_lemons = []
honey_lemons = []
background_speed = 2  # Adjust the speed of the scrolling background
background_pos1 = 0
background_pos2 = -background.get_height()
honey_duration = 0
bomb_timer = 0


# initialize variables
lemon_count = 0
rock_count = 0
bomb_count = 0
mega_lemon_count = 0
honey_lemon_count = 0

score = 0
luck = 0

player_rect.center = (WIDTH // 2, HEIGHT // 2)
rotation_angle = 0
background_rotation_angle = 0

title_rect = start_image.get_rect()
initial_title_y = 280
title_rect.y = initial_title_y

game_state = "start"

font_file = "assets/BaiJamjuree-Bold.ttf"
font = pygame.font.Font(font_file, 36)
shadow_show = True
clock = pygame.time.Clock()

def endgame():
    game_state = "end"
    player_rect.center = (WIDTH // 2, HEIGHT // 2)
    lemons = []
    mega_lemons = []
    honey_lemons = []
    bombs = []
    rocks = []
    score = 0
    speed_multiplier = 0.75
    honey_duration = 0
    honey_covered = False
    player_image = normal_player_image
    bomb_chance = 1
    player_speed = 5
    dash_speed = 15
    dash_cooldown = 35
    luck = 100 - ((rock_count * 2 / (lemon_count * 1.3 + mega_lemon_count * 10)) * 100)
    shadow_show = True

# particle system
class Particle:
    def __init__(self, x, y, color, radius):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.speed = random.uniform(2, 5)
        self.angle = math.radians(random.uniform(0, 360))

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.speed -= 0.1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

particles = []

def create_particles(x, y, color, radius, count=10):
    for _ in range(count):
        particles.append(Particle(x, y, color, radius))


# read from csv
def read_high_score():
    try:
        with open('highscore.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                return int(row[0])
    except FileNotFoundError:
        return 0

# write to csv
def write_high_score(high_score):
    with open('highscore.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([str(high_score)])

high_score = read_high_score()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            write_high_score(high_score)
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == 'tutorial':
                game_state = "playing"
            if event.key == pygame.K_RETURN and game_state == 'start':
                game_state = "tutorial"
            if event.key == pygame.K_ESCAPE and game_state == 'playing':
                if input_cooldown == False:
                    game_state = "pause"
                    print(game_state)
                    input_cooldown = True
            if event.key == pygame.K_ESCAPE and game_state == 'pause':
                if input_cooldown == False:
                    game_state = "playing"
                    print(game_state)
                    input_cooldown = True
            if event.key == pygame.K_RETURN and game_state == 'end':
                game_state = "start"
            input_cooldown = True
        elif event.type == pygame.KEYUP:
            input_cooldown = False
        

    # get keys that are currently pressed
    keys = pygame.key.get_pressed()

    # check for dash key
    if keys[pygame.K_SPACE] and not is_dashing and cooldown_timer == 0:
        is_dashing = True
        pygame.mixer.Sound.play(woosh)
        dash_timer = dash_duration
        cooldown_timer = dash_cooldown
        if honey_covered == True:
            dash_duration = 24
            create_particles(player_rect.x + player_rect.width / 2, player_rect.y + player_rect.height / 2, ORANGE, 6, count=4)

    if cooldown_timer == 0:
        normal_rotation_speed = -5

    # update player position based on pressed keys
    if game_state == "playing":
        if keys[pygame.K_LEFT] and player_rect.left> 0:
            player_rect.x -= dash_speed if is_dashing else player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += dash_speed if is_dashing else player_speed
        if keys[pygame.K_UP] and player_rect.top > 0:
            player_rect.y -= dash_speed if is_dashing else player_speed
        if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
            player_rect.y += dash_speed if is_dashing else player_speed

        # dash timer
        if dash_timer > 0:
            dash_timer -= 1
            rotation_speed = dash_rotation_speed
        else:
            is_dashing = False
            rotation_speed = normal_rotation_speed

        # bomb timer
        if bomb_timer > 0:
            bomb_timer -= 1

        # cooldown timer decreases per frame
        if cooldown_timer > 0:
            cooldown_timer -= 1
        
        if honey_duration > 0:
            honey_duration -= 1

        # rotate the player image
        rotated_player = pygame.transform.rotate(player_image, rotation_angle)
        rotated_rect = rotated_player.get_rect(center=player_rect.center)

    if game_state == "playing":
        # lemon spawn
        if random.randint(1, 100) <= lemon_chance:  
            lemon_rect = lemon_image.get_rect()
            lemon_rect.x = random.randint(0, WIDTH - lemon_rect.width)
            lemon_rect.y = -lemon_rect.height
            lemons.append(lemon_rect)
            if score > 10:
                lemon_count += 1

        # mega lemon spawn
        if score > 80:
            if random.randint(1, 1000) <= mega_lemon_chance:
                mega_lemon_rect = mega_lemon_image.get_rect()
                mega_lemon_rect.x = random.randint(0, WIDTH - mega_lemon_rect.width)
                mega_lemon_rect.y = -mega_lemon_rect.height
                mega_lemons.append(mega_lemon_rect)
                mega_lemon_count += 1
        # mega lemon spawn
        if score > 0:
            if random.randint(1, 1000) <= honey_lemon_chance:
                honey_lemon_rect = honey_lemon_image.get_rect()
                honey_lemon_rect.x = random.randint(0, WIDTH - honey_lemon_rect.width)
                honey_lemon_rect.y = -honey_lemon_rect.height
                honey_lemons.append(honey_lemon_rect)
                honey_lemon_count += 1

        # rocks spawn randomly
        if score > 10:
            if score > 50:
                rock_chance = 2
                speed_multiplier = 1
                if score > 100:
                    rock_chance = 2
                    speed_multiplier = 1.25
                    if score > 200:
                        rock_chance == 3
                        player_speed = 5.5
                        speed_multiplier = 1.5
                    if score > 300:
                        rock_chance == 4
                        player_speed = 6
                        speed_multiplier = 1.75
                        dash_speed = 24
                        dash_cooldown = 30
                    if score > 400:
                        rock_chance == 5
                        speed_multiplier = 2
                    if score > 500:
                        player_speed = 7
                        speed_multiplier = 2.25
                        dash_cooldown = 25
                    if score > 800:
                        player_speed = 8
                        rock_chance == 8
            if random.randint(1, 100) <= rock_chance:  # adjust the probability of rock spawn
                rock_rect = rock_image.get_rect()
                rock_rect.x = random.randint(0, WIDTH - rock_rect.width)
                rock_rect.y = -rock_rect.height
                rocks.append(rock_rect)
                rock_count += 1

        # bombs spawn randomly
            if random.randint(1, 1000) <= rock_chance and bomb_timer == 0:
                bomb_rect = bomb_image.get_rect()
                bomb_timer = random.randint(round(50 * 1/speed_multiplier), round(100 * 1/speed_multiplier))
                bomb_rect.x = random.randint(0, WIDTH - bomb_rect.width)
                bomb_rect.y = -bomb_rect.height
                bombs.append(bomb_rect)
                bomb_count += 1
            if bomb_timer == 1:
                expanded_bomb_rect = bomb_image.get_rect()
                for expanded_bomb_rect in bombs:
                    bombs.remove(expanded_bomb_rect)
                    pygame.mixer.Sound.play(explosion)
                    create_particles(expanded_bomb_rect.x + expanded_bomb_rect.width / 2, expanded_bomb_rect.y + expanded_bomb_rect.height / 2, RED, 7, count=10)
                    create_particles(expanded_bomb_rect.x + expanded_bomb_rect.width / 2, expanded_bomb_rect.y + expanded_bomb_rect.height / 2, GRAY, 7, count=10)
                    for lemon_rect in lemons:
                        if lemon_rect.colliderect(expanded_bomb_rect):
                            lemons.remove(lemon_rect)
                            score += 1
                    for rock_rect in rocks:
                        if rock_rect.colliderect(expanded_bomb_rect):
                            rocks.remove(rock_rect)
                            score += 1
                    for mega_lemon_rect in mega_lemons:
                        if mega_lemon_rect.colliderect(expanded_bomb_rect):
                            mega_lemons.remove(mega_lemon_rect)
                            score += 1
                    for honey_lemon_rect in honey_lemons:
                        if honey_lemon_rect.colliderect(expanded_bomb_rect):
                            honey_lemons.remove(honey_lemon_rect)
                            score += 1
                    if player_rect.colliderect(expanded_bomb_rect):
                        pygame.mixer.Sound.play(death)
                        game_state = "end"
                        player_rect.center = (WIDTH // 2, HEIGHT // 2)
                        lemons = []
                        mega_lemons = []
                        honey_lemons = []
                        bombs = []
                        rocks = []
                        score = 0
                        speed_multiplier = 0.75
                        honey_duration = 0
                        honey_covered = False
                        player_image = normal_player_image
                        rock_chance = 1
                        player_speed = 5
                        dash_speed = 15
                        dash_cooldown = 35
                        luck = 100 - ((rock_count * 2 / (lemon_count * 1.3 + mega_lemon_count * 10)) * 100)
                        shadow_show = True
                

    if game_state == "playing":
        # move and check for collisions with lemons
        for lemon_rect in lemons:
            lemon_rect.y += lemon_speed * speed_multiplier
            if lemon_rect.colliderect(player_rect):
                lemons.remove(lemon_rect)
                score += 1
                score_count = score
                decide = random.randint(1,3)
                #if decide == 0:
                #    cut_sound = pygame.mixer.Sound(cut)
                #    cut_sound.set_volume(0.8)
                #    cut_sound.play()
                if decide == 1:
                    cut_sound = pygame.mixer.Sound(cut1)
                    cut_sound.set_volume(1)
                    cut_sound.play()
                if decide == 2:
                    cut_sound = pygame.mixer.Sound(cut2)
                    cut_sound.set_volume(1)
                    cut_sound.play()
                if decide == 3:
                    cut_sound = pygame.mixer.Sound(cut3)
                    cut_sound.set_volume(1.7)
                    cut_sound.play()

                create_particles(lemon_rect.x + lemon_rect.width / 2, lemon_rect.y + lemon_rect.height / 2, YELLOW, 5, count=4)
        
        for mega_lemon_rect in mega_lemons:
            mega_lemon_rect.y += lemon_speed * speed_multiplier * 1.1
            if mega_lemon_rect.colliderect(player_rect):
                mega_lemons.remove(mega_lemon_rect)
                score += 5
                pygame.mixer.Sound.play(cutmega)
                for x in range(10):
                    lemon_rect = lemon_image.get_rect()
                    lemon_rect.x = random.randint(0, WIDTH - lemon_rect.width)
                    lemon_rect.y = -lemon_rect.height
                    lemons.append(lemon_rect)
                create_particles(mega_lemon_rect.x + mega_lemon_rect.width / 2, mega_lemon_rect.y + mega_lemon_rect.height / 2, ORANGE, 6, count=10)
        
        
        
        for honey_lemon_rect in honey_lemons:
            honey_lemon_rect.y += lemon_speed * speed_multiplier * 1.1
            if honey_lemon_rect.colliderect(player_rect):
                honey_lemons.remove(honey_lemon_rect)
                score += 5
                honey_covered = True
                player_image = honey_player_image
                honey_duration = 300
                pygame.mixer.Sound.play(cuthoney)
                create_particles(honey_lemon_rect.x + honey_lemon_rect.width / 2, honey_lemon_rect.y + honey_lemon_rect.height / 2, ORANGE, 6, count=10)
        if honey_duration == 0:
            dash_duration = 12
            honey_covered = False
            player_image = normal_player_image

        # move and check for collisions with rocks
        for rock_rect in rocks:
            rock_rect.y += rock_speed * speed_multiplier
            if rock_rect.colliderect(player_rect) and is_dashing == False and honey_covered == False:
                # player hit a rock, reset the game
                pygame.mixer.Sound.play(death)
                # player hit a rock, reset the game
                pygame.mixer.Sound.play(death)
                game_state = "end"
                player_rect.center = (WIDTH // 2, HEIGHT // 2)
                lemons = []
                mega_lemons = []
                honey_lemons = []
                bombs = []
                rocks = []
                score = 0
                speed_multiplier = 0.75
                honey_duration = 0
                honey_covered = False
                player_image = normal_player_image
                rock_chance = 1
                player_speed = 5
                dash_speed = 15
                dash_cooldown = 35
                luck = 100 - ((rock_count * 2 / (lemon_count * 1.3 + mega_lemon_count * 10)) * 100)
                shadow_show = True
            elif rock_rect.colliderect(player_rect) and is_dashing == False and honey_covered == True:
                rocks.remove(rock_rect)
                pygame.mixer.Sound.play(cuthoney)
                pygame.mixer.Sound.play(death)
                honey_covered = False
                score += 2
                honey_duration = 0
                player_image = normal_player_image
                create_particles(rock_rect.x + rock_rect.width / 2, rock_rect.y + rock_rect.height / 2, GRAY, 5, count=10)
            elif rock_rect.colliderect(player_rect) and honey_covered == True and is_dashing == True:
                pygame.mixer.Sound.play(cuthoney)
                rocks.remove(rock_rect)
                score += 2
                create_particles(rock_rect.x + rock_rect.width / 2, rock_rect.y + rock_rect.height / 2, GRAY, 5, count=10)
            elif rock_rect.colliderect(player_rect) and is_dashing == True and honey_covered == False:
                rocks.remove(rock_rect)
                pygame.mixer.Sound.play(death)
                is_dashing = False
                cooldown_timer = 100
                normal_rotation_speed = 10
                score += 2
                create_particles(rock_rect.x + rock_rect.width / 2, rock_rect.y + rock_rect.height / 2, GRAY, 5, count=10)
        
        for bomb_rect in bombs:
            bomb_rect.y += rock_speed * speed_multiplier
        #     if bomb_rect.colliderect(player_rect):
        #         # player hit a rock, reset the game
        #         pygame.mixer.Sound.play(death)
        #         game_state = "end"
        #         player_rect.center = (WIDTH // 2, HEIGHT // 2)
        #         lemons = []
        #         mega_lemons = []
        #         honey_lemons = []
        #         rocks = []
        #         bombs = []
        #         score = 0
        #         speed_multiplier = 0.75
        #         honey_duration = 0
        #         honey_covered = False
        #         player_image = normal_player_image
        #         rock_chance = 1
        #         player_speed = 5
        #         dash_speed = 15
        #         dash_cooldown = 35
        #         luck = 100 - ((rock_count * 2 / (lemon_count * 1.3 + mega_lemon_count * 10)) * 100)
        #         shadow_show = True
            
                

        rotation_angle += rotation_speed

    # Draw background and game elements based on game state
    if game_state == "start":
        title_rect.y = initial_title_y + 10 * math.sin(pygame.time.get_ticks() * 0.005)
        title_rect.x = 100
        screen.blit(start_image, (0, 0))
        screen.blit(start_key, title_rect)
        font = pygame.font.Font(font_file, 36)
        high_score_text = font.render(f"Best: {high_score}", True, BLACK)
        high_score_text.set_alpha(95)
        text_rect = high_score_text.get_rect(center=(WIDTH/2, HEIGHT/4))
        screen.blit(high_score_text, text_rect)


    elif game_state == 'pause':
        if shadow_show == True:
            screen.blit(pause_image, (0, 0))
            shadow_show = False

    if game_state == 'end':
        if shadow_show == True:
            screen.blit(shadow, (0, 0))
            shadow_show = False
        
        if last_score > 0:
            
            font = pygame.font.Font(font_file, 50)
            score_text = font.render(f"Score: {last_score}", True, BLACK)
            score_text.set_alpha(95)
            screen.blit(score_text, (100, 260))
            luck = round(luck)
            luck_text = font.render(f"Luck: {luck}% Average", True, BLACK)
            luck_text.set_alpha(95)
            if luck >= 40:
                luck_text = font.render(f"Luck: {luck}%", True, YELLOW)
                if luck >= 70:
                    luck_text = font.render(f"Luck: {luck}%", True, GREEN)
            else:
                luck_text = font.render(f"Luck: {luck}%", True, RED)
            screen.blit(luck_text, (100, 440))
            
            # Display and update the high score
            if type(high_score) == "<class 'NoneType'>":
                high_score = 0
            if last_score > high_score:
                high_score = last_score
            high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
            screen.blit(high_score_text, (100, 350))
            font = pygame.font.Font(font_file, 36)
            text = font.render("Press Enter to play again", True, YELLOW)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/3))
            screen.blit(text, text_rect)
            font = pygame.font.Font(font_file, 100)
            death_text = font.render(f"You Died!", True, RED)
            text_rect = death_text.get_rect(center=(WIDTH/2, HEIGHT/6))
            screen.blit(death_text, text_rect)

    elif game_state == "tutorial":
        screen.blit(tutorial_image, (0, 0))


    elif game_state == "playing":
        shadow_show = True
        screen.blit(background, (0, 0))
        # update background positions for scrolling effect
        background_pos1 += background_speed * speed_multiplier
        background_pos2 += background_speed * speed_multiplier

        # if first background image moves off screen, reset opsition
        if background_pos1 >= HEIGHT:
            background_pos1 = -background.get_height()

        # if second background image moves off screen, reset position
        if background_pos2 >= HEIGHT:
            background_pos2 = -background.get_height()

        # draw both backgrounds 
        screen.blit(background, (0, background_pos1))
        screen.blit(background, (0, background_pos2))
        screen.blit(rotated_player, rotated_rect)

        # draw lemons
        for lemon_rect in lemons:
            screen.blit(lemon_image, lemon_rect)

        for mega_lemon_rect in mega_lemons:
            screen.blit(mega_lemon_image, mega_lemon_rect)

        for honey_lemon_rect in honey_lemons:
            screen.blit(honey_lemon_image, honey_lemon_rect)

        # draw rocks
        for rock_rect in rocks:
            screen.blit(rock_image, rock_rect)

        for bomb_rect in bombs:
            screen.blit(bomb_image, bomb_rect)
        
        

        # draw score
        font = pygame.font.Font(font_file, 100)
        score_text = font.render(f"{score}", True, BLACK)
        score_text.set_alpha(80)
        screen.blit(score_text, (30, 30))
        last_score = score

        # draw particle
        for particle in particles:
            particle.move()
            particle.draw(screen)
        # remove particles
        particles = [particle for particle in particles if particle.speed > 0]

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
