import pygame
import random
import sys

# ==========================================
# 1. ESASY SAZLAMALAR WE BAŞLANGYÇ
# ==========================================

WIDTH  = 480        # Oýun penjiresiniň ini
HEIGHT = 600        # Oýun penjiresiniň boýy
FPS    = 60         # Sekuntdaky kadr sany

# Reňkler (RGB formatynda)
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0  )
RED    = (255, 0,   0  )
GREEN  = (0,   255, 0  )
YELLOW = (255, 255, 0  )

# Pygame-i işe girizmek
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kosmos Goragçysy")
clock = pygame.time.Clock()

# Ekrana tekst çyzmak üçin kömekçi funksiýa
font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


# ==========================================
# 2. OÝUN OBÝEKTLERINIŇ KLASSLARY (OOP)
# ==========================================

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Oýunçynyň gämisi – ýaşyl reňkli blok
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom  = HEIGHT - 10
        self.speedx = 0

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_LEFT]:
            self.speedx = -6
        if keystate[pygame.K_RIGHT]:
            self.speedx = 6

        self.rect.x += self.speedx

        # Ekrandan çykmagynyň öňüni almak
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Duşman (Meteorit) – gyzyl reňkli blok
        self.image = pygame.Surface((30, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self._reset_position()

    def _reset_position(self):
        self.rect.x  = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y  = random.randrange(-100, -40)
        self.speedy  = random.randrange(2, 7)
        self.speedx  = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # Ekrandan çykansoň täzeden ýokardan peýda bolmak
        if (self.rect.top > HEIGHT + 10 or
                self.rect.left < -25 or
                self.rect.right > WIDTH + 20):
            self._reset_position()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Ok – sary reňkli kiçi blok
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottom  = y
        self.rect.centerx = x
        self.speedy = -10   # Ýokaryk uçýar

    def update(self):
        self.rect.y += self.speedy
        # Ekrandan çykyp gitse ýatdan pozmak (memory leak öňüni almak)
        if self.rect.bottom < 0:
            self.kill()


# ==========================================
# 3. TOPARLARY WE OÝNY DÖRETMEK
# ==========================================

all_sprites = pygame.sprite.Group()
mobs        = pygame.sprite.Group()
bullets     = pygame.sprite.Group()

# Oýunçyny döretmek
player = Player()
all_sprites.add(player)

# Başlangyç 8 sany duşman (meteorit)
for _ in range(8):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

score     = 0
game_over = False
running   = True


# ==========================================
# 4. ESASY OÝUN SIKLI (GAME LOOP)
# ==========================================

while running:
    # A) FPS kadalaşdyrmasy
    clock.tick(FPS)

    # B) Wakalary barlamak
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.shoot()
            # Oýun gutaransoň "R" düwmesi bilen täzeden başlamak
            if event.key == pygame.K_r and game_over:
                score     = 0
                game_over = False
                # Ähli sprite-lary arassalamak
                all_sprites.empty()
                mobs.empty()
                bullets.empty()
                player = Player()
                all_sprites.add(player)
                for _ in range(8):
                    m = Mob()
                    all_sprites.add(m)
                    mobs.add(m)

    # C) Logikany täzelemek
    if not game_over:
        all_sprites.update()

        # Çaknyşma 1: Ok duşmana degdimi?
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for _ in hits:
            score += 10
            m = Mob()
            all_sprites.add(m)
            mobs.add(m)

        # Çaknyşma 2: Duşman oýunça degdimi?
        if pygame.sprite.spritecollide(player, mobs, False):
            game_over = True

    # D) Ekrana çyzmak
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, f"Utuk: {score}", 24, WIDTH // 2, 10)

    if game_over:
        draw_text(screen, "OÝUN GUTARDY!",               50, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(screen, f"Utugyňyz: {score}",          30, WIDTH // 2, HEIGHT // 2 + 10)
        draw_text(screen, "Täzeden başlamak üçin [R]",   22, WIDTH // 2, HEIGHT // 2 + 55)
        draw_text(screen, "Çykmak üçin penjireden [X]",  18, WIDTH // 2, HEIGHT // 2 + 90)

    pygame.display.flip()

# Programmany asuda ýapmak
pygame.quit()
sys.exit()
