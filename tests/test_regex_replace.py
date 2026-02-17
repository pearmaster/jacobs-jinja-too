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


def test_regex_replace_basic():
    """Test basic string replacement."""
    templator = Templator()
    result = templator.render_string("{{ 'hello world' | regex_replace('world', 'universe') }}")
    assert result == "hello universe"


def test_regex_replace_pattern():
    """Test regex pattern replacement."""
    templator = Templator()
    result = templator.render_string("{{ 'test123test456' | regex_replace('\\d+', 'NUM') }}")
    assert result == "testNUMtestNUM"


def test_regex_replace_email_domain():
    """Test replacing email domain."""
    templator = Templator()
    result = templator.render_string("{{ 'user@example.com' | regex_replace('@.*', '@newdomain.com') }}")
    assert result == "user@newdomain.com"


def test_regex_replace_multiple_spaces():
    """Test replacing multiple spaces with single space."""
    templator = Templator()
    result = templator.render_string("{{ 'hello    world   test' | regex_replace('\\s+', ' ') }}")
    assert result == "hello world test"


def test_regex_replace_backreference():
    """Test using backreferences in replacement."""
    templator = Templator()
    # Swap first and last name - use raw string for replacement
    result = templator.render_string(
        "{{ text | regex_replace(pattern, replacement) }}",
        text='John Doe',
        pattern=r'(\w+) (\w+)',
        replacement=r'\2, \1'
    )
    assert result == "Doe, John"


def test_regex_replace_case_insensitive():
    """Test case-insensitive replacement using inline flag."""
    templator = Templator()
    result = templator.render_string("{{ 'Hello HELLO hello' | regex_replace('(?i)hello', 'Hi') }}")
    assert result == "Hi Hi Hi"


def test_regex_replace_remove_html_tags():
    """Test removing HTML tags."""
    templator = Templator()
    result = templator.render_string("{{ '<p>Hello <b>world</b></p>' | regex_replace('<[^>]+>', '') }}")
    assert result == "Hello world"


def test_regex_replace_no_match():
    """Test when pattern doesn't match anything."""
    templator = Templator()
    result = templator.render_string("{{ 'hello world' | regex_replace('xyz', 'abc') }}")
    assert result == "hello world"


def test_regex_replace_empty_string():
    """Test replacing with empty string (deletion)."""
    templator = Templator()
    result = templator.render_string("{{ 'hello123world456' | regex_replace('\\d+', '') }}")
    assert result == "helloworld"


def test_regex_replace_special_characters():
    """Test escaping special regex characters."""
    templator = Templator()
    result = templator.render_string("{{ 'price: $100' | regex_replace('\\$\\d+', '$200') }}")
    assert result == "price: $200"


def test_regex_replace_in_template_file():
    """Test regex_replace filter in a template file."""
    templator = Templator(output_dir=test_output_dir)
    
    # Create a test template
    template_dir = test_output_dir / "templates"
    template_dir.mkdir(exist_ok=True)
    template_file = template_dir / "regex_test.txt.jinja2"
    template_file.write_text("{{ text | regex_replace(pattern, replacement) }}")
    
    templator.add_template_dir(template_dir)
    
    output_path = templator.render_template(
        "regex_test.txt.jinja2",
        output_name="regex_output.txt",
        text="Version 1.2.3",
        pattern=r"\d+\.\d+\.\d+",
        replacement="2.0.0"
    )
    
    assert output_path.exists()
    assert output_path.read_text() == "Version 2.0.0"


def test_regex_replace_multiline():
    """Test multiline replacement."""
    templator = Templator()
    text = "line1\\nline2\\nline3"
    result = templator.render_string("{{ text | regex_replace('^line', 'row') }}", text=text)
    # Without multiline flag, only first line is replaced
    assert result == "row1\\nline2\\nline3"


def test_regex_replace_with_variable():
    """Test using variables for pattern and replacement."""
    templator = Templator()
    result = templator.render_string(
        "{{ text | regex_replace(search, replace) }}",
        text="foo bar baz",
        search="bar",
        replace="qux"
    )
    assert result == "foo qux baz"
