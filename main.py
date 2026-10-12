# main.py --

### Imports ###
import sys
from random import choice, randint
from time import sleep

import pygame as pg
pg.init()


### Data ###
game_over = False
dt = 0

SCR_WIDTH = 720
SCR_HEIGHT = 720

SPR_WIDTH = 40 # scale width, height
SPR_HEIGHT = 40

SPACING = 20

P_RATE = 5
p_timer = P_RATE

FPS = 60


## Fonts
LARGE_FONT = pg.font.Font("assets/game_font.ttf", 30)
SMALL_FONT = pg.font.Font("assets/game_font.ttf", 16)

# Image Paths
BG_IMG_PATH = "assets/UI/space_background.png"
BG_IMG = pg.image.load(BG_IMG_PATH)

PLAYER_IMG_PATH = "assets/Players/playerShip2_blue.png"
LASER_IMG_PATH = "assets/Lasers/laserBlue16.png"

ENEMY_IMG_PATH_1 = "assets/Enemies/enemyBlack1.png"
ENEMY_IMG_PATH_2 = "assets/Enemies/enemyBlack2.png"
ENEMY_IMG_PATH_3 = "assets/Enemies/enemyBlack3.png"
ENEMY_IMG_PATH_4 = "assets/Enemies/enemyBlack4.png"
ENEMY_IMG_PATH_5 = "assets/Enemies/enemyBlack5.png"

METEOR_IMG_PATH_1 = "assets/Meteors/meteorGrey_med1.png"
METEOR_IMG_PATH_2 = "assets/Meteors/meteorGrey_med2.png"
METEOR_IMG_PATH_3 = "assets/Meteors/meteorGrey_small1.png"
METEOR_IMG_PATH_4 = "assets/Meteors/meteorGrey_small2.png"
METEOR_IMG_PATH_5 = "assets/Meteors/meteorGrey_tiny1.png"
METEOR_IMG_PATH_6 = "assets/Meteors/meteorGrey_tiny2.png"

HP_IMG_PATH = "assets/Power-ups/pill_blue.png"
FR_IMG_PATH = "assets/Power-ups/bolt_gold.png"

LASER_SFX_PATH = "assets/Audio/laserSmall_002.ogg"
EXPLOTION_SFX_PATH = "assets/Audio/explosionCrunch_002.ogg"

## Path lisst
ENEMY_IMG_PATHS = [ENEMY_IMG_PATH_1, ENEMY_IMG_PATH_2, ENEMY_IMG_PATH_4, ENEMY_IMG_PATH_5]
METEOR_IMG_PATHS = [METEOR_IMG_PATH_1, METEOR_IMG_PATH_2, METEOR_IMG_PATH_3, METEOR_IMG_PATH_4, METEOR_IMG_PATH_5, METEOR_IMG_PATH_6]

### Window Setup ###
mw = pg.display.set_mode((SCR_WIDTH, SCR_HEIGHT))

pg.display.set_caption("Space Shooter")
clock = pg.time.Clock()
### Classes
class BaseSprite(pg.sprite.Sprite):
    def __init__(self, img_path, x_pos, y_pos, step, scale_Width=None, scale_height=None, group=None ):
        super().__init__()
        if scale_Width is not None and scale_height is not None:
            self.image = pg.transform.scale(pg.image.load(img_path), (scale_Width, scale_height))
        else:
            self.image = pg.image.load(img_path)
        
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

        self.step = step

        if group is not None:
            group.add(self)

