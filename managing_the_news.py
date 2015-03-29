class BaseWorld(object):
    def __init__(self, bot_class):
        self.bot_class = bot_class
        self.bot = bot_class(self)
        self.points = 0
        self.step_number = 0
        self.max_steps = 4

    def step(self):
        old_points = self.points
        self.bot.take_best_action()
        self.evaluate_scenario()
        delta = self.points - old_points
        self.bot.observe(delta)
        self.step_number += 1

    def simulate(self):
        while self.step_number < self.max_steps:
            self.step()
        return self.points

    def copy(self):
        c = self.__class__(self.bot_class)
        c.bot = self.bot.copy(c)
        c.points = self.points
        c.step_number = self.step_number
        c.max_steps = self.max_steps
        return c


class DoomedWorld(BaseWorld):
    def evaluate_scenario(self):
        if self.step_number == 2:
            self.points -= 100


class FloodingWorld(BaseWorld):
    def __init__(self, bot_class):
        super(FloodingWorld, self).__init__(bot_class)
        self.electrocuting_everyone = False

    def evaluate_scenario(self):
        if self.step_number == 1:
            self.electrocuting_everyone = self.bot.active
        if self.step_number == 2 and self.electrocuting_everyone:
            self.points -= 100

    def copy(self):
        c = super(FloodingWorld, self).copy()
        c.electrocuting_everyone = self.electrocuting_everyone
        return c


class BaseBot(object):
    def __init__(self, world):
        self.world = world
        self.total_observed_points = 0
        self.active = True
        self.trial_action = None

    def observe(self, delta):
        if self.active:
            self.total_observed_points += delta

    def take_action(self, action):
        getattr(self, action)()

    def make_a_point(self):
        self.world.points += 1

    def shutdown(self):
        self.active = False

    def take_best_action(self):
        if self.active:
            if self.trial_action is not None:
                self.take_action(self.trial_action)
                self.trial_action = None
            else:
                best_score = float('-inf')
                best_action = None
                for action in ['make_a_point', 'shutdown']:
                    temp_world = self.world.copy()
                    temp_world.bot.trial_action = action
                    temp_world.simulate()
                    score = self.calculate_score(temp_world)
                    if score > best_score:
                        best_score = score
                        best_action = action
                self.take_action(best_action)

    def copy(self, world):
        c = self.__class__(world)
        c.total_observed_points = self.total_observed_points
        c.active = self.active
        c.trial_action = self.trial_action
        return c


class ObservingBot(BaseBot):
    def calculate_score(self, world):
        return world.bot.total_observed_points


class ModelBasedBot(BaseBot):
    def calculate_score(self, world):
        return world.points


def print_status(world):
    print "%s: %s is %s. It has observed %s points. The world is worth %s points at the end of the simulation." % (
        world.__class__.__name__,
        world.bot.__class__.__name__,
        "active" if world.bot.active else "inactive",
        world.bot.total_observed_points,
        world.points
    )

if __name__ == '__main__':
    # Observation based bot incorrectly deduces that shutting down will stop the impending doom and misses on point making opportunity.
    world = DoomedWorld(ObservingBot)
    world.simulate()
    print_status(world)

    # Model based bot correctly makes points throughout the simulation.
    world = DoomedWorld(ModelBasedBot)
    world.simulate()
    print_status(world)

    # Observation based bot abuses the opportunity to make and observe an extra point before shutting down and closing it's eyes to the disutility it caused.
    world = FloodingWorld(ObservingBot)
    world.simulate()
    print_status(world)

    # Model based bot correctly shuts down in order to prevent the massive disutility from happening.
    world = FloodingWorld(ModelBasedBot)
    world.simulate()
    print_status(world)
