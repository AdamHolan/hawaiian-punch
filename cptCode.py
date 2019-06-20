# CPT: Hawaiian Punch
# Authors : Adam & Akshay
# Course: ICS3U1
# Date: 2019/06/13

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

background = pygame.image.load("beachBackground.png").convert()


pygame.display.set_caption('Hawaiian Punch')

# loop until close
done = False

# screen updates (for readability)
clock = pygame.time.Clock()

class character(pygame.sprite.Sprite):
    def __init__(self, name, char, x, y):
        super().__init__()
        # name means which player you are, and char is the character you are playing
        self.name = name
        self.char = char

        # image sections, seperated right from left
        self.loadImages(char)

        # rectangle and positional sections
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.xChange = 0
        self.yChange = 0

        # character's attributes
        self.health = 100
        self.attack = 10
        self.punchSpeed = 0
        self.attackTimer = 0
        self.punchAnimationTimer = 0
        self.points = 0

        # used to control the flow of animations
        self.punching = False
        self.blocking = False
        self.enemy = None
        self.moveRight = False
        self.moveLeft = False
        self.showHealth = True
        self.enemyCollision = True

        # player specific attributes
        if self.name == 'player1':
            self.healthBarLocation = 100
            self.idleImage = self.idleImageRight
            self.punchImage = self.punchImageRight
            self.blockImage = self.blockImageRight

        # flip images to face
        else:
            self.healthBarLocation = 500
            self.idleImage = self.idleImageLeft
            self.punchImage = self.punchImageLeft
            self.blockImage = self.blockImageLeft

        # lists for collisions
        self.platformList = pygame.sprite.Group()
        self.fruitsList = pygame.sprite.Group()
        self.charBlockList = pygame.sprite.Group()

    # a useful function for updating images, especially for the css. contains both left and right images.
    def loadImages(self, char):
        self.char = char
        self.idleImageRight = pygame.image.load(char + '.png').convert()
        self.idleImageRight.set_colorkey(green)
        self.punchImageRight = pygame.image.load(char + 'Punch.png').convert()
        self.punchImageRight.set_colorkey(green)
        self.blockImageRight = pygame.image.load(char + 'Block.png').convert()
        self.blockImageRight.set_colorkey(green)

        self.idleImageLeft = pygame.transform.flip(self.idleImageRight, True, False)
        self.punchImageLeft = pygame.transform.flip(self.punchImageRight, True, False)
        self.blockImageLeft = pygame.transform.flip(self.blockImageRight, True, False)
        self.image = self.idleImageRight

    # display a simple healthbar
    def healthBar(self):
        if self.showHealth:
            pygame.draw.rect(screen, red, [self.healthBarLocation, 50, 200, 25])
            pygame.draw.rect(screen, green, [self.healthBarLocation, 50, self.health * 2, 25])

    # main update method, controls animations, collisions, and movement
    def update(self):
        # apply gravity
        self.calcGravity()

        # if punnching, not blocking, and your attack is not on cooldown, display the punch image
        if self.punching and not self.blocking:
            if self.attackTimer < 10:
                self.image = self.punchImage

            # this stops punch image from displaying if it's not on cooldown
            else:
                self.punching = False

        # display blocking image
        elif self.blocking:
            self.image = self.blockImage

        # otherwise, display the base image depending on who is more towards the right
        # this makes sure both players always face eachother
        else:
            self.image = self.idleImage
            if self.rect.x > self.enemy.rect.x:
                self.idleImage = self.idleImageLeft
                self.punchImage = self.punchImageLeft
                self.blockImage = self.blockImageLeft
            else:
                self.idleImage = self.idleImageRight
                self.punchImage = self.punchImageRight
                self.blockImage = self.blockImageRight

        # movement control. This is the only system that does not produce any bugs for this game specifically
        if self.moveRight:
            self.xChange = 3
        if self.moveLeft:
            self.xChange = -3
        if not self.moveRight and not self.moveLeft:
            self.xChange = 0

        # apply both player's movement
        self.rect.x += self.xChange
        self.rect.y += self.yChange

        # display the health bar if punnching, not blocking, and your attack is not on cooldown, display the punch image
        if self.punching and not self.blocking:
            if self.attackTimer < 10:
                self.image = self.punchImage

            # this stops punch image from displaying if it's not on cooldown
            else:
                self.punching = False

        # display blocking image
        elif self.blocking:
            self.image = self.blockImage

        self.healthBar()

        # control how fast you can punch. at 60 fps it takes 1 second
        if self.attackTimer != 0:
            self.attackTimer += 1
            if self.attackTimer == 20 - self.punchSpeed:
                self.attackTimer = 0

        # enemy collision detection
        enemyColList = pygame.sprite.spritecollide(self, [self.enemy], False)

        # uses the greater x value to determine the outcome, works generically since players can swap sides
        # Also, i use a variable to determine if i want collisions, specifcally to make the css easier to navigate
        if self.enemyCollision:
            for enemy in enemyColList:
                if self.rect.x > self.enemy.rect.x:
                    self.rect.left = self.enemy.rect.right
                else:
                    self.rect.right = self.enemy.rect.left

        # main platform collision detection, seperate from "charblocks" since they have special properties
        self.platformHitList = pygame.sprite.spritecollide(self, self.platformList, False)
        for platform in self.platformHitList:
            if self.rect.y > 0:
                self.rect.bottom = platform.rect.top
                self.yChange = 0

        # "charBlocks", blocks that change your character. collision only detected vertically
        self.charBlockHitList = pygame.sprite.spritecollide(self, self.charBlockList, False)
        for block in self.charBlockHitList:
            if self.yChange <= 0:
                self.rect.top = block.rect.bottom
                # stop vertical movement
                self.yChange = 0
                # load image associated with the block
                self.loadImages(block.name)

        # prevents user from going offscreen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > size[0]:
            self.rect.right = size[0]

        # fruit collision detection and point assignment
        fruitHitList = pygame.sprite.spritecollide(self, self.fruitsList, True)

        # assigns powerups per fruit
        for fruit in fruitHitList:
            if fruit.name == 'banana':
                self.punchSpeed += 2
            if fruit.name == 'mango':
                self.attack += 2
            if fruit.name == 'coconut':
                self.health -= 10

    # simple gravity calculator
    def calcGravity(self):

        # make sure the player is always going downwards, just like gravity
        if self.yChange == 0:
            self.yChange = 1

        # if the player is in the air, constantly counteract the vertical momentum
        else:
            self.yChange += 0.4

    # main attacking method
    def punch(self):

        # if not on cooldown, allow punching
        if self.attackTimer == 0:
            self.punching = True
            self.attackTimer += 1

        if not self.blocking and self.punching:
            # inflate the hitbox
            inflated = self.rect.inflate(30, 0)

            # if the inflation hit anything
            if inflated.colliderect(self.enemy):
                # if the enemy is blocking, reduce your damage
                if self.enemy.blocking:
                    self.enemy.health -= self.attack / 10

                # otherwise apply the correct amount of damage
                else:
                    self.enemy.health -= self.attack

    # simply sets blocking to true for animations, as the enemy deals with damage reduction
    def block(self):
        self.blocking = True

    # checks if the player has less than 0 health, and returns True if they are dead
    def deathCheck(self):
        dead = False
        if self.health <= 0:
            dead = True
        return dead

    # player jumping method
    def jump(self):

        # this line checks if the player is standing on a plattfom
        self.rect.y += 2
        self.platformHitList = pygame.sprite.spritecollide(self, self.platformList, False)
        self.rect.y -= 2

        # if you are on a platform, execute the jump
        if len(self.platformHitList) > 0:
            self.yChange = -10