class PlayerSprite(BaseSprite):
    def __init__(self, img_path, x_pos, y_pos, step, scale_Width=None, scale_height=None, group=None):
        super().__init__(img_path, x_pos, y_pos, step, scale_Width, scale_height, group)
        
        self.start_x = x_pos
        self.start_y = y_pos

        self.lives = 3
        self.score = 0

        self.DEFAULT_SHOOTING_INTERVAL = 0.5
        self.shooting_interval = self.DEFAULT_SHOOTING_INTERVAL
        self.shoot_timer = self.shooting_interval
        self.fr_timer =  None


    def update(self):

        pressed_keys = pg.key.get_pressed()

        ## Momvent Controls
        if (pressed_keys[pg.K_a] or pressed_keys[pg.K_LEFT]) and self.rect.left >= 0:
            self.rect.x -= self.step
        if (pressed_keys[pg.K_d] or pressed_keys[pg.K_RIGHT]) and self.rect.right <= SCR_WIDTH:
            self.rect.x += self.step        

        ## Shooting Controls
        self.shoot_timer -= dt
        if pressed_keys[pg.K_SPACE] and self.shoot_timer <= 0:
            laser_sfx.play()
            laser = LaserSprite(LASER_IMG_PATH, self.rect.centerx - 3, self.rect.y - 20, 6, 6, 36, laser_sprite_group)
            self.shoot_timer = self.shooting_interval

        ## FR Power Timer
        if self.shooting_interval != self.DEFAULT_SHOOTING_INTERVAL:
            if self.fr_timer is None:
                self.fr_timer = 8.0
            else:
                self.fr_timer -= dt
                if self.fr_timer <= 0:
                    self.shooting_interval = self.DEFAULT_SHOOTING_INTERVAL
                    self.fr_timer = None                    

class LaserSprite(BaseSprite):
    def update(self):
        if self.rect.y > -self.rect.height: # comfirm still in inside MW
            self.rect.y -= self.step
            if pg.sprite.groupcollide(laser_sprite_group, enemy_sprite_group, True, True):
                expolotion_sfx.play()
                player.score += 10
                del self
            if pg.sprite.groupcollide(laser_sprite_group, meteor_sprite_group, True, False):
                del self
    
        else:      #remove the laser when it outside the MW
            laser_sprite_group.remove(self)
            del self

class MeteorSprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCR_HEIGHT: #check if sprite still in window
            self.rect.y += self.step
            if pg.sprite.groupcollide(meteor_sprite_group, player_sprite_group, False ,True):
                expolotion_sfx.play()
                player.lives = 0

            if pg.sprite.groupcollide(meteor_sprite_group, enemy_sprite_group, False ,True):
                if self.rect.y >= 0:
                    expolotion_sfx.play()
                    
        else:
            meteor_sprite_group.remove(self) # delete sprite, update health when outside window
            del self

class EnemySprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCR_HEIGHT: #check if sprite still in window
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, enemy_sprite_group, True):
                expolotion_sfx.play()
                player.lives -= 1
                del self
        else:
            enemy_sprite_group.remove(self) # delete sprite, update health when outside window
            player.lives -= 1
            del self

class HPPowerSprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCR_HEIGHT: #check if sprite still in window
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, pu_sprite_group, True) and player.lives <= 5:
                player.lives += 1
                del self
        else:
            pu_sprite_group.remove(self) # delete sprite when outside window
            del self    

class FRPowerSprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCR_HEIGHT: #check if sprite still in window
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, pu_sprite_group, True):
                player.shooting_interval = 0.2
                player.fr_timer = 8.0
                del self
        else:
            pu_sprite_group.remove(self) # delete sprite when outside window
            del self  


### Function ###
def check_quit(event):
    if event.type == pg.QUIT:
        return True
    
def draw_lives():
    lives_img = SMALL_FONT.render(f"Lives {player.lives}", True, (214, 214, 214))
    mw.blit(lives_img, (15, 10))

def draw_score():
    score_img = SMALL_FONT.render(f"{player.score} Score", True, (214, 214, 214))
    mw.blit(score_img, (SCR_WIDTH - score_img.get_width() - 15, 10))

