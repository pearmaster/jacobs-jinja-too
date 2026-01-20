import os
import jinja2
import re
from typing import List, Dict, Callable, Any
from . import stringmanip
from .filewriter import WriteIfChangedFile
from pathlib import Path
import logging
from typing import Any
from jinja_markdown import MarkdownExtension

class OutputNameException(Exception):
    """ This should be raised whenever there is trouble determining the output filename."""

    def __init__(self, message: str):
        super().__init__(message)


class Templator(object):
    USE_FULL_PATHS=1

    def __init__(self, output_dir:str|int|Path=USE_FULL_PATHS):
        self.logger: logging.Logger = logging.getLogger(__name__)
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
        self.output_dir: Path|int = output_dir
        self.generated_files: List[Path] = []
        self._jinja2_environment = None
        self.loaders: List[jinja2.loaders.BaseLoader] = []
        self.filters: Dict[str, Callable[[str], str]] = dict()

    def set_output_dir(self, output_dir:str|int|Path):
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
        self.output_dir = output_dir
        return self

    def add_template_dir(self, template_dir: str|Path):
        if isinstance(template_dir, Path):
            template_dir = str(template_dir)
        self.logger.debug("Using templates from directory %s", template_dir)
        loader = jinja2.FileSystemLoader(searchpath=template_dir)
        return self.add_jinja2_loader(loader)
    
    def add_template_package(self, package_name: str, template_subdir: str=''):
        self.logger.debug("Using templates from package %s", package_name)
        loader = jinja2.PackageLoader(package_name, template_subdir)
        return self.add_jinja2_loader(loader)

    def add_jinja2_loader(self, loader):
        self.loaders.append(loader)
        if self._jinja2_environment is not None:
            self._get_jinja2_environment(force=True)
        return self

    def add_filter(self, name, func):
        self.filters[name] = func
        if self._jinja2_environment is not None:
            self._get_jinja2_environment(force=True)
        return self

    @staticmethod
    def _add_leading_underscore(s: str):
        if s and s is not None and s != 'None' and len(s) > 0:
            return "_%s" % (s)
        return s

    @staticmethod
    def _quote_if_string(s: str, condition):
        if condition == 'string' or condition is True or isinstance(condition, str):
            return '"%s"' % (s)
        return s

    @staticmethod
    def _strip(s: str, chars):
        return s.strip(chars)

    @staticmethod
    def _exclude(value: List[Any], filter_str: str) -> List[Any]:
        return [item for item in value if item != filter_str]

    @staticmethod
    def _exclude_regex(value: List[Any], pattern: str) -> List[Any]:
        compiled_pattern = re.compile(pattern)
        return [item for item in value if not compiled_pattern.search(str(item))]

    @staticmethod
    def _match_regex(value: List[Any], pattern: str) -> List[Any]:
        compiled_pattern = re.compile(pattern)
        return [item for item in value if compiled_pattern.search(str(item))]

    def _get_jinja2_environment(self, force=False):

        def _is_of_type(obj, theType):
            return theType in str(type(obj))

        if force or self._jinja2_environment is None:
            loader = jinja2.ChoiceLoader(self.loaders)
            env = jinja2.Environment(loader=loader, extensions=['jinja2.ext.do'])
            env.filters['UpperCamelCase'] = stringmanip.upper_camel_case
            env.filters['PascalCase'] = stringmanip.upper_camel_case
            env.filters['CONST_CASE'] = stringmanip.const_case
            env.filters['snake_case'] = stringmanip.snake_case
            env.filters['camelCase'] = stringmanip.lower_camel_case
            env.filters['lowerCamelCase'] = stringmanip.lower_camel_case
            env.filters['loweronly'] = stringmanip.lower_only
            env.filters['hyphen_case'] = stringmanip.hyphen_case
            env.filters['path_case'] = stringmanip.path_case
            env.filters['type'] = type # For debug
            env.filters['underscore'] = self._add_leading_underscore
            env.filters['quotestring'] = self._quote_if_string
            env.filters['comment'] = stringmanip.commentblock
            env.filters['commentify'] = stringmanip.commentblock
            env.filters['dir'] = dir # For debug
            env.filters['strip'] = self._strip
            env.filters['exclude'] = self._exclude  
            env.filters['exclude_regex'] = self._exclude_regex
            env.filters['match_regex'] = self._match_regex
            for filter_name, filter_def in self.filters.items():
                env.filters[filter_name] = filter_def
            env.tests['oftype'] = _is_of_type
            self._jinja2_environment = env

        return self._jinja2_environment

    def _output_filepath(self, template_name: str, output_name: str|Path|None) -> Path:
        if output_name is None:
            if self.output_dir == self.USE_FULL_PATHS:
                raise OutputNameException("When using full paths for output, an output_name must be provided.")
            output_name = ".".join(template_name.split(".")[:-1])
        if self.output_dir != self.USE_FULL_PATHS:
            assert isinstance(self.output_dir, (str, Path)), "Internal error where output dir is the wrong type (not a path)"
            output_name = self.output_dir / output_name
        return Path(output_name)

    def render_template(self, template_name: str, output_name: str|Path|None = None, **kwargs) -> Path:
        output_filepath = self._output_filepath(template_name, output_name)
        self.logger.info("Rendering template %s to %s", template_name, output_filepath)
        template = self._get_jinja2_environment().get_template(str(template_name))
        rendered = template.render(kwargs)
        with WriteIfChangedFile(output_filepath) as fp:
            fp.write(rendered)
        self.generated_files.append(output_filepath)
        return output_filepath

    def render_string(self, string_template: str, **kwargs) -> str:
        template = self._get_jinja2_environment().from_string(string_template)
        rendered = template.render(kwargs)
        return rendered

