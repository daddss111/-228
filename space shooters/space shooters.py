import pygame
import random
import sys

# Инициализация
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический бой: Возврат в меню")

# --- ГРАФИКА ---
def create_player_surf():
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (0, 200, 255), [(25, 0), (50, 50), (25, 40), (0, 50)])
    pygame.draw.polygon(surf, (255, 255, 255), [(25, 0), (50, 50), (25, 40), (0, 50)], 2)
    return surf

def create_enemy_surf():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (255, 50, 50), [(0, 0), (40, 0), (20, 40)])
    return surf

def create_powerup_surf(color):
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (15, 15), 13)
    pygame.draw.circle(surf, (255, 255, 255), (15, 15), 13, 2)
    return surf

# Ресурсы
player_img = create_player_surf()
enemy_img = create_enemy_surf()
bullet_img = pygame.Surface((8, 18), pygame.SRCALPHA)
pygame.draw.ellipse(bullet_img, (255, 255, 0), (0, 0, 8, 18))

POWERUPS = {"speed": (0, 255, 0), "score": (255, 215, 0), "shield": (0, 150, 255)}
font = pygame.font.SysFont("Arial", 26)
large_font = pygame.font.SysFont("Arial", 60)
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.speed = 8
        self.fire_rate = 20
        self.invincible = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH-40), y=-50)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT: self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dy, is_enemy=False):
        super().__init__()
        self.image = bullet_img.copy()
        if is_enemy:
            self.image = pygame.transform.flip(self.image, False, True)
            self.image.fill((255, 50, 50), special_flags=pygame.BLEND_ADD)
        self.rect = self.image.get_rect(center=(x, y))
        self.dy = dy

    def update(self):
        self.rect.y += self.dy
        if self.rect.bottom < 0 or self.rect.top > HEIGHT: self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(list(POWERUPS.keys()))
        self.image = create_powerup_surf(POWERUPS[self.type])
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT: self.kill()

def menu_screen():
    while True:
        screen.fill((15, 15, 35))
        title = large_font.render("ВЫБОР СЛОЖНОСТИ", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        btns = [("Легкий", (0, 255, 0), 250), ("Средний", (255, 165, 0), 330), ("Тяжелый", (255, 50, 50), 410)]
        rects = []
        for text, color, y in btns:
            r = pygame.Rect(WIDTH // 2 - 100, y, 200, 50)
            pygame.draw.rect(screen, color, r, border_radius=10)
            lbl = font.render(text, True, (255, 255, 255))
            screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.y + 12))
            rects.append((r, text))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for r, diff in rects:
                    if r.collidepoint(event.pos): return diff
        pygame.display.flip()
        clock.tick(60)

def game_loop(difficulty):
    player = Player()
    enemies, bullets, e_bullets, powerups = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

    if difficulty == "Легкий": e_spd, spwn, f_ch, eb_spd, p_chance = 3, 45, 0.01, 4, 0.45
    elif difficulty == "Средний": e_spd, spwn, f_ch, eb_spd, p_chance = 4, 32, 0.02, 7, 0.25
    else: e_spd, spwn, f_ch, eb_spd, p_chance = 6, 22, 0.04, 11, 0.15

    score, frame = 0, 0
    speed_t, shield_t = 0, 0

    while True:
        frame += 1
        screen.fill((10, 10, 25))

        if speed_t > 0:
            speed_t -= 1
            if speed_t == 0: player.fire_rate = 20
        if shield_t > 0:
            shield_t -= 1
            player.invincible = True
            if frame % 10 < 5: pygame.draw.circle(screen, (0, 150, 255), player.rect.center, 35, 2)
            if shield_t == 0: player.invincible = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        if frame % player.fire_rate == 0:
            bullets.add(Bullet(player.rect.centerx, player.rect.top, -6))
        if frame % spwn == 0:
            enemies.add(Enemy(e_spd))

        player.update()
        enemies.update(); bullets.update(); e_bullets.update(); powerups.update()

        for e in enemies:
            if random.random() < f_ch:
                e_bullets.add(Bullet(e.rect.centerx, e.rect.bottom, eb_spd, True))

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            if random.random() < p_chance:
                powerups.add(PowerUp(hit.rect.centerx, hit.rect.centery))

        for p in pygame.sprite.spritecollide(player, powerups, True):
            if p.type == "speed": player.fire_rate, speed_t = 7, 400
            elif p.type == "score": score += 150
            elif p.type == "shield": shield_t = 400

        # Поражение: Показываем экран и выходим из цикла в меню
        if not player.invincible:
            if pygame.sprite.spritecollideany(player, enemies) or \
               pygame.sprite.spritecollideany(player, e_bullets):
                screen.fill((0, 0, 0))
                msg = large_font.render("ИГРА ОКОНЧЕНА", True, (255, 50, 50))
                sc_msg = font.render(f"Ваш счет: {score}", True, (255, 255, 255))
                screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(sc_msg, (WIDTH // 2 - sc_msg.get_width() // 2, HEIGHT // 2 + 50))
                pygame.display.flip()
                pygame.time.wait(2000) 
                return # Возврат в main() -> menu_screen()

        powerups.draw(screen); bullets.draw(screen); e_bullets.draw(screen); enemies.draw(screen)
        screen.blit(player.image, player.rect)
        info = font.render(f"Счет: {score}", True, (255, 255, 255))
        screen.blit(info, (15, 15))
        pygame.display.flip()
        clock.tick(60)

def main():
    while True:
        diff = menu_screen() # Шаг 1: Выбор сложности
        game_loop(diff)      # Шаг 2: Игра до поражения
                             # Шаг 3: Автоматический возврат к Шагу 1

if __name__ == "__main__":
    main()