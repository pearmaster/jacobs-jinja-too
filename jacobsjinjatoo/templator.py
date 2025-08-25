import os
import jinja2
import stringcase
import re
from typing import Union, List, Dict, Callable
from . import stringmanip
from .filewriter import WriteIfChangedFile

class Templator(object):
    USE_FULL_PATHS=1

    def __init__(self, output_dir:Union[str, int]=USE_FULL_PATHS):
        self.output_dir = output_dir
        self.generated_files: List[str] = []
        self._jinja2_environment = None
        self.loaders: List[jinja2.loaders.BaseLoader] = []
        self.filters: Dict[str, Callable[[str], str]] = dict()

    def set_output_dir(self, output_dir:Union[str,int]):
        self.output_dir = output_dir
        return self

    def add_template_dir(self, template_dir):
        loader = jinja2.FileSystemLoader(searchpath=template_dir)
        return self.add_jinja2_loader(loader)
    
    def add_template_package(self, package_name):
        loader = jinja2.PackageLoader(package_name, '')
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

    def _get_jinja2_environment(self, force=False):

        def _is_of_type(obj, theType):
            return theType in str(type(obj))

        if force or self._jinja2_environment is None:
            loader = jinja2.ChoiceLoader(self.loaders)
            env = jinja2.Environment(loader=loader, extensions=['jinja2.ext.do'])
            env.filters['UpperCamelCase'] = stringmanip.upper_camel_case
            env.filters['PascalCase'] = stringmanip.upper_camel_case
            env.filters['CONST_CASE'] = lambda s : stringcase.constcase(str(s)).replace('__', '_')
            env.filters['snake_case'] = stringcase.snakecase
            env.filters['camelCase'] = stringmanip.lower_camel_case
            env.filters['lowerCamelCase'] = stringmanip.lower_camel_case
            env.filters['type'] = type # For debug
            env.filters['underscore'] = self._add_leading_underscore
            env.filters['quotestring'] = self._quote_if_string
            env.filters['dir'] = dir # For debug
            env.filters['strip'] = self._strip
            for filter_name, filter_def in self.filters.items():
                env.filters[filter_name] = filter_def
            env.tests['oftype'] = _is_of_type
            self._jinja2_environment = env

        return self._jinja2_environment

    def render_template(self, template_name, output_name = None, **kwargs):
        if isinstance(self.output_dir, str):
            output_filename = output_name or ".".join(template_name.split(".")[:-1])
            output_file = os.path.join(self.output_dir, output_filename)
        else:
            output_filename = os.path.basename(output_name)
            output_file = output_name
        template = self._get_jinja2_environment().get_template(template_name)
        rendered = template.render(kwargs)
        with WriteIfChangedFile(output_file) as fp:
            fp.write(rendered)
        self.generated_files.append(output_filename)
        return output_filename


class MarkdownTemplator(Templator):

    def __init__(self, output_dir:Union[str,int]=Templator.USE_FULL_PATHS):
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
        lines = str.split("\n")
        return "\n".join([">"+l for l in lines])


class CodeTemplator(MarkdownTemplator):
    """Since most code can use markdown in documentation blocks, we inherit from MarkdownTemplator.
    """

    def __init__(self, output_dir:Union[str,int]=Templator.USE_FULL_PATHS):
        super().__init__(output_dir)
        self.add_filter('enumify', self._enumify)
        self.add_filter('privatize', self._privatize)
        self.add_filter('doxygenify', self._doxygenify)

    @staticmethod
    def _enumify(s: str):
        if s[0].isnumeric():
            s = '_'+s
        return stringcase.constcase(s)
    
    @classmethod
    def _privatize(cls, s: str):
        return cls._add_leading_underscore(stringcase.camelcase(s))

    @staticmethod
    def _doxygenify(s: str):
        """ Translates a markdown string for use as a doxygen description.
        """
        if "```plantuml" in s:
            plantuml_replace = re.compile(r"```plantuml\n(.*)```", re.DOTALL|re.MULTILINE)
            return plantuml_replace.sub(r"\\startuml\n\1\\enduml", s)
        return s
