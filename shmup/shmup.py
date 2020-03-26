# Shmup game
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3 
# Art from Kenny.nl

import pygame
import random
import os

# Window Constants
WIDTH = 800
HEIGHT = 600
FPS = 30

# Colours
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW =(255,255,0)

POWERUP_TIMER = 5000

# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(50,38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2) - 4
        # pygame.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT-20
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIMER:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -10
        if keystate[pygame.K_RIGHT]:
            self.speedx = 10
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.centerx += self.speedx
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                shoot_sound.play()
                bullet = Bullet(self.rect.centerx,self.rect.top)
                bullets.add(bullet)
                all_sprites.add(bullet)
            if self.power >= 2:
                shoot_sound.play()
                bullet1 = Bullet(self.rect.left,self.rect.centery)
                bullet2 = Bullet(self.rect.right,self.rect.centery)
                bullets.add(bullet1)
                bullets.add(bullet2)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2 , HEIGHT +2000)


# Mob
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pygame.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.x = random.randrange(WIDTH-self.rect.width)
        self.rect.y = random.randrange(-100,-40)
        self.speedx = random.randrange(-3,3)
        self.speedy = random.randrange(1,20)
        self.rot = 0
        self.rot_speed = random.randrange(-8,8)
        self.last_update = pygame.time.get_ticks()
    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig,self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center 

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.y > HEIGHT or self.rect.left <-30 or self.rect.right > WIDTH +30:
            self.rect.x = random.randrange(WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedx = random.randrange(-3,3)
            self.speedy = random.randrange(1,20)

# Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -20

    def update(self):
        self.rect.bottom += self.speedy
        if self.rect.bottom < 0 :
            self.kill()

# Explosion
class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 10

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# PowerUps
class PowerUp(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield","gun"])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5

    def update(self):
        self.rect.bottom += self.speedy
        if self.rect.top > HEIGHT :
            self.kill()

# new mob
def new_mob():
    m = Mob()
    mobs.add(m)
    all_sprites.add(m)

# Draw lives
def draw_lives(surf,x,y,lives,img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x - 20 * (lives-1-i)
        img_rect.y = y
        surf.blit(img,img_rect)

# Draw text
font_name = pygame.font.match_font('arial')
def draw_text(surf,text,size,x,y):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text,True,WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surf.blit(text_surface,text_rect)

#Draw shield
def draw_shield(surf,x,y,pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    if pct <= 20:
        colour = RED
    else:
        colour = GREEN
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,WHITE,outline_rect,2)
    pygame.draw.rect(surf,colour,fill_rect)

# Game over
def show_go_screen():
    screen.blit(background,background_rect)
    draw_text(screen,"SHMUP!",64,WIDTH/2,HEIGHT/4)
    draw_text(screen,"Arrow keys to move, Space to shoot",22,WIDTH/2,HEIGHT/2)
    draw_text(screen,"Press enter to play again",18,WIDTH/2,HEIGHT *3/4)
    draw_text(screen,str(score),18,WIDTH/2,10)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting = False

# Initialisations
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

# folder path
file_path = os.path.dirname(__file__)
folder_path = os.path.join(file_path,"images")
sound_path = os.path.join(file_path,"sounds")
explosions_path = os.path.join(file_path,"Explosions")

# Load all images
background = pygame.image.load(os.path.join(folder_path,"starfield.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(folder_path,"player.png")).convert()
player_mini_img = pygame.transform.scale(player_img,(17,13))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(os.path.join(folder_path,"laser.png")).convert()

meteor_images = []
meteor_list = ['meteorBig1.png','meteorBig2.png','meteorBig3.png','meteorMed1.png',
                'meteorMed2.png','meteorSmall1.png','meteorTiny1.png','meteorTiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(folder_path,img)).convert())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range (9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(explosions_path,filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img,(75,75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img,(32,32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(explosions_path,filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['gun'] = pygame.image.load(os.path.join(folder_path,"bolt_gold.png")).convert()
powerup_images['shield'] = pygame.image.load(os.path.join(folder_path,"shield_gold.png")).convert()

# load all sounds
shoot_sound = pygame.mixer.Sound(os.path.join(sound_path,"laser_shoot.wav"))
shield_sound = pygame.mixer.Sound(os.path.join(sound_path,"Powerup1.wav"))
gun_sound = pygame.mixer.Sound(os.path.join(sound_path,"Powerup2.wav"))
expl_sounds = []
for snd in ['Explosion1.wav','Explosion1.wav']:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(sound_path,snd)))

player_die_sound = pygame.mixer.Sound(os.path.join(sound_path,"rumble1.ogg"))
pygame.mixer.music.load(os.path.join(sound_path,"tgfcoder-FrozenJam-SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(0.2)


all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
number_of_mobs = 8
player = Player()
all_sprites.add(player)
for i in range(number_of_mobs):
    new_mob()

score = 0

pygame.mixer.music.play(loops = -1)

# Game loop
game_over = True
running = True

while running:
    if game_over:
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        number_of_mobs = 8
        player = Player()
        all_sprites.add(player)
        for i in range(number_of_mobs):
            new_mob()
        show_go_screen()
        game_over = False
        
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # Update
    all_sprites.update()

    # bullet collides with mob
    hits = pygame.sprite.groupcollide(mobs,bullets,True,True)
    for hit in hits:
        if random.random() > 0.9:
            pow = PowerUp(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        random.choice(expl_sounds).play()
        score += 55 - hit.radius
        new_mob()
        explosion = Explosion(hit.rect.center,'lg')
        all_sprites.add(explosion)

    # PowerUp collides with player
    hits = pygame.sprite.spritecollide(player,powerups,True)

    for hit in hits:
        if hit.type == 'shield':
            shield_sound.play()
            player.shield += random.randrange(10,30)
            if player.shield >=100:
                   player.shield =100

        if hit.type == 'gun':
            gun_sound.play()
            player.powerup()

    # player collides with mob
    hits = pygame.sprite.spritecollide(player,mobs,True,pygame.sprite.collide_circle)

    for hit in  hits:
        player.shield -= hit.radius * 2
        explosion = Explosion(hit.rect.center,'sm')
        all_sprites.add(explosion)
        new_mob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center,'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100 

    # if both player and explosion dead
    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    # Drawing and rendering
    screen.fill(BLACK)
    screen.blit(background,background_rect)
    all_sprites.draw(screen)
    draw_text(screen,str(score),18,WIDTH/2,10)
    draw_lives(screen,WIDTH - 20,5,player.lives,player_mini_img)
    draw_shield(screen,5,5,player.shield)

    # Flipping
    pygame.display.flip()

pygame.quit()