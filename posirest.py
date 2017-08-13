from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from math import pi
import os

def single(request, shape, param):
	errors = []
	value_name = 'side'
	value = 0
	area = 0

	try:
		value = float(param)
	except:
		errors.append(param + ' is not valid float value')

	if shape == 'circle':
		multiplier  = 1 if 'd' in request.GET else 2
		value_name  = 'diameter' if 'd' in request.GET else 'radius'
		if len(errors) == 0 and value>=0:
			area = multiplier*pi*value

	elif shape == 'rectangle':
		shape = 'square'
		if len(errors) == 0 and value>=0:
			area = value*value

	else:
		errors.append('unknown shape: '+ shape)

	if value<0:
		errors.append(value_name + ' value can not be less then zero')

	if len(errors):
		return fault(errors)

	return {
		'status' : 'success',
		'result' :{
			'shape'			: shape,
			value_name	: value,
			'area'			: area
		}
	}
 
def double (request, shape, param1, param2):
	errors = []
	width = 0
	height = 0

	try:
		width = float(param1)
	except:
		errors.append(param1+ ' is not valid float value of width')

	if width <0:
		errors.append('width can not be less then zero')

	try:
		height = float(param2)
	except:
		errors.append(param2+ ' is not valid float value of height')

	if height <0:
		errors.append('height can not be less then zero')

	if shape != 'rectangle':
		errors.append('unknown shape: '+ shape)

	if len(errors):
		return fault(errors)

	return{
		'status':'success',
		'result':{
			'shape'		: 'rectangle',
			'width'		: width,
			'height'	: height,
			'area'		: height*width
		}
	}

def fault (errors):
	return{
		'status': 'fault',
		'errors': errors
	}

@view_config(route_name='common', renderer='json')
def  common (request):
	if request.method == 'GET':
		tail = request.matchdict['tail']

		if   0 == len(tail):
			discription = open(os.path.join(os.path.dirname(__file__), 'help.txt')).read()
			return Response(content_type ='text/plain', body = discription)

		shape =''
		param1 = ''
		param2 = ''

		if 0 < len(tail):
			shape = tail[0]
			if shape != 'circle' and shape != 'rectangle':
				return fault(['shape: '+ shape+ ' is not valid'])

		if 1 == len(tail):
			return fault(['too less parameters for shape: '+ shape])

		if 2 == len(tail):
			param1 = tail[1]
			return single(request, shape, param1)

		if 3 == len(tail):
			param1 = tail[1]
			param2 = tail[2]
			if shape == 'rectangle':
				return double(request, shape, param1, param2)
			else:
				return fault(['too mach params for shape '+ shape])

		if 3 < len(tail):
			return fault(['too mach params for shape '+ shape])

	else:
		return fault([request.method+' method is not implemented'])

if __name__ == '__main__':
	config = Configurator()
	config.add_static_view(name='static', path='positest:static')
	config.add_route('common', '/*tail')
	config.scan('.')
	app = config.make_wsgi_app()
	server = make_server('0.0.0.0', 8080, app)
	server.serve_forever()

