from typing import Dict, Any, override, Self
from copy import deepcopy
import logging

from frozendict import frozendict


def _register_generic(
    module_dict: Dict,
    module_name: str,
    module: object,
):
    assert module_name not in module_dict, logging.info(module_name, module_dict, 'defined in several script files')
    module_dict[module_name] = module


class Registry(dict):
    """A helper class for registering and managing modules

    >>> # build registry
    >>> REGISTRY_NAME = Registry(name='REGISTRY_NAME')

    >>> # registr function
    >>> @REGISTRY_NAME.register
    >>> def foo():
    >>>     pass

    >>> # registr class
    >>> @REGISTRY_NAME.register
    >>> class bar():
    >>>     pass

    >>> # fetch for class construction within builder
    >>> class_instance = REGISTRY_NAME[module_name](*args, **kwargs)

    >>> # fetch for function call
    >>> result = REGISTRY_NAME[module_name](*args, **kwargs)
    """

    def __init__(self, name: str = 'Registry', **kwargs):
        """
        Args:
            name: name of the registry
        """
        self.name = name
        super(Registry, self).__init__(**kwargs)

    def register(self, module: Any) -> Any:
        """Register module (class/functino/etc.) into this registry.

        Typically used as decorater, thus return the input module itself.

        Args:
            module: Python object that needs to be registered.

        Returns:
            Any: The registered module.
        """
        name = module.__name__
        _register_generic(self, name, module)

        return module

    @override
    def __getitem__(self, name: str) -> Any:
        if name not in self:
            raise ValueError(f'Object {name} does not exist')

        return super().__getitem__(name)

    def register_from_python_module(self, module: Any) -> Self:
        """Register all members from a Python module.

        Args:
            module: Python module to be processed.

        Returns:
            Self: The yielded registry.
        """
        self.name = module.__name__
        for k, v in module.__dict__.items():
            if k.startswith('__'):
                continue
            self[k] = v

        return self


def build_object_within_registry_from_config(
    registry: Registry,
    config: Dict[str, Any] = frozendict(),  # TODO: replace with Python built-in static mapping object
    **kwargs,
) -> Any:
    """Builder function to build object within a registry from config.

    Config should be in form of keyword arguments (dict-like).
    Support adding additional config items through kwargs.

    NOTE: kwargs will not be deep-copied.

    Args:
        registry: registry to retrieve class to be constructed.
        config: config function that provide the class name and the corresponding arguments,
            which should be arranged in the following format:

                .. code-block:: YAML

                    type: TYPENAME
                    arg1: value1
                    arg2: value2
                    ...

        **kwargs: key-word arguments to be passed to the retrieved class function.

    Return:
        Any: The built object.
    """
    config = deepcopy(config)
    config = dict(**config)
    kwargs = deepcopy(kwargs)
    config.update(kwargs)
    class_name = config.pop('type')
    obj = registry[class_name](**config)

    return obj