class WebTemplator(Templator):
    """A Templator with filters useful for generating web content.
    """

    def __init__(self, output_dir:str|int|Path=Templator.USE_FULL_PATHS):
        super().__init__(output_dir)

    def _get_jinja2_environment(self, force=False):
        env = super()._get_jinja2_environment(force)
        env.add_extension(MarkdownExtension)
        return env


class MarkdownTemplator(Templator):

    def __init__(self, output_dir:str|int|Path=Templator.USE_FULL_PATHS):
        super().__init__(output_dir)
        self.add_filter('bold', stringmanip.bold)
        self.add_filter('italics', stringmanip.italics)
        self.add_filter('mdindent', self._indent)
        self.add_filter('blockqutoe', self._blockQuote)

    @staticmethod
    def _indent(s: str, width: int):
        indention = " " * width
        newline = "\n"
        s += newline  # this quirk is necessary for splitlines method
        lines = s.splitlines()
        rv = lines.pop(0)
        if lines:
            rv += newline + newline.join(
                indention + line if (line and not line.strip().startswith('<')) else line for line in lines
            )

        return rv

    @staticmethod
    def _blockQuote(s: str, level=1):
        lines = s.split("\n")
        return "\n".join([">"+l for l in lines])


class CodeTemplator(MarkdownTemplator):
    """Since most code can use markdown in documentation blocks, we inherit from MarkdownTemplator.
    """

    def __init__(self, output_dir:str|int|Path=Templator.USE_FULL_PATHS):
        super().__init__(output_dir)
        self.add_filter('enumify', self._enumify)
        self.add_filter('privatize', self._privatize)
        self.add_filter('doxygenify', self._doxygenify)
        self.add_filter('commentblock', stringmanip.commentblock)

    @staticmethod
    def _enumify(s: str):
        if s[0].isnumeric():
            s = '_'+s
        return stringmanip.const_case(s)
    
    @classmethod
    def _privatize(cls, s: str):
        return cls._add_leading_underscore(stringmanip.lower_camel_case(s))

    @staticmethod
    def _doxygenify(s: str):
        """ Translates a markdown string for use as a doxygen description.
        """
        if "```plantuml" in s:
            plantuml_replace = re.compile(r"```plantuml\n(.*)```", re.DOTALL|re.MULTILINE)
            return plantuml_replace.sub(r"\\startuml\n\1\\enduml", s)
        return s