def game_manager():
    if player.lives <= 0:
        txt_img_1 = LARGE_FONT.render("GAME OVER", True, (214, 214, 214))
        txt_img_2 = LARGE_FONT.render("SCORE", True, (214, 214, 214))
        txt_img_3 = LARGE_FONT.render(f"{player.score}", True, (214, 214, 214))

        txt_img_2_cord = (
            (SCR_WIDTH / 2) - (txt_img_2.get_width() / 2),
            (SCR_HEIGHT / 2) - (txt_img_2.get_height() / 2)
        )
        txt_img_1_cord = (
            (SCR_WIDTH / 2) - (txt_img_1.get_width() / 2),
            txt_img_2_cord[1] - txt_img_1.get_height() - SPACING
        )
        txt_img_3_cord = (
            (SCR_WIDTH / 2) - (txt_img_3.get_width() / 2),
            txt_img_2_cord[1] - txt_img_3.get_height() + SPACING
        )      

        mw.blit(txt_img_1, txt_img_1_cord)
        mw.blit(txt_img_2, txt_img_2_cord)
        mw.blit(txt_img_3, txt_img_3_cord)

        return True

def spawn_enemy():
    if len(enemy_sprite_group) < 5:
        enemy = EnemySprite(
            choice(ENEMY_IMG_PATHS),
            randint(SPR_WIDTH, SCR_WIDTH - SPR_WIDTH*2),
            -randint(SPR_HEIGHT, SPR_HEIGHT*6),
            randint(1, 3),
            SPR_WIDTH,
            SPR_HEIGHT,
            enemy_sprite_group
        )

def spawn_meteor():
    if len(enemy_sprite_group) < 2:
        meteor = MeteorSprite(
            choice(METEOR_IMG_PATHS),
            randint(SPR_WIDTH, SCR_WIDTH - SPR_WIDTH * 2),
            -randint(SPR_HEIGHT, SPR_HEIGHT * 6),
            randint(2, 4),
            group=meteor_sprite_group
        )

def spawn_pu(p_timer, dt, P_RATE):
    p_timer -= dt
    if p_timer <= 0:
        p_timer = P_RATE
        spawn_power = bool(randint(0, 2))
        print(f"Spawn power up {spawn_power}") 
        if spawn_power: #only spawn power if true
            power_type = bool(randint(0, 2))
            print(f"Power type: {power_type} (True = HP | False = FR )")
            if power_type: # spawn HP power up 
                power_up = HPPowerSprite(
                    HP_IMG_PATH,
                    randint(SPR_WIDTH, SCR_WIDTH - SPR_WIDTH * 2),
                    -randint(SPR_HEIGHT, SPR_HEIGHT * 6),
                    randint(2, 4),
                    group=pu_sprite_group                 
                )
            elif not power_type: # spawn FR power up
                power_up = FRPowerSprite(
                    FR_IMG_PATH,
                    randint(SPR_WIDTH, SCR_WIDTH - SPR_WIDTH * 2),
                    -randint(SPR_HEIGHT, SPR_HEIGHT * 6),
                    randint(2, 4),
                    group=pu_sprite_group                 
                )                

    return p_timer


### Sprites & Groups

## Groups
player_sprite_group = pg.sprite.Group()
laser_sprite_group = pg.sprite.Group()
enemy_sprite_group = pg.sprite.Group()
meteor_sprite_group = pg.sprite.Group()
pu_sprite_group = pg.sprite.Group()

## sprites
player = PlayerSprite(PLAYER_IMG_PATH, 360, 650, 5, SPR_WIDTH, SPR_HEIGHT, player_sprite_group)

## Sound Effects

laser_sfx = pg.mixer.Sound(LASER_SFX_PATH)
expolotion_sfx = pg.mixer.Sound(EXPLOTION_SFX_PATH)


### Game Loop ###
while not game_over:
    mw.blit(BG_IMG, (0, 0))

    game_over = game_manager()

    draw_lives()
    draw_score()

    spawn_enemy()
    spawn_meteor()
    p_timer = spawn_pu(p_timer, dt, P_RATE)

    player_sprite_group.update()
    laser_sprite_group.update()
    enemy_sprite_group.update()
    meteor_sprite_group.update()
    pu_sprite_group.update()

    player_sprite_group.draw(mw)
    laser_sprite_group.draw(mw)
    enemy_sprite_group.draw(mw)
    meteor_sprite_group.draw(mw)
    pu_sprite_group.draw(mw)


    for event in pg.event.get():
        game_over = check_quit(event)


    pg.display.flip()
    dt = clock.tick(FPS) / 1000


sleep(2)
pg.quit()
sys.exit()