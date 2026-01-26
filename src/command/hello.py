from command.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("name", nargs="?", default="World", help="Who to greet")

    def handle(self, name, **options):
        print(f"Hello, {name}!")
