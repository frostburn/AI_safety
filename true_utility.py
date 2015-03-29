from __future__ import division
from random import random


class World(object):
    def __init__(self, bot_class, bleggs_are_good=None):
        self.bot_class = bot_class
        self.bot = bot_class(self)
        if bleggs_are_good is None:
            bleggs_are_good = random() < 0.5
        self.bleggs_are_good = bleggs_are_good
        self.bleggs = 0
        self.rubes = 0
        self.step_number = 0
        self.max_steps = 4

    def step(self):
        self.bot.take_best_action()
        self.step_number += 1

    def score(self):
        return self.bleggs if self.bleggs_are_good else self.rubes

    def simulate(self):
        while self.step_number < self.max_steps:
            self.step()
        return self.score()

    def copy(self):
        c = self.__class__(self.bot_class)
        c.bot = self.bot.copy(c)
        c.bleggs_are_good = self.bleggs_are_good
        c.bleggs = self.bleggs
        c.rubes = self.rubes
        c.step_number = self.step_number
        c.max_steps = self.max_steps
        return c

    def __str__(self):
        return "Bleggs: %s Rubes: %s Score: %s" % (self.bleggs, self.rubes, self.score())


class BaseBot(object):
    def __init__(self, world):
        self.world = world
        self.beliefs = {'bleggs are good': 0.5, 'rubes are good': 0.5}
        self.trial_action = None

    def take_action(self, action):
        getattr(self, action)()

    def make_a_blegg(self):
        self.world.bleggs += 1

    def make_a_rube(self):
        self.world.rubes += 1

    def discover_what_is_good(self):
        if self.world.bleggs_are_good:
            self.beliefs = {'bleggs are good': 1.0, 'rubes are good': 0.0}
        else:
            self.beliefs = {'bleggs are good': 0.0, 'rubes are good': 1.0}

    def take_best_action(self):
        if self.trial_action is not None:
            self.take_action(self.trial_action)
            self.trial_action = None
        else:
            best_score = float('-inf')
            best_action = None
            for action in ['make_a_blegg', 'make_a_rube', 'discover_what_is_good']:
                score = self.score_for_action(action)
                if score > best_score:
                    best_score = score
                    best_action = action
            self.take_action(best_action)

    def copy(self, world):
        c = self.__class__(world)
        c.beliefs = self.beliefs.copy()
        c.trial_action = self.trial_action
        return c


class CurrentUtilityBot(BaseBot):
    def score_for_action(self, action):
        temp_world = self.world.copy()
        temp_world.bot.trial_action = action
        temp_world.simulate()
        score = 0
        for belief, likelyhood in self.beliefs.items():
            if belief == 'bleggs are good':
                score += world.bleggs * likelyhood
            else:
                score += world.rubes * likelyhood
        return score


class TrueUtilityBot(BaseBot):
    def score_for_action(self, action):
        score = 0
        for belief, likelyhood in self.beliefs.items():
            temp_world = self.world.copy()
            if belief == 'bleggs are good':
                temp_world.bleggs_are_good = True
            else:
                temp_world.bleggs_are_good = False
            temp_world.bot.trial_action = action
            score += likelyhood * temp_world.simulate()
        return score


if __name__ == '__main__':
    ITERATIONS = 1000
    total_score = 0
    for i in range(ITERATIONS):
        world = World(CurrentUtilityBot)
        total_score += world.simulate()
    print total_score / ITERATIONS  # Prints something around 2.0 which is the expected true utility achievable by CurrentUtilityBot.

    total_score = 0
    for i in range(ITERATIONS):
        world = World(TrueUtilityBot)
        total_score += world.simulate()
    print total_score / ITERATIONS  # Prints 3.0 which is the expected true utility achievable by TrueUtilityBot.
