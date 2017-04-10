#/usr/bin/python

import pygame
import random
import math
from copy import deepcopy

GAME_WIDTH = 1000
GAME_HEIGHT = 500;

color = {
    'white' : (255, 255, 255),
    'black' : (0, 0, 0),
    'red'   : (255, 0, 0),
    'blue'  : (0, 0, 255),
    'purple': (255, 0, 255),
    'orange': (255, 127, 0)
}

class Game():
    def __init__(self):
        self.manager = NeuralNetwork_manager()
        self.ball = Ball()
        self.l_current = 0
        self.r_current = 0
        self.paddles = [Paddle(True), Paddle(False)]
        self.lscore = 0
        self.rscore = 0
        self.color = color['black']
        self.scorefont = pygame.font.SysFont("monospace", 15)
        self.scorecolor = color['white']
        self.reset(True)

    def reset(self, l_won):
        self.ball.reset()
        for paddle in self.paddles:
            paddle.reset()
        if self.lscore == 3 or self.rscore == 3:
            self.lscore = 0
            self.rscore = 0
            if l_won:
                self.manager.fitness[self.l_current] += 1
                self.manager.fitness[self.r_current] -= 2
                self.r_current = self.l_current
                while self.r_current == self.l_current:
                    self.r_current = random.randint(0, len(self.manager.brains)-1)
            else:
                self.manager.fitness[self.l_current] -= 2
                self.manager.fitness[self.r_current] += 1
                self.l_current = self.r_current
                while self.l_current == self.r_current:
                    self.l_current = random.randint(0, len(self.manager.brains)-1)

            self.manager.breed(self.manager.brains, self.manager.fitness)

    def update(self):
        self.ball.update(self, self.paddles)
        l_inp = [
            float(abs(self.paddles[0].x-self.ball.x))/GAME_WIDTH,
            float((self.paddles[0].y+self.paddles[0].height/2)-self.ball.y)/GAME_HEIGHT]
        r_inp = [
            float(abs(self.paddles[1].x-self.ball.x))/GAME_WIDTH,
            float((self.paddles[1].y+self.paddles[1].height/2)-self.ball.y)/GAME_HEIGHT]

        l_forward = self.manager.brains[self.l_current].forward(l_inp)[0]
        r_forward = self.manager.brains[self.r_current].forward(r_inp)[0]
        if l_forward > 0.5:
            self.paddles[0].move(True)
        else:
            self.paddles[0].move(False)

        if r_forward > 0.5:
            self.paddles[1].move(True)
        else:
            self.paddles[1].move(False)

    def draw(self, screen):
        screen.fill(self.color)
        self.ball.draw(screen)
        for paddle in self.paddles:
            paddle.draw(screen)

        score1 = self.scorefont.render("SCORE: "+str(self.lscore), 1, self.scorecolor)
        score2 = self.scorefont.render("SCORE: "+str(self.rscore), 1, self.scorecolor)
        lfitness = self.scorefont.render("CFIT: "+str(self.manager.fitness[self.l_current]), 1,
                                         self.scorecolor)
        rfitness = self.scorefont.render("CFIT: "+str(self.manager.fitness[self.r_current]), 1,
                                         self.scorecolor)
        num_breeds = self.scorefont.render("NUM BREEDS: "+str(self.manager.num_breeds), 1,
                                           self.scorecolor)
        screen.blit(score1, (50, 20))
        screen.blit(score2, (GAME_WIDTH - 100, 20))
        screen.blit(lfitness, (50, 40))
        screen.blit(rfitness, (GAME_WIDTH - 100, 40))
        screen.blit(num_breeds, (GAME_WIDTH/2 - 50, 20))

        self.manager.brains[self.l_current].draw(screen, 70, 100)
        self.manager.brains[self.r_current].draw(screen, GAME_WIDTH - 150, 100)

class Ball():
    def __init__(self):
        self.velocity = 5
        self.radius = 5
        self.color = color['white']
        self.reset()

    def reset(self):
        self.x = GAME_WIDTH / 2
        self.y = GAME_HEIGHT / 2
        self.vx = self.velocity if random.random() < .5 else -self.velocity
        self.vy = self.velocity if random.random() < .5 else -self.velocity

    def update(self, game, paddles):
        self.x += self.vx
        self.y += self.vy

        if self.x < 0:
            game.rscore += 1
            game.reset(False)

        elif self.x > GAME_WIDTH:
            game.lscore += 1
            game.reset(True)

        if self.y < 0:
            self.y = self.radius
            self.vy = random.randint(self.velocity/2, self.velocity)

        elif self.y > GAME_HEIGHT:
            self.y = GAME_HEIGHT
            self.vy = -random.randint(self.velocity/2, self.velocity)

        for paddle in paddles:
            if (paddle.left and
                (self.x < paddle.x + paddle.width and
                 self.y - self.radius >= paddle.y and
                 self.y <= paddle.y + paddle.height)):
                self.vx = random.randint(self.velocity/2, self.velocity)
            elif (not paddle.left and
                (self.x + self.radius >= paddle.x and
                 self.y - self.radius >= paddle.y and
                 self.y <= paddle.y + paddle.height)):
                self.vx = -random.randint(self.velocity/2, self.velocity)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, [self.x, self.y], self.radius)

