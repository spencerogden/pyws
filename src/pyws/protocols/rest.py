from datetime import date, datetime

from functools import partial
import re

from pyws.errors import BadRequest
from pyws.functions.args.types.complex import List
from pyws.response import Response
from pyws.utils import json
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
        return request.tail

    def get_arguments(self, request, function):
        # Parameters in the path take precedence over values in the query string
        result = {}
        
        res = function.route_regex.match(request.tail)
        name_dict = res.groupdict()

        # span tuples are unique identifiers of groups
        # index_dict should be all groups not in name_dict
        index_dict = dict(enumerate(res.groups(),1))
        index_dict = dict((i,value) for (i,value) 
                        in dict(enumerate(res.groups(),1)) # dict of all groups
                        if not res.span(i) in map(res.span,name_dict.keys()))

        found_parameters = dict(name_dict.items() + index_dict.items())
        # found_parameters should have all matched groups, keyed either by
        # name or position

        for index,field in enumerate(function.args.fields):
            value_query_named = request.GET.get(field.name,None)
            value_path_index = found_parameters.get(index,value_query_named)
            value_path_named = found_parameters.get(field.name,value_path_index)
            # Find the parameter in various locations, named in the path takes precedent
            
            if issubclass(field.type, List):
                result[field.name] = value
            elif value:
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
        # Parse args from path and query string, overwrite with JSON arguments if found
        args = super(JsonProtocol,self).get_arguments()
        if request.text:
            try:
                args.update(json.loads(request.text))
            except ValueError:
                raise BadRequest()
        return args