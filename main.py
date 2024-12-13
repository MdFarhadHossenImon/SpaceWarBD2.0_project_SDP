import pygame
from pygame import mixer
from pygame.locals import *
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

#define fps
clock = pygame.time.Clock()
fps = 60

# Update screen resolution
screen_width = 1920
screen_height = 1080

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Bangladesh 2.0')

#define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

#load sounds
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)

#define game variables
rows = 2  # Increase the number of rows
cols = 10  # Increase the number of columns
alien_cooldown = 1000 #bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()
countdown = 5
last_count = pygame.time.get_ticks()
game_over = 0 #0 is no game over, 1 means player has won, -1 means player has lost
score = 0  # Initialize score

#define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

#load image
bg = pygame.image.load("img/bdbg1.png")
bg = pygame.transform.scale(bg, (screen_width, screen_height))

def draw_bg():
    screen.blit(bg, (0, 0))

#define function for creating text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#create spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/BD Students.png")
        self.image = pygame.transform.scale(self.image, (150, 150)) # Make the spaceship bigger
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        #set movement speed
        speed = 8
        #set a cooldown variable
        cooldown = 500 #milliseconds
        game_over = 0

        #get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed
        #record current time
        time_now = pygame.time.get_ticks()
        #shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        #update mask
        self.mask = pygame.mask.from_surface(self.image)

        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

#create Bullets class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.image = pygame.transform.scale(self.image, (10, 20)) # Adjust size as needed
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 8
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            global score
            score += 10  # Increase score for each alien hit

#create Aliens class
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/" + str(random.randint(1, 5)) + ".png")
        self.image = pygame.transform.scale(self.image, (150, 150)) # Adjust size as needed
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

#create Alien Bullets class
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.image = pygame.transform.scale(self.image, (10, 20)) # Adjust size as needed
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 10
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            #reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

#create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            #add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        #update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

#create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
    #generate aliens
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(180 + item * 180, 180 + row * 180)
            alien_group.add(alien)

create_aliens()

#create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

# Create buttons
def draw_buttons():
    restart_button = pygame.Rect(screen_width - 220, screen_height - 60, 105, 50)
    exit_button = pygame.Rect(screen_width - 100, screen_height - 60, 90, 50)
    pygame.draw.rect(screen, green, restart_button)
    pygame.draw.rect(screen, red, exit_button)
    draw_text('Restart', font30, white, restart_button.x + 10, restart_button.y + 10)
    draw_text('Exit', font30, white, exit_button.x + 20, exit_button.y + 10)
    return restart_button, exit_button





# Initialize the game state
game_active = False
run = True

while run:
    clock.tick(fps)

    # Draw background
    draw_bg()

    if not game_active:  # If the game is not active, show the "GET READY" screen
        if countdown > 0:
            draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
            draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
            count_timer = pygame.time.get_ticks()
            if count_timer - last_count > 1000:
                countdown -= 1
                last_count = count_timer
        else:
            game_active = True
            create_aliens()  # Start the game when countdown ends

    if game_active:  # If the game is active
        # Create random alien bullets
        time_now = pygame.time.get_ticks()
        if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now

        # Check if all the aliens have been killed
        if len(alien_group) == 0:
            game_over = 1

        if game_over == 0:
            # Update spaceship
            game_over = spaceship.update()

            # Update sprite groups
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
        else:
            if game_over == -1:
                draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
            if game_over == 1:
                draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))

    # Draw buttons
    restart_button, exit_button = draw_buttons()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    # Check for button clicks
    if restart_button.collidepoint(mouse_pos) and mouse_click[0] == 1:
        # Restart the game
        game_active = True
        countdown = 5
        game_over = 0
        score = 0
        create_aliens()
        spaceship.health_remaining = spaceship.health_start

    if exit_button.collidepoint(mouse_pos) and mouse_click[0] == 1:
        run = False

    # Update explosion group
    explosion_group.update()

    # Draw sprite groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    # Event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
