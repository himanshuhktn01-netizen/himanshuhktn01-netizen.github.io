# /// script
# dependencies = [
#     "pygame-ce",
# ]
# ///

import asyncio
import pygame
from pygame import mixer
import random
import math
import sys

pygame.init()

# variables
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))


font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 60)

# background music and image
audio_extension = "ogg" if sys.platform == "emscripten" else "mp3"
mixer.music.load(f'Myassests/Game Music.{audio_extension}')
background=pygame.image.load('Myassests/background.png')
# sounds
bullet_music=mixer.Sound(f'Myassests/Bullet shot .{audio_extension}')
Ekill_music=mixer.Sound(f'Myassests/Enemy damage.{audio_extension}')
damage_music=mixer.Sound(f'Myassests/Player damage.{audio_extension}')
wave_change_sound=mixer.Sound(f'Myassests/Wave up.{audio_extension}')

# LOGO and name
icon=pygame.image.load("Myassests/LOGO.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Goblin Slayer")
#  ALL images 
player_img = pygame.transform.scale(
    pygame.image.load("Myassests/player.png"), (180, 100)
)
goblin_img = pygame.transform.scale(
    pygame.image.load("Myassests/goblin2.png"), (120, 120)
)
boss_img = pygame.transform.scale(
    pygame.image.load("Myassests/gbossgoblinwave3.png"), (140, 140)
)
bullet_img = pygame.transform.scale(
    pygame.image.load("Myassests/pbullet.png"), (20, 20)
)
ground = pygame.image.load("Myassests/Grass.png")   
bullet_sign = pygame.transform.scale(
    pygame.image.load('Myassests/gammo.png'), (50, 50)
)


#  FUNCTIONS

