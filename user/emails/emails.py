from abc import ABC, abstractmethod


# Abstract class for emails
class Email(ABC):
    def __init__(self, target):
        self.target = target

    @abstractmethod
    def send(self):
        pass


class EmailDispatcher:
    def __init__(self, email: Email):
        self.email = email

    def send(self):
        self.email.send()
