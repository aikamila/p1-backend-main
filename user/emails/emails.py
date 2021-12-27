from abc import ABC, abstractmethod


# Abstract classes for emails
class Email(ABC):
    def __init__(self, target):
        self.target = target

    @abstractmethod
    def send(self):
        pass


# class SingleEmail(Email):
#     def __init__(self, target):
#         self.target = target
#
#     @abstractmethod
#     def send(self):
#         pass
#
#
# class MultipleEmails(Email):
#     def __init__(self, *targets):
#         self.targets = targets
#
#     @abstractmethod
#     def send(self):
#         pass


class EmailDispatcher:
    def __init__(self, email: Email):
        self.email = email

    def send(self):
        self.email.send()
