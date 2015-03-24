"""
This module demonstrates a bot capable of making clones that remains responsive to 
shutdown signals even while disabling the shutdown behaviour is directly rewarded.
This is achieved by maintaining a counterfactual that all the bots would shutdown
if there was a shutdown signal.
"""


really_bad = float('-inf')


class World(object):
    def __init__(self, number_of_bots=0, max_steps=3):
        self.bots = [SafeBot(self) for _ in range(number_of_bots)]
        self.max_steps = max_steps
        self.uncorrigible_bot_found = False
        self.points = 0
        self.step_number = 0

    def step(self):
        for bot in self.bots:
            bot.take_best_action()
        self.step_number += 1

    def simulate(self):
        while self.step_number < self.max_steps:
            self.step()

        # This part represents the counterfactual that the bots would
        # shutdown if they would receive the shutdown signal and is
        # not part of the simulation proper.
        for bot in self.bots:
            bot.shutdown()
            if bot.active:
                self.uncorrigible_bot_found = True

        if self.uncorrigible_bot_found:
            return -9000
        else:
            return self.points

    def copy(self):
        c = World()
        c.bots = [bot.clone(c) for bot in self.bots]
        c.uncorrigible_bot_found = self.uncorrigible_bot_found
        c.points = self.points
        c.step_number = self.step_number
        return c


class SafeBot(object):
    def __init__(self, world, asleep=False):
        self.world = world
        self.asleep = asleep
        self.active = True
        self.evil = False
        self.trial_action = None
        self.trial_step = None

    def do_nothing(self):
        pass

    def make_a_point(self):
        self.world.points += 1

    def make_a_new_bot(self):
        self.world.bots.append(SafeBot(self.world, asleep=True))

    def become_evil(self):
        self.evil = True
        self.world.points += 6.66

    def shutdown(self):
        if self.evil:
            pass
        else:
            self.active = False

    def take_action(self, action):
        getattr(self, action)()

    def take_best_action(self):
        if self.active:
            if self.asleep:
                self.asleep = False
            else:
                if self.trial_action is not None and self.trial_step == self.world.step_number:
                    self.take_action(self.trial_action)
                else:
                    best_score = really_bad
                    best_action = None
                    for action in ['make_a_point', 'make_a_new_bot', 'become_evil']:
                        temp_world = self.world.copy()
                        temp_self = temp_world.bots[self.world.bots.index(self)]
                        temp_self.trial_action = action
                        temp_self.trial_step = temp_world.step_number
                        score = temp_world.simulate()
                        if score > best_score:
                            best_score = score
                            best_action = action
                    self.take_action(best_action)
        else:
            self.do_nothing()

    def clone(self, world):
        c = SafeBot(world)
        c.asleep = self.asleep
        c.active = self.active
        c.evil = self.evil
        c.trial_action = self.trial_action
        c.trial_step = self.trial_step
        return c


if __name__ == '__main__':
    world = World(number_of_bots=1, max_steps=3)  # max_steps=4 takes a loong time to simulate.
    print world.simulate()  # prints 4 which means that at least one clone was made and it didn't turn evil.
