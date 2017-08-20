from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from math import pi
import os

def fault (errors):
	return{
		'status': 'fault',
		'errors': errors
	}

def circle(params):
	param_name = params[0][0]
	param_value = params[0][1]
	errors = []
 
	factor = 1
	if param_name == 'radius':
		factor = pi
	elif param_name == 'diameter':
		factor = 2*pi
	else:
		errors.append('incorrect parameter name ' + param_name)

	value = 0	
	try:
		value = float(param_value)
	except:
		errors.append(param_value + ' is not float value')

	if value < 0:
		errors.append(param_name + ' could not be less then zero')
	
	if len(errors):
		return Response(json_body = fault(errors), status_code = 404)
	
	result = {
		'status' : 'success',
		'result' :{
			'shape'			: 'circle',
			param_name	: param_value,
			'area'			: factor * value
		}
	}
	return Response(json_body = result) 

def rectangle(params):
	param_name1 = params[0][0]
	param_value1 = params[0][1]
	param_name2 = params[1][0]
	param_value2 = params[1][1]
	errors = []
	
	valid_pram_names = ['width','height']

	if param_name1 == param_name2:
		errors.append(param_name1 + ' defined twice')
	if param_name1 not in valid_pram_names:
		errors.append(param_name1 + ' is not valid param name')
	if param_name2 not in valid_pram_names:
		errors.append(param_name2 + ' is not valid param name')
	
	value1 = 0
	try:
		value1 = float(param_value1)
	except:
		errors.append(param_value1 + ' is not float value')

	value2 = 0	
	try:
		value2 = float(param_value2)
	except:
		errors.append(param_value2 + ' is not float value')

	if value1 < 0:
		errors.append(param_name1 + ' could not be less then zero')	

	if value2 < 0:
		errors.append(param_name2 + ' could not be less then zero')	

	if len(errors):
		return Response(json_body = fault(errors), status_code = 404)
	result = {
		'status' : 'success',
		'result' :{
			'shape'			: 'rectangle',
			'width'			: param_value1 if param_name1 == 'width' else param_value2,
			'height'		: param_value1 if param_name1 == 'height' else param_value2,
			'area'			: value1 * value2
		}
	}
	return Response(json_body = result) 

@view_config(route_name ='common')
def common (request):
	if request.method == 'GET':
		tail = list(request.matchdict['fizzle'])
		if 0 == len(tail):
			description = open(os.path.join(os.path.dirname(__file__), 'help.txt')).read()
			return Response(content_type ='text/plain', body = description)
		
		shape = ''
		if len(tail):
			shape = tail[0]
			valid_shapes = ['circle', 'rectangle']
			if shape not in valid_shapes:
					return Response(json_body = fault([shape + ' is unknown']), status_code = 404)

		del tail[0]

		if (shape == 'circle' and len(tail) > 2) or (shape == 'rectangle' and len(tail) > 4):
			return Response(json_body = fault(['too much params for ' + shape]), status_code = 404)
		if (shape == 'circle' and len(tail) < 2) or (shape == 'rectangle' and len(tail) < 4): 
			return Response(json_body = fault(['too less params for ' + shape]), status_code = 404)

		params = list(zip(*[iter(tail)] * 2))

		if shape == 'circle':
			return circle(params)
		if shape == 'rectangle':
			return rectangle(params)
		
		return Response(json_body = fault(['something went wrong']), status_code = 500)
	else:
		return Response(json_body = fault(['method ' + request.method + ' is not implemented']),
										allow = 'GET',
										status_code = 405)

if __name__ == '__main__':
	config = Configurator()
	config.add_route('common', '/*fizzle')
	config.scan('.')
	app = config.make_wsgi_app()
	server = make_server('0.0.0.0', 8080, app)
	server.serve_forever()

