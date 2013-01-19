from datetime import date, datetime

from functools import partial

from pyws.errors import BadRequest
from pyws.functions.args.types.complex import List
from pyws.response import Response
from pyws.utils import json,Route
from pyws.protocols.base import Protocol

__all__ = ('RestProtocol', 'JsonProtocol', )


class DateIso8601Encoder(json.JSONEncoder):
    # JSON Serializer with datetime support
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


create_response = partial(Response, content_type='application/json')
create_error_response = partial(create_response, status=Response.STATUS_ERROR)


class RestProtocol(Protocol):

    name = 'rest'

    def get_function(self, request):
        return Route(request.tail,request.METHOD)

    def get_arguments(self, request, function):
        result = {}
        name_dict = {}
        index_dict = {}
        if isinstance(function.name,Route):
            m = function.name.regex.match(Route(request.tail,request.METHOD))
            name_dict = m.groupdict()
            index_dict = dict((i,value) for (i,value)
                                in dict(enumerate(m.groups(),1)).items() # numbered dict of all groups
                                if not m.span(i) in map(m.span,name_dict.keys()))
        path_params = dict(name_dict.items() + index_dict.items())

        for index,field in enumerate(function.args.fields):
            value = request.GET.get(field.name,None)
            value = path_params.get(index     ,value)
            value = path_params.get(field.name,value)
            if not type(value) in (list,tuple):
                value = (value,)

            if issubclass(field.type, List):
                result[field.name] = value
            elif value != (None,):
                result[field.name] = value[0]
        return result

    def get_response(self, result, name, return_type):
        return create_response(
            json.dumps({'result': result}, cls=DateIso8601Encoder))

    def get_error_response(self, error):
        return create_error_response(
            json.dumps({'error': self.get_error(error)}))


class JsonProtocol(RestProtocol):

    name = 'json'

    def get_arguments(self, request, function):
        try:
            return json.loads(request.text)
        except ValueError:
            raise BadRequest()
