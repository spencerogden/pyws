import pyws
from werkzeug.serving import run_simple
from werkzeug.routing import NotFound
from werkzeug.wsgi import DispatcherMiddleware

from pyws.functions.register import register
from pyws.adapters._wsgi import create_application
from pyws.functions.args.types import ListOf
from pyws.utils import Route

import logging
logger = logging.getLogger('pyws')
ch = logging.StreamHandler()
logger.addHandler(ch)

pywsserver = pyws.server.Server(
{'PROTOCOLS':(
pyws.protocols.rest.RestProtocol(),
pyws.protocols.rest.JsonProtocol(),
pyws.protocols.soap.SoapProtocol(
            service_name="SimpleApp",
            tns="http://www.example.com/",
            location="http://localhost:8000/simple/soap/"
            ),
)}
)

items = []

@register(['create_item',Route(r'^Item$',"PUT")],args=(str,))
def create_item(value):
    print "in create item with value",value
    items.append(value)
    print items
    return len(items)-1
    
@register(['get_item',Route(r'^Item/(?P<id>\d*)$',"GET")],args=(int,str))
def get_item(id):
    print "in get item with id",id
    return items[id]
    
@register(['get_all_items',Route(r'^Item/?$',"GET")],return_type=ListOf(str))
def get_all_items():
    print "in get all"
    return items
    
@register(['update_item',Route(r'^Item/(?P<id>\d+)$',"POST")],args=(int,str))
def update_item(id,value):
    print "in update item"
    items[id] = value
    
@register(['delete_item',Route(r'^Item/(?P<id>\d+)$',"DELETE")],args=(int,))
def delete_item(id):
    print "in delete item"
    del items[id]

app = create_application(pywsserver, '')

urls = DispatcherMiddleware(NotFound(), {
'/simple': app,
})

run_simple('0.0.0.0',8000, urls,use_debugger=True,use_reloader=True)