def is_collision_bullet(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt(
        (enemy_x - bullet_x) ** 2 +
        (enemy_y - bullet_y) ** 2
    )
    return distance < 70


# CLASSES

# player class=Player stats, drawing, and actions,
class Player:
   
    def __init__(self):
        self.health = 100
        self.wallet = 0
        self.bull_count = 18
        self.damage = 20
        self.x = 0
        self.y = 350
        self.rect = pygame.Rect(0, 350, 180, 100)
        self.damage_cooldown = 0
        self.image = player_img
        self.message=''
        self.messagetimer=0
        self.damage_music=damage_music

    def take_damage(self, amount):
      
        self.health-=amount
        self.damage_music.play()
        self.damage_cooldown = 1100
 
    def add_money(self, amount):
        self.wallet += amount

    def reload(self):
        
        if self.bull_count == 18:
            return

        elif self.wallet >= 50:
        
            self.bull_count = 18
            self.wallet -= 50
            self.message = "Reloaded!"
            self.messagetimer = 120
        

    def p_health(self):
        if self.health<100:
            self.health+=50
            if self.health>100:
                self.health=100
            

    def can_shoot(self):
        # checking for shooting 
        if self.bull_count > 0:
            self.bull_count -= 1
            return True
        return False

    def draw_data(self, surface):
        # data_details 
        surface.blit(
            small_font.render(f"Health : {self.health}", True, (255, 0, 0)),
            (20, 20)
        )
        surface.blit(
            small_font.render(f"Ammo : {self.bull_count}", True, (0, 0, 255)),
            (20, 55)
        )
        surface.blit(
            small_font.render(f"Wallet : {self.wallet}", True, (0, 150, 0)),
            (20, 90)
        )

    def draw(self, surface):
        # player invisible rectangle creation 
        surface.blit(self.image, (self.x, self.y))
        self.rect = pygame.Rect(self.x, self.y, 180, 100)

    def draw_reload_sign(self, surface):
        if self.bull_count == 0:
            surface.blit(bullet_sign, (45, 300))

# bullet class= Bullet state, movement, and drawing
class Bullet:
    
    def __init__(self):
        self.x = 150
        self.y = 365
        self.state = "ready"   # "ready" or "fire"
        self.image = bullet_img
        self.music=bullet_music
        self.ekill=Ekill_music
    def fire(self):
        if self.state == "ready":
            self.state = "fire"
            self.x = 150   
            bullet_music.play()


    def move(self):
        if self.state == "fire":
            self.x += 10
            if self.x >= WIDTH:
                self.state = "ready"
                self.x = 150

    def draw(self, surface):
        if self.state == "fire":
            surface.blit(self.image, (self.x, self.y))

    def reset(self):
        self.state = "ready"
        self.x = 150
        self.ekill.play()

# class enemy= for enemy details like position,stats and drawing
class Enemy:
  
    def __init__(self, enemy_type, x, y, health, speed, money, damage):
        self.type = enemy_type   # "goblin" or "boss"
        self.x = x
        self.y = y
        self.health = health
        self.speed = speed
        self.money = money
        self.damage = damage
        
        if self.type == "goblin":               
            self.image = goblin_img
            self.width = 120
            self.height = 120
        else:
            self.image = boss_img
            self.width = 140
            self.height = 140

    def move(self):
        if self.x > 120:
            self.x -= self.speed
        else:
            self.x = 120

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def get_rect(self):
        # enemy imaginary rectangle 
        return pygame.Rect(self.x, self.y, self.width, self.height)

# class wave= handle waves data spawning, and wave progression.
class WaveManager:

    def __init__(self):
        self.wave_data = {
            "wave1": [
                {"goblin": 8, "G_health": 30, "g_spd": 0.6},
                {"boss": 1, "b_health": 80, "b_spd": 0.5},
            ],
            "wave2": [
                {"goblin": 10, "G_health": 35, "g_spd": 0.8},
                {"boss": 2, "b_health": 90, "b_spd": 0.6},
            ],
            "wave3": [
                {"goblin": 12, "G_health": 40, "g_spd": 1},
                {"boss": 3, "b_health": 95, "b_spd": 1},
            ],
            "wave4": [
                {"goblin": 14, "G_health": 45, "g_spd": 1.2},
                {"boss": 4, "b_health": 100, "b_spd": 1.4},
            ],
            "wave5": [
                {"goblin": 16, "G_health": 50, "g_spd": 1.5},
                {"boss": 5, "b_health": 120, "b_spd": 1.7 },
            ]

        }
        self.current_wave = 1
        self.wave_change_sound=wave_change_sound

    def spawn_wave(self, wave_number):
        # gives a list of Enemy objects for the given wave.
      
        enemies = []
        data = self.wave_data[f"wave{wave_number}"]
        goblin = data[0]
        boss = data[1]

        for i in range(goblin["goblin"]):
            enemies.append(Enemy(
                "goblin",
                random.randint(900, 1100),
                348,
                goblin["G_health"],
                goblin['g_spd'],
                10,
                10
            ))

        for _ in range(boss["boss"]):
            enemies.append(Enemy(
                "boss",
                random.randint(1000, 1200),
                320,
                boss["b_health"],
                boss['b_spd'],
                20,
                18
            ))
        
        self.wave_change_sound.play()

      
        return enemies
        

    def next_wave(self):
        
        # for increase wave no. and return true if more waves else win
        self.current_wave += 1
        return self.current_wave <= len(self.wave_data)

# class game=control all game events
class Game:
    
    def __init__(self):
       
        self.running = True
        self.game_state = "menu"   # "menu", "game", "end", "win"
        self.music_started = False

        # Create components
        self.player = Player()
        self.bullet = Bullet()
        
        self.wave_manager = WaveManager()

        # Enemies list
        self.enemies = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.game_state == "menu":
                        self.start_music()
                        self.game_state = "game"
                        if len(self.enemies) == 0:
                            self.enemies = self.wave_manager.spawn_wave(
                                self.wave_manager.current_wave
                            )

                    elif self.game_state == "end" or self.game_state == "win":
                        self.start_music()
                        # Reset everything
                        self.player.health = 100
                        self.player.wallet = 0
                        self.player.bull_count = 18
                        self.bullet.reset()
                        self.wave_manager.current_wave = 1
                        self.enemies = self.wave_manager.spawn_wave(
                            self.wave_manager.current_wave
                        )
                        self.game_state = "game"

    def start_music(self):
        if not self.music_started:
            mixer.music.play(-1)
            self.music_started = True

    def update(self):
        if self.game_state != "game":
            return

     
        # Bullet
        keys = pygame.key.get_pressed()

        # Shoot
        if keys[pygame.K_SPACE] and self.bullet.state == "ready":
            if self.player.can_shoot():
                self.bullet.fire()

        # Reload
        if keys[pygame.K_r]:
            self.player.reload()
        # Health
        if keys[pygame.K_h]:
            self.player.p_health()

        # Move bullet
        self.bullet.move()

        # Enemies
        for enemy in self.enemies:
            enemy.move()

            # Bullet collision
            if (self.bullet.state == "fire" and
                is_collision_bullet(enemy.x, enemy.y,
                                    self.bullet.x, self.bullet.y)):
                if enemy.health <= self.player.damage:
                    self.player.add_money(enemy.money)
                    self.enemies.remove(enemy)
                else:
                    enemy.health -= self.player.damage
                
                self.bullet.reset()

            # Player collision
            if self.player.damage_cooldown==0:
                if self.player.rect.colliderect(enemy.get_rect()):
                    self.player.take_damage(enemy.damage)
            else:
                self.player.damage_cooldown-=1

        # Wave progression
        if len(self.enemies) == 0:
            if self.wave_manager.next_wave():
                self.enemies = self.wave_manager.spawn_wave(
                    self.wave_manager.current_wave
                )
            else:
                self.game_state = "win"

        # Player death
        if self.player.health <= 0:
            self.game_state = "end"

    def draw(self):
        # Clear screen
        screen.fill((255, 255, 255))

        if self.game_state == "menu":
            # Menu screen
            title = font.render(
                "Welcome to Goblin Slayer!",
                True, (0, 100, 0)
            )
            screen.blit(title, (250, 90))

            screen.blit(font.render("Controls", True, (0, 0, 0)), (410, 180))
            screen.blit(font.render("SPACE - Shoot", True, (0, 0, 0)), (380, 230))
            screen.blit(font.render("R - Reload ,    Cost=50", True, (0, 0, 0)), (380, 280))
            screen.blit(font.render("H - Health ,    Cost=100", True, (0, 0, 0)), (380,330))
            screen.blit(font.render("ENTER - Start", True, (0, 0, 0)), (380, 380))

            start = big_font .render("Press ENTER to Start", True, (200, 0, 0))
            screen.blit(start, (225, 450))

        elif self.game_state == "game":
            # background
            screen.blit(background,(0,0))
            # ground
            screen.blit(ground, (0, 520))
            screen.blit(ground, (500, 520))
            screen.blit(ground, (0, 450))
            screen.blit(ground, (500, 450))

            # Player
            self.player.draw(screen)

          
            self.player.draw_data(screen)
            screen.blit(
                small_font.render(f"Wave : {self.wave_manager.current_wave}",
                                  True, (120, 0, 120)),
                (20, 125)
            )
            if self.player.messagetimer > 0:
                screen.blit(
                    font.render(self.player.message, True, (0, 220, 0)),
                     (150, 170)
                    )
                self.player.messagetimer-=1
             
            # Bullet
            self.bullet.draw(screen)

            # Enemies
            for enemy in self.enemies:
                enemy.draw(screen)

            # Reload sign
            self.player.draw_reload_sign(screen)

        elif self.game_state == "end":
            screen.fill((20, 20, 20))
            title = font.render("YOU HAVE FALLEN...", True, (180, 0, 0))
            screen.blit(title, (325, 70))
            screen.blit(
                font.render("The goblins overran the village.", True, (220, 220, 220)),
                (235, 170)
            )
            screen.blit(
                font.render("Your courage will be remembered.", True, (220, 220, 220)),
                (215, 230)
            )
            screen.blit(
                font.render("Another village still needs you!", True, (255, 215, 0)),
                (225, 330)
            )
            screen.blit(
                big_font.render("Press ENTER to Play Again", True, (0, 255, 0)),
                (180, 460)
            )

        elif self.game_state == "win":
            screen.fill((20, 20, 20))
            title = font.render("YOU WIN!", True, (0, 255, 0))
            screen.blit(title, (315,70))
            msg1 = font.render("You defeated every goblin!", True, (255, 255, 255))
            screen.blit(msg1, (250, 170))
            msg2 = font.render("The village is safe once again.", True, (255, 255, 255))
            screen.blit(msg2, (250, 230))
            reward = font.render(f"Final Wallet: {self.player.wallet}", True, (255, 215, 0))
            screen.blit(reward, (350, 320))
            restart = big_font.render("Press ENTER to Save another village", True, (0, 255, 0))
            screen.blit(restart, (30, 450))

        pygame.display.update()

    async def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            await asyncio.sleep(0)


async def main():
    game = Game()
    await game.run()
    pygame.quit()


asyncio.run(main())
