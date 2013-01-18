import suds
import requests
import json

client = suds.client.Client('http://localhost:8000/simple/soap/wsdl')

r = requests.put('http://localhost:8000/simple/rest/Item?value=test%20string')
id = json.loads(r.text)['result']
print "Create item with REST and got id",id

r = requests.get('http://localhost:8000/simple/rest/Item/'+str(id))
text = json.loads(r.text)['result']
print "Got item with REST with value:",text

text = client.service.get_item(id)
print "Got item with SOAP with value:",text

id = client.service.create_item("another test string")
print "Create item with SOAP and got id",id

r = requests.get('http://localhost:8000/simple/rest/Item/')
strings = json.loads(r.text)['result']
print "Got all items with REST",strings

strings = client.service.get_all_items()
print "Got all items with SOAP",strings.item

r = requests.post('http://localhost:8000/simple/rest/Item/'+str(id)+"?value=updated%20string")
strings = client.service.get_all_items()
print "Got all items with SOAP",strings.item

client.service.delete_item(id)

r = requests.get('http://localhost:8000/simple/rest/Item/')
strings = json.loads(r.text)['result']
print "Got all items with REST",strings