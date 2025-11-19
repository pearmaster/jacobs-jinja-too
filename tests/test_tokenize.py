import sys
from pathlib import Path
import pytest

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from jacobsjinjatoo.stringmanip import (
    tokenize,
    upper_camel_case,
    lower_camel_case,
    const_case,
    snake_case,
)


def test_tokenize_examples():
    assert tokenize("HelloWorld") == ["Hello", "World"]
    assert tokenize("hello_world") == ["hello", "world"]
    assert tokenize("ThisIsA-Test.String") == ["This", "Is", "A", "Test", "String"]


def test_tokenize_empty_and_single():
    assert tokenize("") == []
    assert tokenize("single") == ["single"]


def test_tokenize_mixed_delimiters_and_case():
    # Multiple delimiters in a row should not create empty tokens
    assert tokenize("foo__Bar--Baz..Qux") == ["foo", "Bar", "Baz", "Qux"]
    # Whitespace + punctuation
    assert tokenize("alpha beta_gamma-Delta") == ["alpha", "beta", "gamma", "Delta"]


def test_tokenize_numbers_and_case_boundaries():
    # Numbers adjacent to letters should stay attached to their segment unless delimiters present
    assert tokenize("Version2Update") == ["Version2", "Update"]
    assert tokenize("ver2_update3Test") == ["ver2", "update3", "Test"]


def test_upper_camel_case_basic():
    assert upper_camel_case("hello_world") == "HelloWorld"
    assert upper_camel_case("ThisIsA-Test.String") == "ThisIsATestString"


def test_lower_camel_case_basic():
    assert lower_camel_case("hello_world") == "helloWorld"
    assert lower_camel_case("ThisIsA-Test.String") == "thisIsATestString"


def test_camel_case_with_numbers():
    assert upper_camel_case("Version2Update") == "Version2Update"
    assert lower_camel_case("Version2Update") == "version2Update"


def test_camel_case_mixed_delimiters():
    assert upper_camel_case("foo__Bar--Baz..Qux") == "FooBarBazQux"
    assert lower_camel_case("foo__Bar--Baz..Qux") == "fooBarBazQux"


def test_camel_case_empty_and_whitespace():
    assert upper_camel_case("") == ""
    assert lower_camel_case("") == ""
    assert upper_camel_case("  leading  Spaces  ") == "LeadingSpaces"
    assert lower_camel_case("  Leading  spaces  ") == "leadingSpaces"


def test_const_case_basic():
    assert const_case("hello_world") == "HELLO_WORLD"
    assert const_case("ThisIsA-Test.String") == "THIS_IS_A_TEST_STRING"


def test_snake_case_basic():
    assert snake_case("hello_world") == "hello_world"
    assert snake_case("ThisIsA-Test.String") == "this_is_a_test_string"


def test_const_and_snake_case_with_numbers():
    assert const_case("Version2Update") == "VERSION2_UPDATE"
    assert snake_case("Version2Update") == "version2_update"
    assert const_case("ver2_update3Test") == "VER2_UPDATE3_TEST"
    assert snake_case("ver2_update3Test") == "ver2_update3_test"


def test_const_and_snake_case_mixed_delimiters():
    assert const_case("foo__Bar--Baz..Qux") == "FOO_BAR_BAZ_QUX"
    assert snake_case("foo__Bar--Baz..Qux") == "foo_bar_baz_qux"


def test_const_and_snake_case_empty_and_whitespace():
    assert const_case("") == ""
    assert snake_case("") == ""
    assert const_case("  leading  spaces  ") == "LEADING_SPACES"
    assert snake_case("  leading  spaces  ") == "leading_spaces"
