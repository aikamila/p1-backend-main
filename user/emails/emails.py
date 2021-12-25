from abc import ABC, abstractmethod


# Abstract classes for emails sent to one or more people
class Email(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def send(self):
        pass


class SingleEmail(Email):
    def __init__(self, target):
        self.target = target

    @abstractmethod
    def send(self):
        pass


class MultipleEmails(Email):
    def __init__(self, *targets):
        self.targets = targets

    @abstractmethod
    def send(self):
        pass
