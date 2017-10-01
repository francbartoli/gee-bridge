#!/usr/bin/env python

from pyswagger import App
import yaml


app = App.create('http://localhost:9000/api/v1/swagger?format=openapi')
obj = app.dump()
with open('./swagger/schema.yaml', 'w') as w:
     w.write(yaml.safe_dump(obj))
