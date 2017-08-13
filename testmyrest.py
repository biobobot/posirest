import json
import http.client as client
import os

class Tester:
	valid=[
	'0',
	'2', 
	'2.2',
	'%32',
	'87486635647389820987352773527192\
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
871263871263871254653754',
	'2e+2'
	]
	invalid =[
	'2,2',
	'-2',
	'string',
	'@&:()%$~?^'
	]
	unsupported = [
	'POST',
	'DELETE',
	'OPTIONS',
	'TRACE'
	]

	DELIMITER = '------------------------------------'
	host = 'localhost'
	total_tests_count = 0
	failed_tests_count = 0
	failed_uris = []
	

	def start(self):
		self.f = open(os.path.join(os.path.dirname(__file__), 'testmyrest.log'), 'w')		

	def finish(self):	
		self.f.close()

	def notify(self, mess):
		print(mess)
		if self.f:
			self.f.write(mess+'\n')
	
	def prepare_value(self, value):
		if len(value)>20:
			return '~big~'
		if not value:
			return '~empty~'
		return value

	def prepare_uri(self, values, get_params, simplify):
		uri =''
		for v in values:
			if simplify:
				v = self.prepare_value(v)
			uri += ('/'+v)
		if get_params:
			uri += get_params
		return uri

	def make_request(self, method, uri):
		connection = client.HTTPConnection(self.host)
		connection.request(method, uri)
		response = connection.getresponse()
		connection.close()
		return response

	def get_json_result(self, response, result):
		if response.status != 200:
			result['what'].append('service returns '+ str(response.status))
		try:
			body_bytes = response.read()
			body_string = body_bytes.decode('utf-8')
			result['response'] = json.loads(body_string)
			return True
		except:
			result['what'].append('response is not JSON object')
		return False

	def check_result(self, response, result, status):
		if not self.get_json_result(response,result):
			return False
		if 'status'not in result['response']:
			result['what'].append('response do not contains status field')
		else:
			if result['response']['status'] != ('success' if status else 'fault'):
				result['what'].append('response contains '+result['response']['status']+' status')
			if result['response']['status'] == 'success':
				if 'result'not in result['response']:
					result['what'].append('response do not contains result field')
				else:
					if 'shape'not in result['response']['result']:
						result['what'].append('result do not contains shape field')
					if 'area'not in result['response']['result']:
						result['what'].append('result do not contains area field')
			else:
				if 'errors'not in result['response']:
					result['what'].append('response do not contains errors field')
		return not len(result['what'])

	def make_test(self, method, shape, values, get_params, status):
		uri = self.prepare_uri(values,get_params,False)
		response = self.make_request(method,uri)
		result = {}
		result['what'] = []
		sucsess = self.check_result(response, result, status)
		if sucsess and status:
			if result['response']['result']['shape'] != shape:
				result['what'].append(result['response']['result']['shape'] +" is not valid shape" )
		result['status'] = 'ok' if not len(result['what']) else 'fail'
		if 'response' in result and 'errors' in result['response']:
			for e in result['response']['errors']:
					result['what'].append(e)
		self.total_tests_count += 1;
		if result['status'] == 'fail':
			self.failed_tests_count += 1
			self.failed_uris.append(self.prepare_uri(values, get_params,True))

		self.notify(self.DELIMITER)
		self.notify(' %-5s ! %s: %s' % (result['status'], method, self.prepare_uri(values,get_params,True)))
		self.notify_explanation(result['what'])
		self.notify(self.DELIMITER)

	def	notify_explanation(self, what):
		if len(what):
			self.notify(self.DELIMITER)
			for w in what:
				self.notify('. ' + w)

	class Tests:

		@staticmethod
		def test_circle_by_valid_radius(tester):
			'''Circle by valid radius'''
			for v in tester.valid:
			 result = tester.make_test('GET', 'circle', ['circle', v], '', True)

		@staticmethod
		def test_circle_by_invalid_radius(tester):
			'''Circle by invalid radius'''
			for v in tester.invalid:
				result = tester.make_test('GET', 'circle', ['circle', v], '', False)

		@staticmethod
		def test_circle_by_valid_diameter(tester):
			'''Circle by valid diameter'''
			for v in tester.valid:
				result = tester.make_test('GET', 'circle', ['circle', v], '?d', True)

		@staticmethod
		def test_circle_by_invalid_diameter(tester):
			'''Circle by invalid diameter'''
			for v in tester.invalid:
				result = tester.make_test('GET', 'circle', ['circle', v], '?d', False)

		@staticmethod
		def test_circle_by_empty_radius(tester):
			'''Circle by empty radius'''
			result = tester.make_test('GET', 'circle', ['circle', '/'], '', False)

		@staticmethod
		def test_circle_by_empty_diameter(tester):
			'''Circle by empty diameter'''
			result = tester.make_test('GET','circle',['circle', '/'],'?d', False)

		@staticmethod
		def test_circle_by_valid_radius_with_additinal_get_params(tester):
			'''Circle by valid radius with useless get params'''
			for v in tester.valid:
				result = tester.make_test('GET', 'circle', ['circle', v], '?param1=0&?param2=0', True)

		@staticmethod
		def test_circle_by_excess_data(tester):
			'''Circle by empty diameter'''
			result = tester.make_test('GET', 'circle', ['circle', '2', '3'], '?d', False)

		@staticmethod
		def test_square_by_valid_side(tester):
			'''Rectangle by valid single side'''
			for v in tester.valid:
				result = tester.make_test('GET', 'square', ['rectangle', v], '', True)

		@staticmethod
		def test_square_by_invalid_side(tester):
			'''Rectangle by invalid single side'''
			for v in tester.invalid:
				result = tester.make_test('GET', 'square', ['rectangle', v], '', False)

		@staticmethod
		def test_square_by_empty_side(tester):
			'''Rectangle by empty single side'''
			result = tester.make_test('GET', 'square', ['rectangle', '/'], '', False)

		@staticmethod
		def test_rectangle_by_valid_valid(tester):
			'''Rectangle by valid valid values'''
			for v1 in tester.valid:
				for v2 in tester.valid:
					result = tester.make_test('GET', 'rectangle',[ 'rectangle', v1, v2], '', True)

		@staticmethod
		def test_rectangle_by_valid_invalid(tester):
			'''Rectangle by valid invalid values'''
			for v1 in tester.valid:
				for v2 in tester.invalid:
					result = tester.make_test('GET', 'rectangle', ['rectangle', v1, v2], '', False)

		@staticmethod
		def test_rectangle_by_invalid_valid(tester):
			'''Rectangle by invalid valid values'''
			for v1 in tester.invalid:
				for v2 in tester.valid:
					result = tester.make_test('GET', 'rectangle', ['rectangle', v1, v2], '', False)

		@staticmethod
		def test_rectangle_by_invalid_invalid(tester):
			'''Rectangle by invalid invalid values'''
			for v1 in tester.invalid:
				for v2 in tester.invalid:
					result = tester.make_test('GET', 'rectangle' ,['rectangle', v1, v2], '', False)

		@staticmethod
		def test_rectangle_by_excess_data(tester):
			'''Rectangle by empty diameter'''
			result = tester.make_test('GET', 'rectangle', ['rectangle', '2', '3', '4'] ,'?d', False)

		@staticmethod
		def test_unsupported(tester):
			'''Unsupported methods'''
			for u in tester.unsupported:
					result = tester.make_test(u, '', [], '', False)

def main():
	'''
	Testing now is started
	'''
	
	
	tester = Tester()
	tester.start()	
	tester.host = 'localhost:8080' 
	tester.notify(main.__doc__)

	for feild in dir(tester.Tests):
		if feild.startswith('test'):
			test = getattr(tester.Tests, feild)
			tester.notify(test.__doc__)
			test(tester) 
			tester.notify('\n')

	tester.notify(' TOTAL: %s' % (tester.total_tests_count))
	tester.notify(' FAILED: %s' % (tester.failed_tests_count))

	for fail in tester.failed_uris:
		tester.notify("   ."+fail)
	
	tester.finish()

if __name__ == "__main__":
	main()
