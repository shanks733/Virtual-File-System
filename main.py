import json , os
import sys
from File_System import FileSystem


fs = FileSystem()
while True:
    command = input(f'{fs.current_directory}$ ')
    fs.execute_command(command)