# TODO: normal platform_spawn()
# TODO: no jumping while jetpack
# TODO: new boosters
# TODO: Enemy hit sound
# Jumpy! - platform game
# Art from Kenney.nl
# Happy tune by https://opengameart.org/users/syncopika
# Yippee by https://opengameart.org/users/snabisch
# Sadness by https://opengameart.org/users/kistol

import pygame
import random
from settings import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        # initialize game window, etc
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.font_name = pygame.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        try:
            with open(path.join(self.dir, HS_FILE), 'r') as hsfile:  # 'with' automatically closes file
                self.highscore = int(hsfile.read())
        except FileNotFoundError:
            self.highscore = 0
        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

        # load cloud images
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pygame.image.load(path.join(img_dir, 'cloud{}.png'.format(i))).convert())

        # load sounds
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'Jump29.wav'))
        self.boost_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'Boost22.wav'))

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.clouds = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        for i in range(3):
            cl = Cloud(self)
            cl.rect.y += 500
        self.mob_timer = 0
        pygame.mixer.music.load(path.join(self.snd_dir, 'happytune.ogg'))
        pygame.mixer.music.set_volume(1)
        self.run()

    def run(self):
        # Game Loop
        pygame.mixer.music.play(loops=-1)
        self.is_playing = True
        while self.is_playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # check if player hits a platform - only if falling #
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = max(hits, key=lambda x: x.rect.bottom)
                if lowest.rect.left - 8 < self.player.pos.x < lowest.rect.right + 8:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.is_jumping = False

        # if player riches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)  # abs ~ module
            if random.randrange(100) < 8:
                Cloud(self)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        # spawn a mob?
        now = pygame.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):  # thousands variants in range => choice
            self.mob_timer = now
            Mob(self)

        # if mob rectangle hits player rectangle
        mob_hits = pygame.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits and self.player.rect.right < WIDTH and self.player.rect.left > 0:
            # if mob mask hits player mask
            mob_mask_hits = pygame.sprite.spritecollide(self.player, mob_hits, False, pygame.sprite.collide_mask)
            if mob_mask_hits:
                self.is_playing = False

        # if player hits a powerup
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for pow in powerup_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.is_jumping = False
        # Die!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self. player.vel.y, 10)
                if sprite. rect.bottom < 0:
                    sprite.kill()
            if len(self.platforms) == 0:
                self.is_playing = False

        # spawn new platforms to keep same average number
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH-width),
                     random.randrange(-75, -30))

    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing the window
            if event.type == pygame.QUIT:
                if self.is_playing:
                    self.is_playing = False
                self.is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame. K_SPACE:
                    self.player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame. K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)

        # after drawing everything flip the display
        pygame.display.flip()

    def show_start_screen(self):
        # game start screen
        pygame.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, BLUE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move, Space to jump", 22, MAGENTA, WIDTH / 2, HEIGHT /2)
        self.draw_text("Press a key to play", 22, RED, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def show_gameover_screen(self):
        # game over/continue screen
        pygame.mixer.music.load(path.join(self.snd_dir, 'Sadness.ogg'))
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(loops=-1)
        if not self.is_running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, RED, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Your score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, BLUE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, RED, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as hsfile:
                hsfile.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, MAGENTA, WIDTH / 2, HEIGHT / 2 - 40)
        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def wait_for_key(self):
        is_waiting = True
        while is_waiting:
            self.clock.tick(30)  # No need to refresh screen 50 fps, if it isn't animated
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_waiting = False
                    self.is_running = False
                if event.type == pygame.KEYUP:
                    is_waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.is_running:
    g.new()
    g.show_gameover_screen()

pygame.quit()
