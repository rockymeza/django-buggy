transitions = set()


class TransitionError(Exception):
    pass


@staticmethod
def CREATOR(bug):
    return bug.comments.earliest().user


class State(object):
    assign_to = None
    requires = []

    def __init__(self, bug):
        self.bug = bug

    def move_to(self, target_state, **kwargs):
        if not self.can_move_to(target_state):
            raise TransitionError("%s can't move to %s." % (self, target_state))
        state = target_state(self.bug)
        # kwargs passed in directly have priority over the kwargs
        # suggested by the target state.
        move_kwargs = {}
        move_kwargs.update(state.get_enter_kwargs())
        move_kwargs.update(kwargs)
        state.validate(move_kwargs)
        self.bug.comments.create(**move_kwargs)

    @property
    def possibilities(self):
        return [transition[1] for transition in transitions
                if transition[0] is type(self)]

    def can_move_to(self, target_state):
        return target_state in self.possibilities

    def validate(self, kwargs):
        for attr in self.requires:
            if attr not in kwargs:
                raise TransitionError("Requirements not met")

    def get_enter_kwargs(self):
        kwargs = {}
        if self.assign_to:
            kwargs['assigned_to'] = self.assign_to(self.bug)
        return kwargs


class Embryo(State):
    pass


class New(State):
    requires = ['title']

transitions.add((Embryo, New))


class Resolved(State):
    assign_to = CREATOR

transitions.add((New, Resolved))


class Verified(State):
    pass

transitions.add((Resolved, Verified))
