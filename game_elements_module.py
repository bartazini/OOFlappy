import pygame as p
import sys
import random
from game_pack import setting as set

class Game:
    def __init__(self):
        self.gravity = set.gravity
        p.init()
        self.screen = p.display.set_mode((576, 1024))
        self.score = set.score
        self.high_score = set.high_score
        self.game_state = set.game_state
        self.clock = p.time.Clock()
        self.env = Enviroment()
        self.bird = Bird()

    def runGame(self):
        while 1:
            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()
                if event.type == p.KEYDOWN:
                    if event.key == p.K_SPACE:
                        self.bird.bird_movement = 0
                        self.bird.bird_movement -= 10
                if event.type == p.KEYDOWN and self.game_state == False:
                    self.game_state = True
                    self.score = set.score
                    self.env.pipes.clear()
                    self.bird.bird_rect.center = (100, 512)
                if event.type == self.env.spawn_pipe:
                    self.env.pipes.extend(self.env.createPipe())
                if event.type == self.bird.BIRDFLAP:
                    if self.bird.bird_index < 2:
                        self.bird.bird_index += 1
                    else:
                        self.bird.bird_index = 0
                    self.bird.bird_surface, self.bird.bird_rect = self.bird.birdAnimation(self.bird.bird_frames)
            ##BackGround
            self.env.drawBg(self.screen)
            ##Floor
            self.env.drawFloor(self.screen)
            if self.game_state:
                ##Pipes
                self.env.pipes = self.env.movePipes(self.env.pipes)
                self.env.drawPipes(self.env.pipes, self.screen)
                ##FuckingBird
                self.bird.bird_movement = self.bird.drawBird(self.screen, self.gravity, self.bird.bird_movement,)
                self.game_state = self.bird.checkCollision(self.env.pipes)
                ##Score
                self.score += 0.01
                self.env.scoreDisplay('game_active', self.screen, self.score, self.high_score)
            else:

                self.screen.blit(self.env.game_over_surface, self.env.game_over_rect)
                ##Score display
                if self.score > self.high_score:
                    self.high_score = self.score
                self.env.scoreDisplay('game_over', self.screen,self.score ,self.high_score)




            p.display.update()
            self.clock.tick(set.MAX_FPS)

class Enviroment:
    def __init__(self):
        self.bg_surface = p.transform.scale2x(p.image.load('sprites/background-day.png').convert())
        self.floor_surface = p.transform.scale2x(p.image.load('sprites/base.png').convert())
        self.pipe_surface = p.transform.scale2x(p.image.load('sprites/pipe-green.png'))
        self.game_over_surface = p.transform.scale2x(p.image.load('sprites/message.png').convert_alpha())
        self.game_over_rect = self.game_over_surface.get_rect(center = (288, 512))
        self.game_font = p.font.Font('04B_19__.TTF', 40)
        self.pipes = []
        self.pipe_height = [400, 600, 800]
        self.spawn_pipe = p.USEREVENT
        p.time.set_timer(self.spawn_pipe, 1200)

    def drawBg(self, screen):
        screen.blit(self.bg_surface, (0, 0))

    def drawFloor(self, screen):
        screen.blit(self.floor_surface, (set.floorXpos, 900))
        screen.blit(self.floor_surface, (set.floorXpos + 576, 900))
        set.floorXpos -= 1
        if set.floorXpos == -576:
            set.floorXpos = 0

    def createPipe(self):
        random_pipe = random.choice(self.pipe_height)
        bottom_pipe = self.pipe_surface.get_rect(midtop = (700, random_pipe))
        top_pipe = self.pipe_surface.get_rect(midbottom = (700, random_pipe - 300))
        return bottom_pipe, top_pipe

    def drawPipes(self, pipes, screen):
        for pipe in pipes:
            if pipe.bottom >= 1024:
                screen.blit(self.pipe_surface, pipe)
            else:
                screen.blit(p.transform.flip(self.pipe_surface, False, True), pipe)

    def movePipes(self, pipes):
        for pipe in pipes:
            pipe.centerx -= 5
        return pipes

    def scoreDisplay(self, game_state, screen, score, high_score):
        if game_state == 'game_active':
            score_surface = self.game_font.render(str(int(score)), True, (255, 255, 255))
            score_rect = score_surface.get_rect(center = (288, 100))
            screen.blit(score_surface, score_rect)
        if game_state == 'game_over':
            score_surface = self.game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center = (288, 100))
            screen.blit(score_surface, score_rect)

            high_score_surface = self.game_font.render(f'High score: {int(high_score)}', True, (255, 255, 255))
            high_score_rect = high_score_surface.get_rect(center = (288, 850))
            screen.blit(high_score_surface, high_score_rect)


class Bird:
    def __init__(self):
        self.bird_movement = set.bird_movement
        self.BIRDFLAP = p.USEREVENT + 1
        p.time.set_timer(self.BIRDFLAP, 200)
        self.bird_dflap = p.transform.scale2x(p.image.load('sprites/yellowbird-downflap.png').convert_alpha())
        self.bird_mflap = p.transform.scale2x(p.image.load('sprites/yellowbird-midflap.png').convert_alpha())
        self.bird_uflap = p.transform.scale2x(p.image.load('sprites/yellowbird-upflap.png').convert_alpha())
        self.bird_frames = [self.bird_dflap, self.bird_mflap, self.bird_uflap]
        self.bird_index = 0
        self.bird_surface = self.bird_frames[self.bird_index]
        self.bird_rect = self.bird_surface.get_rect(center = (100, 512))

    def drawBird(self, screen, gravity, bird_movement):
        bird_movement += gravity
        self.bird_rect.centery += int(bird_movement)
        rotated = self.rotateBird(self.bird_surface)
        screen.blit(rotated, self.bird_rect)
        return bird_movement

    def rotateBird(self, bird_surface):
        new_bird = p.transform.rotozoom(bird_surface, -self.bird_movement*3, 1)
        return new_bird

    def birdAnimation(self, bird_frames):
        new_surface = bird_frames[self.bird_index]
        new_rect = new_surface.get_rect(center = (100, self.bird_rect.centery))
        return new_surface, new_rect

    def checkCollision(self, pipes):
        for pipe in pipes:
            if self.bird_rect.colliderect(pipe):
                return False
        if self.bird_rect.top <= -100 or self.bird_rect.bottom >= 900:
            return False
        return True


