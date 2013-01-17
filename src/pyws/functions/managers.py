from pyws.errors import BadFunction, FunctionNotFound,\
    FunctionAlreadyRegistered
from pyws.functions import Function

import re

class FunctionManager(object):

    def get_one(self, context, name):
        """
        Returns a function by its name if it is accessible in the context. If
        it is not accessible or does not exist, raises
        ``pyws.errors.FunctionNotFound``. Read more about context in chaper
        :doc:`context` and about functions in chapter :doc:`function`.
        """
        raise NotImplementedError('FunctionManager.get_one')

    def get_all(self, context):
        """
        Returns a list of functions accessible in the context. Read more about
        context in chaper :doc:`context` and about functiona in chapter
        :doc:`function`.
        """
        raise NotImplementedError('FunctionManager.get_all')


class FixedFunctionManager(FunctionManager):
    """
    A fixed function manager, it has a fixed set of functions.
    """

    def __init__(self, *functions):
        """
        ``functions`` is a list of functions to be registered.
        """
        self.routes = []
        for function in functions:
            self.add_function(function)

    def build_function(self, function):
        if not isinstance(function, Function):
            raise BadFunction(function)
        return function

    def add_function(self, function):
        """
        Adds the function to the list of registered functions.
        """
        route_regex = re.compile(function.route)
        name_regex  = re.compile('^' + function.name + '$')  
        for action in function.action:
            key = (route_regex,action)
            if key in zip(*self.routes)[:1]:
                raise RouteAlreadyRegistered(function.action + ":" + function.route)
            else:
                self.routes.append((key,function))
             
            key = (name_regex,action)
            if key in zip(*self.routes)[:1]:
                raise FunctionAlreadyRegistered(function.name)
            else:
                self.routes.append((key,function))

    def get_one(self, context, path):
        """
        Returns a function if it is registered, the context is ignored.
        """
        action = "GET"
        found_func = None
        for (re,act),func in self.routes:
            res = re.match(path)
            if res and action == act:
                found_func = func
                break
        if found_func:
            return found_func
        else:
            raise FunctionNotFound(path)

    def get_all(self, context):
        """
        Returns a list of registered functions, the context is ignored.
        """
        return self.functions.values()
