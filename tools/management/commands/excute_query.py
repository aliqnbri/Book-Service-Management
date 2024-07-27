from django.core.management.base import BaseCommand
from tools.Context_manager import ContextFileManger  # Update with your actual app name and path
from pathlib import Path


class Command(BaseCommand):
    help = 'Execute SQL queries from a file.'

    def add_arguments(self, parser):
        parser.add_argument('filepath', help='The path to the SQL file.')
        parser.add_argument('method', help='The Method to Call on FileManger' ,default='read')

    def handle(self, **kwargs):
        filepath = Path(kwargs['filepath'])
        method_name = kwargs['method']
        file_manager = ContextFileManger(filepath)

        if hasattr(file_manager, method_name):
            getattr(file_manager, method_name)()
        else:
            self.stderr.write(f"FileManager does not have a method named '{method_name}'")