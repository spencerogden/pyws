"""
A simple function registration mechanism.
"""

from pyws.errors import ConfigurationError
from pyws.functions import NativeFunctionAdapter
from pyws.server import SERVERS

def register(*args, **kwargs):
    """
    Creates a registrator that, being called with a function as the only
    argument, wraps a function with ``pyws.functions.NativeFunctionAdapter``
    and registers it to the server. Arguments are exactly the same as for
    ``pyws.functions.NativeFunctionAdapter`` except that you can pass
    an additional keyword argument ``to`` designating the name of the server
    which the function must be registered to:

    >>> from pyws.server import Server
    >>> server = Server()
    >>> from pyws.functions.register import register
    >>> @register()
    ... def say_hello(name):
    ...     return 'Hello, %s' % name
    >>> server.get_functions(context=None)[0].name
    'say_hello'

    >>> another_server = Server(dict(NAME='another_server'))
    >>> @register(to='another_server', return_type=int, args=(int, 0))
    ... def gimme_more(x):
    ...     return x * 2
    >>> another_server.get_functions(context=None)[0].name
    'gimme_more'

    """
    if args and callable(args[0]):
        raise ConfigurationError(
            'You might have tried to decorate a function directly with '
            '@register which is not supported, use @register(...) instead')
    def registrator(origin):
        server = SERVERS.get(kwargs.pop('to',None),SERVERS.default)
        names = kwargs.pop('name',*args[:1]) 
        if isinstance(names,str):
            names = [names]
        for n in names:
            server.add_function(
                NativeFunctionAdapter(origin,n, *args[1:], **kwargs))
        return origin
    return registrator