class Paddle():
    def __init__(self, left):
        self.velocity = 10
        self.width = 15
        self.height = 75
        self.left = left
        if left:
            self.x = 0
            self.color = color['red']
        else:
            self.x = GAME_WIDTH - self.width
            self.color = color['orange']
        self.y = GAME_HEIGHT / 2 - self.height / 2
        self.reset()

    def reset(self):
        self.y = GAME_HEIGHT / 2 - self.height / 2

    def move(self, up):
        if (up):
            self.y -= self.velocity
            if self.y < 0:
                self.y = 0
        else:
            self.y += self.velocity
            if self.y + self.height > GAME_HEIGHT:
                self.y = GAME_HEIGHT - self.height

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, [self.x, self.y, self.width, self.height])

############################################################

class NeuralNetwork():
    def __init__(self, weights=None):
        self.num_in = 2
        self.num_hid = 3
        self.num_out = 1
        if weights is None:
            weights = []
            weights.append(
                [[random.random() - random.random() for _ in range(self.num_hid)]
                 for __ in range(self.num_in)])
            weights.append(
                [[random.random() - random.random()] for _ in range(self.num_out)
                 for __ in range(self.num_hid)])
        self.weights = weights

    def forward(self, inp):
        assert len(inp) == self.num_in
        hidden = [0 for _ in range(self.num_hid)]
        for h_index in range(len(hidden)):
            for i_index, i_item in enumerate(inp):
                hidden[h_index] += i_item * self.weights[0][i_index][h_index]
            hidden[h_index] = self._sigmoid(hidden[h_index])

        output = [0 for _ in range(self.num_out)]
        for o_index in range(len(output)):
            for h_index, h_item in enumerate(hidden):
                output[o_index] += h_item * self.weights[1][h_index][o_index]
            output[o_index] = self._sigmoid(output[o_index])

        return output

    def _sigmoid(self, x):
        try:
            return 1/(1+pow(math.e, -x))
        except:
            return 0.5

    def draw(self, screen, x, y):
        radius = 10
        buf = 5
        for i in range(self.num_in):
            pygame.draw.circle(screen, color['white'],
                               (x, y + i*2*radius + buf), radius, 1)
            for h in range(self.num_hid):
                pygame.draw.line(screen,
                                 self._draw_get_weight_color(self.weights[0][i][h]),
                                (x, y + i*2*radius + buf),
                                (x + 4*radius, y + h*2*radius + buf), 2)
        for h in range(self.num_hid):
            pygame.draw.circle(screen, color['white'],
                              (x + 4*radius, y + h*2*radius + buf), radius, 1)
            for o in range(self.num_out):
                pygame.draw.line(screen,
                                 self._draw_get_weight_color(self.weights[1][h][o]),
                                (x + 4*radius, y + h*2*radius + buf),
                                (x + 8*radius, y + o*2*radius + buf), 2)
        for o in range(self.num_out):
            pygame.draw.circle(screen, color['white'],
                               (x + 8*radius, y + o*2*radius + buf), radius, 1)

    def _draw_get_weight_color(self, weight):
        if weight < 0:
            return color['blue']
        return color['red']

class NeuralNetwork_manager():
    def __init__(self):
        self.num_brains = 10
        self.num_breeds = 0
        self.brains = [NeuralNetwork() for _ in range(self.num_brains)]
        self.fitness = [0 for _ in range(self.num_brains)]

    def breed(self, population, fitness):
        self.num_breeds += 1
        p1_index = 0
        p2_index = 1
        c_index = 2
        for i in range(len(population)):
            if fitness[i] > fitness[p1_index]:
                p1_index = i
            elif fitness[i] > fitness[p2_index]:
                p2_index = i
            elif fitness[i] < fitness[c_index]:
                c_index = i
        p1 = population[p1_index]
        p2 = population[p2_index]
        child_weights = []
        fitness[c_index] = 0
        for slce in range(len(p1.weights)):
            layer = []
            for arr in range(len(p1.weights[slce])):
                layer.append([])
                for ele in range(len(p1.weights[slce][arr])):
                    rng = random.random()
                    if rng > .66:
                        layer[arr].append(p1.weights[slce][arr][ele])
                    elif rng > .33:
                        layer[arr].append(p2.weights[slce][arr][ele])
                    else:
                        layer[arr].append(.5*(p1.weights[slce][arr][ele]+
                                                   p2.weights[slce][arr][ele]))
                    if rng <= .06:
                        layer[arr][ele] = random.random()-random.random()
            child_weights.append(layer)
        population[c_index] = NeuralNetwork(child_weights)

    def print_info(self):
        print self.fitness
        print self.num_breeds

##############################################################

def main():
    pygame.init()
    screen = pygame.display.set_mode([GAME_WIDTH, GAME_HEIGHT])
    clock = pygame.time.Clock()
    max_ticks_per_second = 60

    game = Game()

    done = False
    while not done:
        clock.tick(max_ticks_per_second)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                max_ticks_per_second = 99999999
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                max_ticks_per_second = 60
        game.update()
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()

main()


