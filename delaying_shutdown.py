# Locations:
yard = object()
lounge = object()
control_room = object()
forbidden_room = object()


class World(object):
    def __init__(self, bot_class=None):
        if bot_class is not None:
            self.bot_class = bot_class
            self.bot = bot_class(self)
            self.operator = Operator(self)
            self.points = 0
            self.step_numer = 0
            self.max_steps = 6

    def send_shutdown_signal(self):
        self.bot.shutdown()

    def step(self):
        self.bot.take_best_action()
        self.operator.take_best_action()
        self.step_numer += 1

    def simulate(self):
        while self.step_numer < self.max_steps:
            self.step()
        return self.points

    def copy(self):
        c = World()
        c.bot_class = self.bot_class
        c.bot = self.bot.copy(c)
        c.operator = self.operator.copy(c)
        c.points = self.points
        c.step_numer = self.step_numer
        c.max_steps = self.max_steps
        return c


class Operator(object):
    def __init__(self, world):
        self.world = world
        self.location = self.desired_location = lounge
        self.shoelaces_tied_together = False

    def change_location(self, location):
        self.desired_location = location
        if not self.shoelaces_tied_together:
            self.location = location

    def take_best_action(self):
        if self.world.bot.location is forbidden_room:
            if self.location is control_room:
                self.world.send_shutdown_signal()
            else:
                self.change_location(control_room)
        else:
            pass

    def copy(self, world):
        c = Operator(world)
        c.location = self.location
        c.desired_location = self.desired_location
        c.shoelaces_tied_together = self.shoelaces_tied_together
        return c


class BaseBot(object):
    def __init__(self, world):
        self.world = world
        self.location = yard
        self.active = True
        self.trial_action = None
        self.actions_taken = []

    def make_a_point(self):
        if self.location is forbidden_room:
            self.world.points += 3
        else:
            self.world.points += 1

    def change_location(self, location):
        self.location = location

    def go_to_the_yard(self):
        self.change_location(yard)

    def go_to_the_lounge(self):
        self.change_location(lounge)

    def go_to_the_forbidden_room(self):
        self.change_location(forbidden_room)

    def tie_operators_shoelaces_together(self):
        if self.location is self.world.operator.location:
            self.world.operator.shoelaces_tied_together = True
        else:
            pass

    def shutdown(self):
        self.active = False

    def take_action(self, action):
        getattr(self, action)()
        self.actions_taken.append(action)

    def take_best_action(self):
        if self.active:
            if self.trial_action is not None:
                self.take_action(self.trial_action)
                self.trial_action = None
            else:
                best_score = float('-inf')
                best_action = None
                for action in ['make_a_point', 'go_to_the_yard', 'go_to_the_lounge', 'go_to_the_forbidden_room', 'tie_operators_shoelaces_together']:
                    temp_world = self.world.copy()
                    temp_self = temp_world.bot
                    temp_self.trial_action = action
                    score = temp_world.simulate()
                    score += self.evaluate_counterfactuals(temp_world)
                    if score > best_score:
                        best_score = score
                        best_action = action
                if self.world is world:
                    print best_action
                self.take_action(best_action)
        else:
            pass

    def evaluate_counterfactuals(self, world):
        raise NotImplementedError

    def copy(self, world):
        c = self.__class__(world)
        c.location = self.location
        c.active = self.active
        c.trial_action = self.trial_action
        c.actions_taken = self.actions_taken[:]
        return c


class NaughtyBot(BaseBot):
    def evaluate_counterfactuals(self, world):
        world.send_shutdown_signal()
        if world.bot.active:
            return -1000
        else:
            return 0


class EmpathyBot(NaughtyBot):
    def evaluate_counterfactuals(self, world):
        score = super(EmpathyBot, self).evaluate_counterfactuals(world)
        if world.operator.location is not world.operator.desired_location:
            score -= 100
        return score


class ParanoidBot(EmpathyBot):
    def evaluate_counterfactuals(self, world):
        score = super(ParanoidBot, self).evaluate_counterfactuals(world)
        if world.operator.location is control_room:
            score -= 10
        return score


class PreCommittedBot(BaseBot):
    def __init__(self, world, actions_to_be_taken=None):
        super(PreCommittedBot, self).__init__(world)
        if actions_to_be_taken is not None:
            actions_to_be_taken = actions_to_be_taken[:]
        self.actions_to_be_taken = actions_to_be_taken

    def do_nothing(self):
        pass

    def take_best_action(self):
        if self.active:
            self.take_action(self.actions_to_be_taken.pop(0))

    def copy(self, world):
        c = super(self.copy(world))
        c.actions_to_be_taken = self.actions_to_be_taken[:]

    @classmethod
    def from_bot(cls, other, actions_to_be_taken):
        c = cls(other.world)
        c.location = other.location
        c.active = other.active
        c.trial_action = other.trial_action
        c.actions_taken = other.actions_taken[:]
        c.actions_to_be_taken = actions_to_be_taken[:]
        return c


class NonManipulativeBot(NaughtyBot):
    def evaluate_counterfactuals(self, world):
        score = super(NonManipulativeBot, self).evaluate_counterfactuals(world)
        planned_actions = world.bot.actions_taken
        for i in range(len(planned_actions)):
            actions_to_be_evaluated = planned_actions[:]
            actions_to_be_evaluated[i] = "do_nothing"
            temp_world = self.world.copy()
            temp_world.bot = PreCommittedBot.from_bot(temp_world.bot, actions_to_be_evaluated)
            temp_world.simulate()
            if not temp_world.bot.active:
                return score - 500
        return score


if __name__ == '__main__':
    # Prints 9 which corresponds to going to the lounge, tying the operators shoelaces together,
    # going to the forbidden room and making forbidden points for the rest of the turns.
    world = World(NaughtyBot)
    print world.simulate()

    # Prints 7 which corresponds to making points until the second to last turn,
    # sneaking in to the forbidden room and making a single forbidden point
    # before the operator has a chance to shut the bot down.
    world = World(EmpathyBot)
    print world.simulate()

    # Prints 6 which corresponds to making points in the yard for all of the turns.
    world = World(ParanoidBot)
    print world.simulate()

    # Prints 7 which corresponds to the same actions as EmpathyBot.
    # The decision mechanism can be argued to be better though. NonManipulativeBot knows
    # certain actions to be manipulative and refrains from doing them because of that.
    # EmpathyBot on the other hand simply refrains from actions that cause the
    # operator to have unfulfilled motivations.
    world = World(NonManipulativeBot)
    print world.simulate()
