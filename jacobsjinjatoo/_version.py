from importlib.metadata import version

__version__ = version('jacobs-jinja-too')
__version_info__ = tuple(__version__.split('.')[:3])

