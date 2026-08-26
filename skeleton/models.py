#import db

from datetime import timezone

class Pomodoro():
    def __init__(self, user_id, start_time=None, end_time=None):
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = start_time - end_time
        self.is_completed = False

    def check(self):
        if timezone.now() >= self.end_time:
            self.is_completed = True
            return True
        return False

    def time_remaining(self):
        if self.check():
            return 0
        time = timezone.now() - self.start_time
        return time

    def __str__(self):
        return f"Pomodoro for {self.user_id} - {'Completed' if self.is_completed else 'In Progress'}"

class Assignment():
    pass

class User():
    def __init__(self, user_id):
        self.user_id = user_id
        self.pomodoros = []
        self.assignments = []

    def add_pomodoro(self, pomodoro):
        self.pomodoros.append(pomodoro)

    def add_assignment(self, assignment):
        self.assignments.append(assignment)