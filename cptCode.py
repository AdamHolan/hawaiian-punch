import pygame
import random

# some colours
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

pygame.init()

# screen dimensions
size = (800, 600)
screen = pygame.display.set_mode(size)

pygame.display.set_caption('mario killaz')

# loop until close
done = False

# screen updates (for readability)
clock = pygame.time.Clock()


class character(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        super().__init__()
        self.name = name
        self.idleImage = pygame.image.load('ryu.png').convert()
        self.idleImage.set_colorkey(black)
        self.punchImage = pygame.image.load('ryuPunch.png').convert()
        self.punchImage.set_colorkey(black)
        self.blockImage = pygame.image.load('ryuBlock.png').convert()
        self.blockImage.set_colorkey(black)
        self.image = self.idleImage
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.fruitsList = pygame.sprite.Group()
        self.xChange = 0
        self.yChange = 0
        self.health = 100
        self.attack = 10
        self.speed = 3
        self.attacking = False
        self.blocking = False
        self.attackTimer = 0
        self.punchAnimationTimer = 0
        self.enemy = None
        self.font = pygame.font.SysFont('comicsansms', 50)
        # player specific attributes
        if self.name == 'player1':
            self.healthBarLocation = 100
        # flip images to face
        else:
            self.healthBarLocation = 500
            self.idleImage = pygame.transform.flip(self.idleImage, True, False)
            self.punchImage = pygame.transform.flip(self.punchImage, True, False)
            self.blockImage = pygame.transform.flip(self.blockImage, True, False)
        self.platformList = pygame.sprite.Group()



    # def draw(self):
    #     if self.attacking:
    def healthBar(self):
        pygame.draw.rect(screen, red, [self.healthBarLocation, 50, 200, 25])
        pygame.draw.rect(screen, green, [self.healthBarLocation, 50, self.health * 2, 25])

    def update(self):

        self.calcGravity()

        if self.attacking and not self.blocking:
            if self.attackTimer < 10:
                self.image = self.punchImage
            else:
                self.attacking = False

        elif self.blocking:
            self.speed
            self.image = self.blockImage

        else:
            self.image = self.idleImage
        self.rect.x += self.xChange
        self.rect.y += self.yChange
        self.healthBar()

        # control how fast you can punch. at 60 fps it takes 1 second
        if self.attackTimer != 0:
            # self.attacking = False
            self.attackTimer += 1
            if self.attackTimer == 20:
                self.attackTimer = 0

        enemyColList = pygame.sprite.spritecollide(self, [self.enemy], False)

        for enemy in enemyColList:
            if self.name == 'player2':
                self.stop()
            else:
                self.rect.right = self.enemy.rect.left

        self.platformHitList = pygame.sprite.spritecollide(self, self.platformList, False)
        for platform in self.platformHitList:
            if self.yChange > 0:
                self.rect.bottom = platform.rect.top

        self.yChange = 0

        fruitHitList = pygame.sprite.spritecollide(self, self.fruitsList, True)

        for fruit in fruitHitList:
            if fruit.name == 'banana':
                self.speed += 1
            if fruit.name == 'mango':
                self.attack += 5
            if fruit.name == 'coconut':
                self.health -= 10
    def moveRight(self):
        self.xChange = self.speed

    def moveLeft(self):
        self.xChange = -self.speed

    def calcGravity(self):
        if self.yChange == 0:
            self.yChange = 1
        else:
            self.yChange += 0.35

    def stop(self):
        self.xChange = 0

    # def checkCol(self, enemy):

    def punch(self):
        if self.attackTimer == 0:
            self.attacking = True
            self.attackTimer += 1

        if not self.blocking and self.attacking:
            inflated = self.rect.inflate(30, 0)
            if inflated.colliderect(self.enemy):
                if self.enemy.blocking:
                    self.enemy.health -= self.attack / 10
                else:
                    self.enemy.health -= self.attack

    def block(self):
        self.blocking = True

    def deathCheck(self):
        dead = False
        if self.health <= 0:
            dead = True
        return dead

    def jump(self):
        self.rect.y += 2
        self.platformHitList = pygame.sprite.spritecollide(self, self.platformList, False)
        self.rect.y -= 2

        if len(self.platformHitList) > 0:
            self.yChange = -20


class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = size[0]
        self.height = size[1]
        self.image = pygame.Surface([self.width, self.height])
       # self.image.fill(red)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 440


class Fruit(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.name = random.choice(('banana', 'mango', 'coconut'))
        
        print(self.name)
        self.image = pygame.image.load(self.name + '.png').convert()
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(size[0])
        self.rect.y = 0
        self.platformList = pygame.sprite.Group()

        # Attributes
        # self.changeX = 0
        self.changeY = 1

    def update(self):
        self.calcGravity()
        # self.rect.x += self.changeX
        self.rect.y += self.changeY
        self.platformHitList = pygame.sprite.spritecollide(self, self.platformList, False)
        for platform in self.platformList:
            if len(self.platformHitList) > 0:
                self.rect.bottom = platform.rect.top
                if self.name == 'coconut':
                    self.rect.y = 800
            # basically destroy it but im moving it away from the screen, never to be touched

    def calcGravity(self):
        if self.changeY > 0:
            self.changeY += 0.35

background = pygame.image.load("beachBackground.png").convert()

# platform and player initilization (outside loop)

playersList = pygame.sprite.Group()
mainPlatform = platform()
platformList = pygame.sprite.Group()
platformList.add(platform())
fruitsList = pygame.sprite.Group()


def fightKeyhandler():
    done = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                player1.moveRight()
            if event.key == pygame.K_a:
                player1.moveLeft()
            if event.key == pygame.K_e:
                player1.punch()
            if event.key == pygame.K_SPACE:
                player1.jump()
            if event.key == pygame.K_q:
                player1.block()
            if event.key == pygame.K_RIGHT:
                player2.moveRight()
            if event.key == pygame.K_LEFT:
                player2.moveLeft()
            if event.key == pygame.K_SLASH:
                player2.punch()
            if event.key == pygame.K_ESCAPE:
                done = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                player1.stop()
            if event.key == pygame.K_a:
                player1.stop()
            if event.key == pygame.K_e:
                player1.attacking = False
            if event.key == pygame.K_q:
                player1.blocking = False
            if event.key == pygame.K_RIGHT:
                player2.stop()
            if event.key == pygame.K_LEFT:
                player2.stop()
            if event.key == pygame.K_SLASH:
                player2.attacking = False
        return done

def menuKeyhandler():
    scene = 0
    done = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                scene = 1
    return scene, done

roundNum = 1
scene = 2
player1Points = 0
player2Points = 0

def score():
    font = pygame.font.SysFont('comicsansms', 50)
    player1PointsOnScreen = font.render(str(player1Points), True, white)
    player2PointsOnScreen = font.render(str(player2Points), True, white)
    screen.blit(player1PointsOnScreen, [330, 45])
    screen.blit(player2PointsOnScreen, [450, 45])


def fight(roundNum, player1Points, player2Points):
    # spawn rate
    scene = 1
    if random.randint(1, 300) == 1:
        fruit = Fruit()
        fruitsList.add(fruit)
        fruit.platformList.add(mainPlatform)
        for player in playersList:
            player.fruitsList.add(fruit)

    # draw all players
    fruitsList.draw(screen)
    playersList.draw(screen)
    playersList.update()
    fruitsList.update()
    for player in playersList:
        dead = player.deathCheck()
        if dead:
            # check if a player has died and add score acordingly
            if player == player1:
                player2Points += 1
            else:
                player1Points += 1
            # kill the player and reset the scene
            playersList.remove(player)
            roundNum += 1
            scene = 2
    return scene, roundNum, player1Points, player2Points


def roundScreen():
    font = pygame.font.SysFont('comicsansms', 72)
    roundMessage = font.render('Round ' + str(roundNum), False, white)
    pygame.draw.rect(screen, black, [0, 0, size[0], size[1]])
    screen.blit(roundMessage, [100, 100])



# program loop
while not done:
    # event loop
    if scene == 0:
        scene, done = menuKeyhandler()
    elif scene == 1:
        done = fightKeyhandler()
    elif scene == 2:
        # reset player and initiialize them
        # i dont have it outside the loop since i need to do this several times anyway
        for player in playersList:
            playersList.remove(player)
        for fruit in fruitsList:
            fruitsList.remove(fruit)
        player1 = character('player1', 100, 350)
        player2 = character('player2', 500, 350)
        playersList.add(player1)
        playersList.add(player2)
        player1.platformList.add(mainPlatform)
        player2.platformList.add(mainPlatform)
        player1.enemy = player2
        player2.enemy = player1

        scene = 0
    # game logic


    # screen clearing code
    screen.fill(black)
    screen.blit(background,[0,0])

    # game logic

    if scene == 0:
        roundScreen()
    else:
        score()
        scene, roundNum, player1Points, player2Points = fight(roundNum, player1Points, player2Points)

    # update display
    pygame.display.flip()


    # 60 frames
    clock.tick(60)

# close window and quit
pygame.quit()
