import io
import os.path
from pathlib import Path
class WriteIfChangedFile(io.StringIO):

    def __init__(self, filename:str|Path):
        super().__init__()
        if isinstance(filename, str):
            filename = Path(filename)
        self.filename: Path = filename
        self.initialData: str = ''
        try:
            self.initialData = self.filename.read_text()
        except FileNotFoundError:
            self.initialData = ''

    def write_if_changed(self):
        pos = self.tell()
        self.seek(0)
        currentData = self.read()
        self.seek(pos)
        if self.initialData != currentData:
            self.filename.write_text(currentData)
    
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.write_if_changed()
