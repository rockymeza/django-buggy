from django.test import TestCase
from django.contrib.auth import get_user_model

from buggy.models import Bug
from buggy.statemachine import State, TransitionError, transitions

User = get_user_model()


def refresh(obj):
    return obj.__class__._default_manager.get(pk=obj.pk)


class BuggyManualGettersTest(TestCase):
    def setUp(self):
        self.bug = Bug.objects.create()
        self.user = User.objects.create_user(
            'test@example.com',
            'password',
        )

    def test_get_title(self):
        self.bug.comments.create(
            user=self.user,
            title='Title 1',
        )
        self.assertEqual(refresh(self.bug).title, 'Title 1')

        self.bug.comments.create(
            user=self.user,
        )
        self.assertEqual(refresh(self.bug).title, 'Title 1')

        self.bug.comments.create(
            user=self.user,
            title='Title 2',
        )
        self.assertEqual(refresh(self.bug).title, 'Title 2')

    def test_get_assigned_to(self):
        user2 = User.objects.create_user(
            'test2@example.com',
            'password',
        )

        self.bug.comments.create(
            user=self.user,
        )
        self.assertEqual(refresh(self.bug).assigned_to, None)
        self.bug.comments.create(
            user=self.user,
            assigned_to=user2,
        )
        self.assertEqual(refresh(self.bug).assigned_to, user2)

        self.bug.comments.create(
            user=self.user,
        )
        self.assertEqual(refresh(self.bug).assigned_to, user2)

        self.bug.comments.create(
            user=self.user,
            assigned_to=self.user
        )
        self.assertEqual(refresh(self.bug).assigned_to, self.user)


class TwoUserTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            'test1@example.com',
            'password',
        )
        self.user2 = User.objects.create_user(
            'test2@example.com',
            'password',
        )


class StateMachineTest(TwoUserTestCase):
    def setUp(self):
        super(StateMachineTest, self).setUp()

        self.bug = Bug.objects.create()
        self.bug.comments.create(
            user=self.user1,
            assigned_to=self.user2,
        )

    def test_cant_move_to_self(self):
        class CurrentState(State):
            pass

        state = CurrentState(self.bug)

        with self.assertRaises(TransitionError):
            state.move_to(CurrentState, user=self.user1)

    def test_assign_to(self):
        @staticmethod
        def get_user1(bug):
            return self.user1

        class AssignToState(State):
            assign_to = get_user1

        state = State(self.bug)
        transitions.add((State, AssignToState))
        state.move_to(AssignToState, user=self.user2)

        bug = refresh(self.bug)
        self.assertEqual(bug.assigned_to, self.user1)

    def test_requires(self):
        class RequiresTitle(State):
            requires = ['title']

        state = State(self.bug)
        transitions.add((State, RequiresTitle))
        with self.assertRaises(TransitionError):
            state.move_to(RequiresTitle, user=self.user2)

        state.move_to(RequiresTitle, user=self.user2, title='title')
