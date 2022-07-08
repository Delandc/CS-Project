import tkinter as tk
from tkinter import *
from pygame.locals import *
from PIL import Image
import pygame
import os
import time
import random
import sys

root = tk.Tk()
root.geometry("850x700")
imw=tk.PhotoImage(file='warning2.png')
file="bgr.gif"

info = Image.open(file)

frames = info.n_frames  

im = [tk.PhotoImage(file=file,format=f"gif -index {i}") for i in range(frames)]

count = 0
anim = None
def animation(count):
    global anim
    im2 = im[count]

    gif_label.configure(image=im2)
    count += 1
    if count == frames:
        count = 0
    anim = root.after(50,lambda :animation(count))

gif_label = tk.Label(root, text='test',image="")
gif_label.pack()

label= tk.Label(root,text="MAIN MENU",font='20',bd=0)
#label.place(x=425,y=50,anchor="center")

main_frame=tk.Frame(root,bd=4)
#main_frame.place(x=0,y=0,width=850,height=700)

def spaceinv():
    pygame.font.init()
    WIDTH, HEIGHT = 750, 750
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders")

    # Load images
    RED_SPACE_SHIP = pygame.image.load(os.path.join(r"C:\CS Project\redship.png"))
    GREEN_SPACE_SHIP = pygame.image.load(os.path.join(r"C:\CS Project\greenship.png"))
    BLUE_SPACE_SHIP = pygame.image.load(os.path.join(r"C:\CS Project\blueship.png"))

    # Player player
    YELLOW_SPACE_SHIP = pygame.image.load(os.path.join(r"C:\CS Project\spaceship.png"))

    # Lasers
    RED_LASER = pygame.image.load(os.path.join(r"C:\CS Project\pixel_laser_red.png"))
    GREEN_LASER = pygame.image.load(os.path.join(r"C:\CS Project\pixel_laser_green.png"))
    BLUE_LASER = pygame.image.load(os.path.join(r"C:\CS Project\pixel_laser_blue.png"))
    YELLOW_LASER = pygame.image.load(os.path.join(r"C:\CS Project\pixel_laser_yellow.png"))

    # Background
    BG = pygame.transform.scale(pygame.image.load(os.path.join(r"C:\CS Project\background-black.png")), (WIDTH, HEIGHT))

    class Laser:
        def __init__(self, x, y, img):
            self.x = x
            self.y = y
            self.img = img
            self.mask = pygame.mask.from_surface(self.img)

        def draw(self, window):
            window.blit(self.img, (self.x, self.y))

        def move(self, vel):
            self.y += vel

        def off_screen(self, height):
            return not(self.y <= height and self.y >= 0)

        def collision(self, obj):
            return collide(self, obj)


    class Ship:
        COOLDOWN = 30

        def __init__(self, x, y, health=100):
            self.x = x
            self.y = y
            self.health = health
            self.ship_img = None
            self.laser_img = None
            self.lasers = []
            self.cool_down_counter = 0

        def draw(self, window):
            window.blit(self.ship_img, (self.x, self.y))
            for laser in self.lasers:
                laser.draw(window)

        def move_lasers(self, vel, obj):
            self.cooldown()
            for laser in self.lasers:
                laser.move(vel)
                if laser.off_screen(HEIGHT):
                    self.lasers.remove(laser)
                elif laser.collision(obj):
                    obj.health -= 10
                    self.lasers.remove(laser)

        def cooldown(self):
            if self.cool_down_counter >= self.COOLDOWN:
                self.cool_down_counter = 0
            elif self.cool_down_counter > 0:
                self.cool_down_counter += 1

        def shoot(self):
            if self.cool_down_counter == 0:
                laser = Laser(self.x, self.y, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1

        def get_width(self):
            return self.ship_img.get_width()

        def get_height(self):
            return self.ship_img.get_height()


    class Player(Ship):
        def __init__(self, x, y, health=100):
            super().__init__(x, y, health)
            self.ship_img = YELLOW_SPACE_SHIP
            self.laser_img = YELLOW_LASER
            self.mask = pygame.mask.from_surface(self.ship_img)
            self.max_health = health

        def move_lasers(self, vel, objs):
            self.cooldown()
            for laser in self.lasers:
                laser.move(vel)
                if laser.off_screen(HEIGHT):
                    self.lasers.remove(laser)
                else:
                    for obj in objs:
                        if laser.collision(obj):
                            objs.remove(obj)
                            if laser in self.lasers:
                                self.lasers.remove(laser)

        def draw(self, window):
            super().draw(window)
            self.healthbar(window)

        def healthbar(self, window):
            pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
            pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


    class Enemy(Ship):
        COLOR_MAP = {
                    "red": (RED_SPACE_SHIP, RED_LASER),
                    "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                    "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                    }

        def __init__(self, x, y, color, health=100):
            super().__init__(x, y, health)
            self.ship_img, self.laser_img = self.COLOR_MAP[color]
            self.mask = pygame.mask.from_surface(self.ship_img)

        def move(self, vel):
            self.y += vel

        def shoot(self):
            if self.cool_down_counter == 0:
                laser = Laser(self.x-20, self.y, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1


    def collide(obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

    def main():
        run = True
        FPS = 60
        level = 0
        lives = 5
        main_font = pygame.font.SysFont("comicsans", 50)
        lost_font = pygame.font.SysFont("comicsans", 60)

        enemies = []
        wave_length = 5
        enemy_vel = 1

        player_vel = 5
        laser_vel = 5

        player = Player(300, 630)

        clock = pygame.time.Clock()

        lost = False
        lost_count = 0

        def redraw_window():
            WIN.blit(BG, (0,0))
            # draw text
            lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
            level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

            WIN.blit(lives_label, (10, 10))
            WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

            for enemy in enemies:
                enemy.draw(WIN)

            player.draw(WIN)

            if lost:
                lost_label = lost_font.render("You Lost!!!", 1, (255,255,255))
                WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

            pygame.display.update()

        while run:
            clock.tick(FPS)
            redraw_window()

            if lives <= 0 or player.health <= 0:
                lost = True
                lost_count += 1

            if lost:
                if lost_count > FPS * 3:
                    run = False
                else:
                    continue

            if len(enemies) == 0:
                level += 1
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-2000, -100), random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player.x - player_vel > 0: # left
                player.x -= player_vel
            if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
                player.x += player_vel
            if keys[pygame.K_w] and player.y - player_vel > 0: # up
                player.y -= player_vel
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
                player.y += player_vel
            if keys[pygame.K_SPACE]:
                player.shoot()

            for enemy in enemies[:]:
                enemy.move(enemy_vel)
                enemy.move_lasers(laser_vel, player)

                if random.randrange(0, 2*60) == 1:
                    enemy.shoot()

                if collide(enemy, player):
                    player.health -= 10
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)

            player.move_lasers(-laser_vel, enemies)

    def main_menu():
        title_font = pygame.font.SysFont("comicsans", 50)
        run = True
        while run:
            WIN.blit(BG, (0,0))
            title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
            WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE: #escape quits
                       run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    main()
        pygame.quit()
    main_menu()
        
sinb=tk.Button(root,text='SPACE INVADERS',font=('Comic Sans MS','12','bold'),fg='black',bg='cyan',bd=5,command=spaceinv)
sinb.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.055,anchor='center')

