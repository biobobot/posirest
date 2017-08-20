import json, getopt, os, sys
import http.client as client

class Tester:
	
	V = [
		'0',
		'2', 
		'2.2',
		'%32',
		'87486635647389820987352773527\
6693645281209321738712893721897381\
2637346522334456678809876543564765\
8729849090910939898748663564738982\
0987352773527192663645281209321738\
7128937218973812637346537216398217\
3891237612378621837721983712892683\
5487126382173892173812678321645126\
3821763981263872156387126938621753\
8746387731283789126378523487126387\
2138912678362349879823748237487632\
8947328947672386493274893264782637\
4771788276354738291918836361387129\
8739281739827138972139872198321983\
7129873987439874436587346587671263\
871263871263871254653754192223456',
	'2e+2'
	]
	I = [
		'2,2',
		'-2',
		'string',
		'@&:()%$~?^'
	]
	CV = [
		'radius',
		'diameter'
	]
	IP	=	[
		'invalid',
		'another_one'
	]
	RV = [
		'width',
		'height'
	]
	M =	[
		'POST',
		'DELETE',
		'TRACE',
		'OPTIONS'
	]		
	DELIMITER = '------------------------------------'
	total_tests_count = 0
	failed_tests_count = 0
	failed_uris = []	
	log_file = None	

	@staticmethod
	def uri(elements):
		uri = ''
		for e in elements:
			uri += ('/' + e)
		return uri

	@staticmethod
	def request(host, method, uri):
		connection = client.HTTPConnection(host)
		connection.request(method, uri)
		response = connection.getresponse()
		connection.close()
		return response
 
	@staticmethod
	def fill_json(response,result):
		body_bytes = response.read()
		body_string = body_bytes.decode('utf-8')			
		try:
			result['response'] = json.loads(body_string) 
			return True
		except:
			result['response'] = body_string
			return False

	@staticmethod	
	def check_code(response, result, params):	
		if 'HTTP_status' not in params:
			result['errors'].append('test params does not contains HTTP_status')
			return False
		if params['HTTP_status'] != response.status:
			result['errors'].append('waiting code ' + str(params['HTTP_status']) + ' but service returns ' + str( response.status))				
			return False
		return True

	@staticmethod
	def check_is_json(response, result, params):
		if not Tester.fill_json(response,result):
			result['errors'].append('response is not json object')
			return False
		return True

	@staticmethod	
	def check_is_valid_json(response, result, params):
		if not Tester.check_is_json(response, result, params):
			return False
		if 'status' not in result['response']:
			result['errors'].append('response does not contains status field')
			return False
		if 'result' not in result['response'] and 'errors' not in result['response'] :
			result['errors'].append('response does not contains result or error field')
			return False
		return True
	
	@staticmethod
	def check_json_status(response, result, params):
		if not Tester.check_is_valid_json(response, result, params):
			return False
		if 'JSON_status' not in params:
			result['errors'].append('test params does not contains JSON_status')
			return False	
		if result['response']['status'] != params['JSON_status']:
			result['errors'].append('response is not '+ params['JSON_status'] + ' status')
			return False	
		return True	
					
	@staticmethod
	def check_shape(response, result, params):
		if 'shape' not in params:
			result['errors'].append('test params does not contains shape field')
			return False
		if 'shape' not in result['response']['result']:
			result['errors'].append('response does not contains shape field')
			return False
		if result['response']['result']['shape'] != params['shape']:
			result['errors'].append('waiting shape ' + str(params['shape']) + ' but service returns ' + str(result['response']['result']['shape']))				
			return False
		return True	
		
	@staticmethod
	def check_response(response, result, params):
		if not Tester.check_code(response, result, params):
			return False
		if not Tester.check_json_status(response, result, params):
			return False
		if params['JSON_status'] == 'success':
			if not Tester.check_shape(response, result, params): 
				return False
		return True

	@staticmethod	
	def make_test(host, method, uri, params, checker):
		result = {}
		result['errors'] = []
		Tester.total_tests_count += 1	
		try:
			response = Tester.request(host, method, uri)	
			if checker and checker(response, result, params):
				result['status'] = 'ok'
			else:
				result['status'] = 'fail'	
				Tester.failed_uris.append(uri)
				Tester.failed_tests_count += 1	
		except:
			result['status'] = 'fail'
			result['errors'].append('host is not available')	
			Tester.failed_tests_count += 1	
			
		
		Tester.notify(Tester.DELIMITER)
		Tester.notify(' %-5s ! %s: %s' % (result['status'], method, (uri[1:70] + '...') if len(uri) > 70 else uri))
		Tester.notify(Tester.DELIMITER)
		for e in result['errors']:
			Tester.notify('^   ' + e)	
		if 'response' in result and 'errors' in result['response']:	
			for e in result['response']['errors']:
				Tester.notify('^   ' + e)
		return result;
	
	@staticmethod	
	def test1(host):
		'''Check service is available'''
		Tester.make_test(host,'GET', Tester.uri(['/']), {'HTTP_status':200}, Tester.check_code)
	
	@staticmethod		
	def test2(host):
		'''***Circle area via valid names and valid values of parameters***'''
		for param in Tester.CV:
			for value in Tester.V:
				Tester.make_test(host,'GET', Tester.uri(['circle', param, str(value)]), {'HTTP_status':200, 'JSON_status':'success', 'shape':'circle'}, Tester.check_response)
									
	@staticmethod		
	def test3(host):
		'''***Circle area via valid names and invalid values of parameters***'''
		for param in Tester.CV:
			for value in Tester.I:
				Tester.make_test(host,'GET', Tester.uri(['circle', param, str(value)]), {'HTTP_status':404, 'JSON_status':'fault'}, Tester.check_response)

	@staticmethod		
	def test4(host):
		'''***Circle area via invalid names and valid values of parameters***'''
		for param in Tester.IP:
			for value in Tester.V:
				Tester.make_test(host,'GET', Tester.uri(['circle', param, str(value)]), {'HTTP_status':404, 'JSON_status':'fault'}, Tester.check_response)
		
	@staticmethod		
	def test5(host):
		'''***Circle area via extra parameters***'''
		for param in Tester.CV:		
			Tester.make_test(host,'GET', Tester.uri(['circle', param, '2/3']), {'HTTP_status':404, 'JSON_status':'fault'}, Tester.check_response)		
	
	@staticmethod		
	def test6(host):
		'''***Circle area via insufficient parameters***'''
		for param in Tester.CV:		
			Tester.make_test(host,'GET', Tester.uri(['circle', param]), {'HTTP_status':404, 'JSON_status':'fault'}, Tester.check_response)

	@staticmethod		
	def test7(host):
		'''***Rectangle area via valid names and valid values of parameters***'''
		for param1 in Tester.RV:	
			for param2 in Tester.RV:
				for value1 in Tester.V:
					for value2 in Tester.V:
						if param1 != param2:
							Tester.make_test(host,
															'GET', 
															Tester.uri(['rectangle', param1, str(value1), param2, str(value2)]), 
															{'HTTP_status':200, 'JSON_status':'success','shape':'rectangle'}, 
															Tester.check_response)

	@staticmethod		
	def test8(host):
		'''***Rectangle area via valid names and valid invalues of parameters***'''
		for param1 in Tester.RV:	
			for param2 in Tester.RV:
				for value1 in Tester.I:
					for value2 in Tester.I:
						Tester.make_test(host,
														'GET', 
														Tester.uri(['rectangle', param1, str(value1), param2, str(value2)]), 
														{'HTTP_status':404, 'JSON_status':'fault'}, 
														Tester.check_response)	

	@staticmethod		
	def test9(host):
		'''***Rectangle area via invalid names and valid values of parameters***'''
		for param1 in Tester.IP:	
			for param2 in Tester.IP:
				for value1 in Tester.V:
					for value2 in Tester.V:
						Tester.make_test(host,
														'GET', 
														Tester.uri(['rectangle', param1, str(value1), param2, str(value2)]), 
														{'HTTP_status':404, 'JSON_status':'fault'}, 
														Tester.check_response)	

	@staticmethod		
	def test10(host):
		'''***Rectangle area via equal parameters names***'''
		for param1 in Tester.RV:	
			for param2 in Tester.RV:
				if param1 == param2:
					Tester.make_test(host,
													'GET', 
													Tester.uri(['rectangle', param1, str(Tester.V[0]), param2, str(Tester.V[0])]), 
													{'HTTP_status':404, 'JSON_status':'fault'}, 
													Tester.check_response)	


	@staticmethod		
	def test11(host):
		'''***Rectangle area via extra parameters***'''
		for param1 in Tester.RV:	
			for param2 in Tester.RV:
				if param1 != param2:
					Tester.make_test(host,
													'GET', 
													Tester.uri(['rectangle', param1, str(Tester.V[0]), param2, str(Tester.V[0]),str(Tester.V[0])]), 
													{'HTTP_status':404, 'JSON_status':'fault'}, 
													Tester.check_response)

	@staticmethod		
	def test12(host):
		'''***Rectangle area via insufficient parameters***'''
		for param1 in Tester.RV:	
			for param2 in Tester.RV:
				Tester.make_test(host,
												'GET', 
												Tester.uri(['rectangle', param1, param2]), 
												{'HTTP_status':404, 'JSON_status':'fault'}, 
												Tester.check_response)

	@staticmethod		
	def test13(host):
		'''***Check methods inavalable***'''
		for method in Tester.M:	
			Tester.make_test(host,
											method, 
											Tester.uri(['/']), 
											{'HTTP_status':405, 'JSON_status':'fault'}, 
											Tester.check_response)	

	@staticmethod		
	def notify(mess):
		print(mess)
		if Tester.log_file:
			Tester.log_file.write(mess+'\n')		

	

def main():
	log_file_name = os.path.join(os.path.dirname(__file__), 'testmyrest.log')
	host = 'localhost:8080'
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'H:')
		if len(args):
			log_file_name = args[0]
		if optlist and optlist[0][1]:
			host = optlist[0][1]
	except:
		print('usage: python3 testmyrest.py -H <host> <log_file_name>')	
		return

	Tester.log_file = open(log_file_name, 'w')
	for field in dir(Tester):
		if field.startswith('test'):
			test = getattr(Tester, field)
			Tester.notify(test.__doc__)
			test(host)
			Tester.notify('\n')
	for fail in Tester.failed_uris:
		Tester.notify(fail)
	Tester.notify('\n')
	Tester.notify(' TOTAL: %s' % (Tester.total_tests_count))
	Tester.notify(' FAILED: %s' % (Tester.failed_tests_count))

if __name__ == "__main__":
	main()
