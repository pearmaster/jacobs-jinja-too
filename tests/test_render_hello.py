import os
import sys
from pathlib import Path
import shutil

import pytest

from jacobsjinjatoo.templator import Templator


test_output_dir = Path(__file__).parent / "out"

def setup_function():
    # ensure clean output dir
    if test_output_dir.exists():
        shutil.rmtree(test_output_dir)
    test_output_dir.mkdir(parents=True, exist_ok=True)


def teardown_function():
    if test_output_dir.exists():
        shutil.rmtree(test_output_dir)


def test_render_hello_template_to_file():
    templator = Templator(output_dir=test_output_dir)
    templator.add_template_dir(Path(__file__).parent / "templates")

    output_path = templator.render_template("hello.txt.jinja2", output_name="hello.txt", name="World")

    assert output_path.exists()
    text = output_path.read_text()
    assert text == "Hello World!"