def pong():
    pygame.init()
    WIDTH, HEIGHT = 700, 500
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")

    FPS = 60

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
    BALL_RADIUS = 7

    SCORE_FONT = pygame.font.SysFont("comicsans", 50)
    WINNING_SCORE = 10


    class Paddle:
        COLOR = WHITE
        VEL = 4

        def __init__(self, x, y, width, height):
            self.x = self.original_x = x
            self.y = self.original_y = y
            self.width = width
            self.height = height

        def draw(self, win):
            pygame.draw.rect(
                win, self.COLOR, (self.x, self.y, self.width, self.height))

        def move(self, up=True):
            if up:
                self.y -= self.VEL
            else:
                self.y += self.VEL

        def reset(self):
            self.x = self.original_x
            self.y = self.original_y


    class Ball:
        MAX_VEL = 5
        COLOR = WHITE

        def __init__(self, x, y, radius):
            self.x = self.original_x = x
            self.y = self.original_y = y
            self.radius = radius
            self.x_vel = self.MAX_VEL
            self.y_vel = 0

        def draw(self, win):
            pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

        def move(self):
            self.x += self.x_vel
            self.y += self.y_vel

        def reset(self):
            self.x = self.original_x
            self.y = self.original_y
            self.y_vel = 0
            self.x_vel *= -1


    def draw(win, paddles, ball, left_score, right_score):
        win.fill(BLACK)

        left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
        right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
        win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 20))
        win.blit(right_score_text, (WIDTH * (3/4) -
                                    right_score_text.get_width()//2, 20))

        for paddle in paddles:
            paddle.draw(win)

        for i in range(10, HEIGHT, HEIGHT//20):
            if i % 2 == 1:
                continue
            pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

        ball.draw(win)
        pygame.display.update()


    def handle_collision(ball, left_paddle, right_paddle):
        if ball.y + ball.radius >= HEIGHT:
            ball.y_vel *= -1
        elif ball.y - ball.radius <= 0:
            ball.y_vel *= -1

        if ball.x_vel < 0:
            if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
                if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                    ball.x_vel *= -1

                    middle_y = left_paddle.y + left_paddle.height / 2
                    difference_in_y = middle_y - ball.y
                    reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                    y_vel = difference_in_y / reduction_factor
                    ball.y_vel = -1 * y_vel

        else:
            if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
                if ball.x + ball.radius >= right_paddle.x:
                    ball.x_vel *= -1

                    middle_y = right_paddle.y + right_paddle.height / 2
                    difference_in_y = middle_y - ball.y
                    reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
                    y_vel = difference_in_y / reduction_factor
                    ball.y_vel = -1 * y_vel


    def handle_paddle_movement(keys, left_paddle, right_paddle):
        if keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
            left_paddle.move(up=True)
        if keys[pygame.K_s] and left_paddle.y + left_paddle.VEL + left_paddle.height <= HEIGHT:
            left_paddle.move(up=False)

        if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
            right_paddle.move(up=True)
        if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT:
            right_paddle.move(up=False)


    def main():
        run = True
        clock = pygame.time.Clock()

        left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT //
                             2, PADDLE_WIDTH, PADDLE_HEIGHT)
        right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT //
                              2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

        left_score = 0
        right_score = 0

        while run:
            clock.tick(FPS)
            draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE: #escape quits
                        run = False
                    break

            keys = pygame.key.get_pressed()
            handle_paddle_movement(keys, left_paddle, right_paddle)

            ball.move()
            handle_collision(ball, left_paddle, right_paddle)

            if ball.x < 0:
                right_score += 1
                ball.reset()
            elif ball.x > WIDTH:
                left_score += 1
                ball.reset()

            won = False
            if left_score >= WINNING_SCORE:
                won = True
                win_text = "Left Player Won!"
            elif right_score >= WINNING_SCORE:
                won = True
                win_text = "Right Player Won!"

            if won:
                text = SCORE_FONT.render(win_text, 1, WHITE)
                WIN.blit(text, (WIDTH//2 - text.get_width() //
                                2, HEIGHT//2 - text.get_height()//2))
                pygame.display.update()
                pygame.time.delay(5000)
                ball.reset()
                left_paddle.reset()
                right_paddle.reset()
                left_score = 0
                right_score = 0

        pygame.quit()
    main()
    
pob=tk.Button(root,text='PONG',font=('Comic Sans MS','12','bold'),fg='black',bg='cyan',bd=5,command=pong)
pob.place(relx=0.5,rely=0.6,relwidth=0.5,relheight=0.055,anchor='center')

def tr():
    WINDOWWIDTH = 800
    WINDOWHEIGHT = 600
    TEXTCOLOR = (255, 255, 255)
    BACKGROUNDCOLOR = (0, 0, 0)
    FPS = 40
    BADDIEMINSIZE = 10
    BADDIEMAXSIZE = 40
    BADDIEMINSPEED = 8
    BADDIEMAXSPEED = 8
    ADDNEWBADDIERATE = 6
    PLAYERMOVERATE = 5
    count=3

    def terminate():
        pygame.quit()
        sys.exit()

    def waitForPlayerToPressKey():
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE: #escape quits
                        terminate()
                    return

    def playerHasHitBaddie(playerRect, baddies):
        for b in baddies:
            if playerRect.colliderect(b['rect']):
                return True
        return False

    def drawText(text, font, surface, x, y):
        textobj = font.render(text, 1, TEXTCOLOR)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    # set up pygame, the window, and the mouse cursor
    pygame.init()
    mainClock = pygame.time.Clock()
    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('car race')
    pygame.mouse.set_visible(False)

    # fonts
    font = pygame.font.SysFont(None, 30)

    # sounds
    gameOverSound = pygame.mixer.Sound('music_crash.wav')
    pygame.mixer.music.load('music_car.wav')
    laugh = pygame.mixer.Sound('music_laugh.wav')


    # images
    playerImage = pygame.image.load('car1.png')
    car3 = pygame.image.load('car3.png')
    car4 = pygame.image.load('car4.png')
    playerRect = playerImage.get_rect()
    baddieImage = pygame.image.load('car2.png')
    sample = [car3,car4,baddieImage]
    wallLeft = pygame.image.load('left.png')
    wallRight = pygame.image.load('right.png')


    # "Start" screen
    drawText('Press any key to start the game.', font, windowSurface, (WINDOWWIDTH / 3) - 30, (WINDOWHEIGHT / 3))
    drawText('And Enjoy', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3)+30)
    pygame.display.update()
    waitForPlayerToPressKey()
    zero=0
    if not os.path.exists("save.dat"):
        f=open("save.dat",'w')
        f.write(str(zero))
        f.close()   
    v=open("save.dat",'r')
    topScore = (v.readline())
    v.close()
    while (count>0):
        # start of the game
        baddies = []
        score = 0
        playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
        moveLeft = moveRight = moveUp = moveDown = False
        reverseCheat = slowCheat = False
        baddieAddCounter = 0
        pygame.mixer.music.play(-1, 0.0)

        while True: # the game loop
            score += 1 # increase score

            for event in pygame.event.get():
                
                if event.type == QUIT:
                    terminate()

                if event.type == KEYDOWN:
                    if event.key == ord('z'):
                        reverseCheat = True
                    if event.key == ord('x'):
                        slowCheat = True
                    if event.key == K_LEFT or event.key == ord('a'):
                        moveRight = False
                        moveLeft = True
                    if event.key == K_RIGHT or event.key == ord('d'):
                        moveLeft = False
                        moveRight = True
                    if event.key == K_UP or event.key == ord('w'):
                        moveDown = False
                        moveUp = True
                    if event.key == K_DOWN or event.key == ord('s'):
                        moveUp = False
                        moveDown = True

                if event.type == KEYUP:
                    if event.key == ord('z'):
                        reverseCheat = False
                        score = 0
                    if event.key == ord('x'):
                        slowCheat = False
                        score = 0
                    if event.key == K_ESCAPE:
                            terminate()
                   

                    if event.key == K_LEFT or event.key == ord('a'):
                        moveLeft = False
                    if event.key == K_RIGHT or event.key == ord('d'):
                        moveRight = False
                    if event.key == K_UP or event.key == ord('w'):
                        moveUp = False
                    if event.key == K_DOWN or event.key == ord('s'):
                        moveDown = False

                

            # Add new baddies at the top of the screen
            if not reverseCheat and not slowCheat:
                baddieAddCounter += 1
            if baddieAddCounter == ADDNEWBADDIERATE:
                baddieAddCounter = 0
                baddieSize =30 
                newBaddie = {'rect': pygame.Rect(random.randint(140, 485), 0 - baddieSize, 23, 47),
                            'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                            'surface':pygame.transform.scale(random.choice(sample), (23, 47)),
                            }
                baddies.append(newBaddie)
                sideLeft= {'rect': pygame.Rect(0,0,126,600),
                           'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                           'surface':pygame.transform.scale(wallLeft, (126, 599)),
                           }
                baddies.append(sideLeft)
                sideRight= {'rect': pygame.Rect(497,0,303,600),
                           'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                           'surface':pygame.transform.scale(wallRight, (303, 599)),
                           }
                baddies.append(sideRight)
                
                

            # Move the player around.
            if moveLeft and playerRect.left > 0:
                playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
            if moveRight and playerRect.right < WINDOWWIDTH:
                playerRect.move_ip(PLAYERMOVERATE, 0)
            if moveUp and playerRect.top > 0:
                playerRect.move_ip(0, -1 * PLAYERMOVERATE)
            if moveDown and playerRect.bottom < WINDOWHEIGHT:
                playerRect.move_ip(0, PLAYERMOVERATE)
            
            for b in baddies:
                if not reverseCheat and not slowCheat:
                    b['rect'].move_ip(0, b['speed'])
                elif reverseCheat:
                    b['rect'].move_ip(0, -5)
                elif slowCheat:
                    b['rect'].move_ip(0, 1)

             
            for b in baddies[:]:
                if b['rect'].top > WINDOWHEIGHT:
                    baddies.remove(b)

            # Draw the game world on the window.
            windowSurface.fill(BACKGROUNDCOLOR)

            # Draw the score and top score.
            drawText('Score: %s' % (score), font, windowSurface, 128, 0)
            drawText('Top Score: %s' % (topScore), font, windowSurface,128, 20)
            drawText('Rest Life: %s' % (count), font, windowSurface,128, 40)
            
            windowSurface.blit(playerImage, playerRect)

            
            for b in baddies:
                windowSurface.blit(b['surface'], b['rect'])

            pygame.display.update()

            # Check if any of the car have hit the player.
            if playerHasHitBaddie(playerRect, baddies):
                if str(score) > topScore:
                    g=open("save.dat",'w')
                    g.write(str(score))
                    g.close()
                    topScore = score
                break

            mainClock.tick(FPS)


        # "Game Over" screen.
        pygame.mixer.music.stop()
        count=count-1
        gameOverSound.play()
        time.sleep(1)
        if (count==0):
         laugh.play()
         drawText('Game over', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
         drawText('Press any key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 30)
         pygame.display.update()
         time.sleep(2)
         waitForPlayerToPressKey()
         count=3
         gameOverSound.stop()

trb=tk.Button(root,text='TRAFFIC RIDER',font=('Comic Sans MS','12','bold'),fg='black',bg='cyan',bd=5,command=tr)
trb.place(relx=0.5,rely=0.7,relwidth=0.5,relheight=0.055,anchor='center')    

def exw():
    warn=tk.Toplevel(bg='white')
    warn.geometry("400x200")
    lw=tk.Label(warn, image=imw,bg='white')
    lw.place(relx=0.18, rely=0.3,anchor='center')
    def ex():
        warn.destroy()
        root.destroy()
    def ex1():
        warn.destroy()
    b1=tk.Button(warn,text = "Yes, I quit",activeforeground='red', command=ex,bd=4)
    b1.place(relx=0.3,rely=0.7,anchor="center")
    b2=tk.Button(warn,text = "No, go back", command=ex1,bd=4)
    b2.place(relx=0.7,rely=0.7,anchor="center")
    war=tk.Label(warn,text="Are you sure you want to quit ?", font=('Comic Sans MS','13','bold'),bg='white')
    war.place(relx=0.25, rely=0.3,anchor='w')
    warn.mainloop()    

eb=tk.Button(root,text='EXIT',font=('Comic Sans MS','12','bold'),activebackground='red',bg='cyan',bd=5,command=exw)
eb.place(relx=0.5,rely=0.8,relwidth=0.5,relheight=0.055,anchor='center')

animation(count)
root.mainloop()
