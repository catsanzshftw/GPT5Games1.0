#!/usr/bin/env python3
# src/pong.py — Classic Pong (Full Source), 60fps, instant replay prompt, M1/PC/Linux

import sys, math, pygame, numpy as np

# --- Config ---
WIDTH, HEIGHT   = 800, 600
FPS             = 60
PADDLE_W        = 12
PADDLE_H        = 100
BALL_SIZE       = 14
PADDLE_SPEED    = 6
AI_SPEED        = 5
BALL_SPEED_MIN  = 5
BALL_SPEED_MAX  = 8
WIN_SCORE       = 5
WHITE           = (240, 240, 240)
BLACK           = (0, 0, 0)
FONT_NAME       = None
MIDLINE_WIDTH   = 4
SOUND_ON        = True
# ---------------

pygame.init()
if SOUND_ON:
    pygame.mixer.init()
screen  = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong 60fps (GPT-5 M1 Edition)")
clock   = pygame.time.Clock()
font    = pygame.font.SysFont(FONT_NAME, 40, bold=True)
font2   = pygame.font.SysFont(FONT_NAME, 28, bold=True)

def gen_tone(freq=440, duration=0.13, vol=0.38, sr=44100):
    n     = int(sr * duration)
    t     = np.linspace(0, duration, n, endpoint=False)
    wave  = (np.sin(2 * math.pi * freq * t) * vol * 32767).astype(np.int16)
    stereo= np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)

beep = gen_tone(900) if SOUND_ON else None
boop = gen_tone(440) if SOUND_ON else None

def reset_ball(ball, direction):
    ball.center = (WIDTH // 2, HEIGHT // 2)
    speed_x = direction * np.random.randint(BALL_SPEED_MIN, BALL_SPEED_MAX)
    speed_y = np.random.choice([-1, 1]) * np.random.randint(3, 7)
    return [speed_x, speed_y]

def draw_scores(score_l, score_r):
    l = font.render(str(score_l), True, WHITE)
    r = font.render(str(score_r), True, WHITE)
    screen.blit(l, (WIDTH//4 - l.get_width()//2, 26))
    screen.blit(r, (3*WIDTH//4 - r.get_width()//2, 26))

def draw_midline():
    for y in range(0, HEIGHT, 32):
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - MIDLINE_WIDTH//2, y, MIDLINE_WIDTH, 18), border_radius=4)

def game_loop():
    left  = pygame.Rect(30, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
    right = pygame.Rect(WIDTH-42, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
    ball  = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
    ball_vel = reset_ball(ball, np.random.choice([-1, 1]))
    score_l = score_r = 0
    state = "play"

    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if state == "gameover" and e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_y, pygame.K_RETURN):
                    return True
                if e.key in (pygame.K_n, pygame.K_ESCAPE):
                    return False
        keys = pygame.key.get_pressed()
        if state == "play":
            # Player paddle
            if keys[pygame.K_UP]:   right.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN]: right.y += PADDLE_SPEED
            right.clamp_ip(screen.get_rect())
            # AI paddle
            if ball.centery < left.centery - 10:   left.y -= AI_SPEED
            elif ball.centery > left.centery + 10: left.y += AI_SPEED
            left.clamp_ip(screen.get_rect())
            # Ball movement
            ball.x += ball_vel[0]
            ball.y += ball_vel[1]
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_vel[1] *= -1
            # Paddle collisions
            if ball.colliderect(left) and ball_vel[0] < 0:
                ball_vel[0] *= -1; beep and beep.play()
            if ball.colliderect(right) and ball_vel[0] > 0:
                ball_vel[0] *= -1; beep and beep.play()
            # Score
            if ball.left <= 0:
                score_r += 1; boop and boop.play()
                ball_vel = reset_ball(ball, 1)
            if ball.right >= WIDTH:
                score_l += 1; boop and boop.play()
                ball_vel = reset_ball(ball, -1)
            # Win check
            if score_l == WIN_SCORE or score_r == WIN_SCORE:
                state = "gameover"
        # Draw
        screen.fill(BLACK)
        draw_midline()
        pygame.draw.rect(screen, WHITE, left, border_radius=8)
        pygame.draw.rect(screen, WHITE, right, border_radius=8)
        pygame.draw.ellipse(screen, WHITE, ball)
        draw_scores(score_l, score_r)
        if state == "gameover":
            winner = "Left (AI)" if score_l == WIN_SCORE else "Right (You)"
            txt1 = font.render(f"{winner} wins!", True, WHITE)
            txt2 = font2.render("Play again?  Y / N", True, WHITE)
            screen.blit(txt1, (WIDTH//2 - txt1.get_width()//2, HEIGHT//2 - 44))
            screen.blit(txt2, (WIDTH//2 - txt2.get_width()//2, HEIGHT//2 + 16))
        pygame.display.flip()

if __name__ == "__main__":
    while game_loop():
        pass  # restarts cleanly if Y/Enter pressed at game over