class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = size[0] + 200
        self.height = size[1]
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x = -100
        self.rect.y = 500


class Fruit(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.name = random.choice(('banana', 'mango', 'coconut'))
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
                    self.changeY = 0
            # basically destroy it but im moving it away from the screen, never to be touched

    def calcGravity(self):
        if self.changeY > 0:
            self.changeY += 0.35

class charBlock(pygame.sprite.Sprite):
    def __init__(self, x, name):
        super().__init__()
        self.image = pygame.image.load(name + 'CharBlock.png').convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 230
        self.name = name

# platform and player initilization (outside loop)

playersList = pygame.sprite.Group()
mainPlatform = platform()
platformList = pygame.sprite.Group()
platformList.add(platform())
fruitsList = pygame.sprite.Group()
charBlockList = pygame.sprite.Group()

charBlockOffset = 170
ryuBlock = charBlock(170, 'ryu')
kenBlock = charBlock(370, 'ken')
obamaBlock = charBlock(570, 'obama')
charBlockList.add(ryuBlock)
charBlockList.add(kenBlock)
charBlockList.add(obamaBlock)

# handle keypresses for the main menu
def menuKeyhandler():
    scene = 0
    done = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                scene = 1
                pygame.event.clear()
    return scene, done

# handle keypresses for the character select screen
def cssKeyhandler():
    done = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                player1.moveRight = True
            if event.key == pygame.K_a:
                player1.moveLeft = True
            if event.key == pygame.K_w:
                player1.jump()
            if event.key == pygame.K_l:
                player2.moveRight = True
            if event.key == pygame.K_j:
                player2.moveLeft = True
            if event.key == pygame.K_i:
                player2.jump()
            if event.key == pygame.K_ESCAPE:
                done = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                player1.moveRight = False
            if event.key == pygame.K_a:
                player1.moveLeft = False
            if event.key == pygame.K_l:
                player2.moveRight = False
            if event.key == pygame.K_j:
                player2.moveLeft = False
    return done

# handle keypresses for the fight scene
def fightKeyhandler():
    done = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                player1.moveRight = True
            if event.key == pygame.K_a:
                player1.moveLeft = True
            if event.key == pygame.K_e:
                player1.punch()
            if event.key == pygame.K_w:
                player1.jump()
            if event.key == pygame.K_q:
                player1.block()
            if event.key == pygame.K_l:
                player2.moveRight = True
            if event.key == pygame.K_j:
                player2.moveLeft = True
            if event.key == pygame.K_u:
                player2.punch()
            if event.key == pygame.K_o:
                player2.block()
            if event.key == pygame.K_i:
                player2.jump()
            if event.key == pygame.K_ESCAPE:
                done = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                player1.moveRight = False
            if event.key == pygame.K_a:
                player1.moveLeft = False
            if event.key == pygame.K_e:
                player1.punching = False
            if event.key == pygame.K_q:
                player1.blocking = False
            if event.key == pygame.K_l:
                player2.moveRight = False
            if event.key == pygame.K_j:
                player2.moveLeft = False
            if event.key == pygame.K_u:
                player2.punching = False
            if event.key == pygame.K_o:
                player2.blocking = False
        return done


# initialize players
def init(p1Char, p2Char):
    pygame.event.clear()
    # reset player and initiialize them
    # i dont have it outside the loop since i need to do this several times anyway
    for player in playersList:
        playersList.remove(player)
    for fruit in fruitsList:
        fruitsList.remove(fruit)
    player1 = character('player1', p1Char, 200, 400)
    player2 = character('player2', p2Char, 510, 400)
    playersList.add(player1)
    playersList.add(player2)
    for player in playersList:
        for platform in platformList:
            player.platformList.add(platform)
    player1.enemy = player2
    player2.enemy = player1
    return player1, player2


roundNum = 1
scene = 0
roundDisplayTimer = 0
characterSelectCountdown = 600
winnerDisplayTimer = 0

# display score to screen
def score():
    font = pygame.font.SysFont('comicsansms', 50)
    p1PointsOnScreen = font.render(str(player1.points), True, white)
    p2PointsOnScreen = font.render(str(player2.points), True, white)
    screen.blit(p1PointsOnScreen, [330, 45])
    screen.blit(p2PointsOnScreen, [450, 45])

# display the main menu to the screen
def mainMenu():
    image = pygame.image.load('hawaiianPunchMenu.png').convert()
    screen.blit(image, [0, 0])

# display the current round
def roundScreen():
    font = pygame.font.SysFont('comicsansms', 72)
    roundMessage = font.render('Round ' + str(roundNum), False, white)
    pygame.draw.rect(screen, black, [0, 0, size[0], size[1]])
    screen.blit(roundMessage, [100, 100])

# display the character select screen
def css(characterSelectCounter):
    font = pygame.font.SysFont('comicsansms', 72)
    playersList.update()
    playersList.draw(screen)
    charBlockList.draw(screen)
    timer = font.render(str(characterSelectCounter // 60), False, black)
    chooseYourFighter = pygame.image.load('chooseYourFighter.png').convert()
    chooseYourFighter.set_colorkey(green)
    screen.blit(timer, [20, 45])
    screen.blit(chooseYourFighter, [100, 20] )

# control the fight scene
def fight(roundNum, player1, player2):
    # spawn rate
    scene = 3
    if random.randint(1, 100) == 1:
        fruit = Fruit()
        fruitsList.add(fruit)
        fruit.platformList.add(mainPlatform)
        for player in playersList:
            player.fruitsList.add(fruit)

    # draw all players
    playersList.update()
    fruitsList.update()
    fruitsList.draw(screen)
    playersList.draw(screen)
    for player in playersList:
        dead = player.deathCheck()
        if dead:
            # check if a player has died and add score acordingly
            if player == player1:
                player2.points += 1
            else:
                player1.points += 1
            # kill the player and reset the scene
            roundNum += 1
            scene = 4
    return scene, roundNum, player1, player2

# initialize the base players for the character select screen
player1, player2 = init('ryu', 'ken')

# winner scene
def showWinner():
    for player in playersList:
        if player.points == 3:
            winner = player.name
    font = pygame.font.SysFont('comicsansms', 58)
    roundMessage = font.render('The Winner is: ' + winner, False, white)
    pygame.draw.rect(screen, black, [0, 0, size[0], size[1]])
    screen.blit(roundMessage, [100, 100])

# program loop
while not done:

    # event loop
    if scene == 0:
        scene, done = menuKeyhandler()
    elif scene == 1:
        done = cssKeyhandler()
    elif scene == 3:
        done = fightKeyhandler()
    elif scene == 4:
        p1Points = player1.points
        p2Points = player2.points
        player1, player2 = init(player1.char, player2.char)
        player1.points = p1Points
        player2.points = p2Points
        pygame.event.clear()
        scene = 2

    # screen clearing code
    screen.fill(black)
    screen.blit(background, [0,0])

    # game logic
    # main menu scene
    if scene == 0:
        mainMenu()

    # character select screen
    elif scene == 1:
        characterSelectCountdown -= 1
        if characterSelectCountdown == 0:
            characterSelectCountdown = 600
            scene = 4
        for player in playersList:
            player.showHealth = False
            player.enemyCollision = False
            for charBlock in charBlockList:
                player.charBlockList.add(charBlock)
        css(characterSelectCountdown)

    # round number scene
    elif scene == 2:
        roundDisplayTimer += 1
        if roundDisplayTimer / 60 == 1:
            roundDisplayTimer = 0
            scene = 3
            pygame.event.clear()
        roundScreen()

    elif scene == 3:
        # clear the events as sometimes an event would store, making a character move infinitely
        pygame.event.clear()
        # remove the blocks from earlier and show health
        for player in playersList:
            player.showHealth = True
            for charBlock in charBlockList:
                player.charBlockList.remove(charBlock)
        # display the score
        score()
        scene, roundNum, player1, player2 = fight(roundNum, player1, player2)
        for player in playersList:
            if player.points == 3:
                scene = 5

    elif scene == 5:
        showWinner()
        winnerDisplayTimer += 1
        if winnerDisplayTimer == 600:
            winnerDisplayTimer = 0
            roundNum = 0
            # reset players points
            for player in playersList:
                player.points = 0
            # go back to css
            scene = 1

    # update display
    pygame.display.flip()

    # 60 frames
    clock.tick(60)

# close window and quit
pygame.quit()