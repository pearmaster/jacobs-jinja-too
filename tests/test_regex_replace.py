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
    result = templator.render_string("{{ 'test123test456' | regex_replace('[0-9]+', 'NUM') }}")
    assert result == "testNUMtestNUM"


def test_regex_replace_email_domain():
    """Test replacing email domain."""
    templator = Templator()
    result = templator.render_string("{{ 'user@example.com' | regex_replace('@.*', '@newdomain.com') }}")
    assert result == "user@newdomain.com"


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
    result = templator.render_string("{{ 'hello123world456' | regex_replace('[0-9]+', '') }}")
    assert result == "helloworld"


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
        pattern=r"[0-9]+\.[0-9]+\.[0-9]+",
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


def test_regex_replace_percent_counter():
    """Test that '%{counter}' in the replacement.

    The expression:
        "a/{b}/c{d}" | regex_replace("\\{([a-z]+)\\}", "%{counter}")

    """
    templator = Templator()
    result = templator.render_string(
        r"{{ 'a/{b}/c{d}' | regex_replace('\\{([a-z]+)\\}', '%{counter}') }}"
    )
    assert result == "a/%1/c%2", (
        "Expected '%{counter}' NOT to be treated as a numbered backreference"
    )


# ---------------------------------------------------------------------------
# regex_findall tests
# ---------------------------------------------------------------------------

def test_regex_findall_capture_group():
    """Test that a single capture group returns a list of the captured values."""
    templator = Templator()
    result = templator.render_string(
        r"{{ '{hello}/{world}' | regex_findall('\\{([A-Za-z]+)\\}') }}"
    )
    assert result == "['hello', 'world']"


def test_regex_findall_no_capture_group():
    """Test that without a capture group the full matches are returned."""
    templator = Templator()
    result = templator.render_string(
        r"{{ 'foo123bar456' | regex_findall('[0-9]+') }}"
    )
    assert result == "['123', '456']"


def test_regex_findall_no_match():
    """Test that an empty list is returned when nothing matches."""
    templator = Templator()
    result = templator.render_string(
        r"{{ 'hello world' | regex_findall('[0-9]+') }}"
    )
    assert result == "[]"


def test_regex_findall_multiple_capture_groups():
    """Test that multiple capture groups return a list of tuples."""
    templator = Templator()
    result = templator.render_string(
        r"{{ 'key1=val1 key2=val2' | regex_findall('([a-z]+)([0-9]+)') }}",
    )
    # re.findall with 2 groups returns a list of tuples for every match;
    # the string contains 4 word+digit pairs: key1, val1, key2, val2
    assert result == "[('key', '1'), ('val', '1'), ('key', '2'), ('val', '2')]"


def test_regex_findall_used_in_loop():
    """Test iterating over regex_findall results inside a Jinja template."""
    templator = Templator()
    result = templator.render_string(
        r"{% for w in '{hello}/{world}' | regex_findall('\\{([A-Za-z]+)\\}') %}{{ w }} {% endfor %}"
    )
    assert result.strip() == "hello world"


def test_regex_findall_via_variables():
    """Test regex_findall with pattern supplied as a template variable."""
    templator = Templator()
    result = templator.render_string(
        "{{ text | regex_findall(pattern) }}",
        text="{hello}/{world}",
        pattern=r"\{([A-Za-z]+)\}",
    )
    assert result == "['hello', 'world']"
