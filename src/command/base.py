from abc import ABC, abstractmethod
import argparse

class BaseCommand(ABC):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.add_arguments(self.parser)

    def add_arguments(self, parser):
        """
        Override this method to add arguments to the parser.
        """
        pass

    @abstractmethod
    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this method.
        """
        pass

    def run(self, argv):
        args = self.parser.parse_args(argv)
        self.handle(**vars(args))
