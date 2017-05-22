#! 
# coding: utf-8
# web.py

_RESPONSE_STATUSES = {
	100: 'Continue', 
	...
	200: 'OK',
	...
	300: 'Multiple Choices',
	...
}

_RESPONSE_HEADERS = (
	'Accept-Ranges',
	'Age',
	'Allow',
	...
)

#-----------------------------------------#

class HttpError(Exception):
	pass


#-----------------------------------------#
class Route(object):
	'''
	Route对象，可调用对象
	'''
	def __init__(self, func):
		self.path = func.__web_route__
		self.method = func.__web_method__
		self.is_static = _re_route.search(self.path) is None
		if not self.is_static:
			self.route = re.complie(_build_regex(self.path))
		self.func = func

	def __call__(self, *args):
		return self.func(*args)

	def __str__(self):
        if self.is_static:
            return 'Route(static,%s,path=%s)' % (self.method, self.path)
		return 'Route(dynamic,%s,path=%s)' % (self.method, self.path)

	__repr__ = __str__

	def match(self, url):
		m = self.route.match(url)
		if m:
			return m.groups()
		return None


# Request对象 ---------------------------------------#
class Request(object):
	def __init__(self, environ):
		eslf._environ = environ 

	# environ['wsgi.input']------------------#

	def _parse_input(self):
		'''
		解析http请求,
		解析 environ 的 wsgi.input 参数
		'''

		pass 

	def _get_raw_input(self):
		'''
		以dict格式返回 wsgi.input 的值
		'''
		pass 

	def __getitem__(self, key):
		'''
		获取对应参数的值
		'''
		pass
	def get(self, key, default=None):
		'''
		获取对应参数的值
		'''		
		pass
	def gets(self, key):
		'''
		获取多个参数的值, 以list的形式返回
		'''		
		pass

	def input(self, **kw):
		'''
		以dict格式返回http请求,
		如果对应的key不存在则以传入的默认值填充
		'''
		pass

	def get_body(self):
		'''
		获取 REQUEST_METHOD 为 POST 时的 wsgi.input
		以string形式返回
		'''
		fp = self._environ['wsgi.input']
		return fp.read()

	# header (environ['HTTP_XXXXXX'])-------------------#

	def _get_headers(self):
		'''
		获取 environ 中以 'HTTP_' 开头的参数的值
		'''
		if not hasattr(self, '_headers'):
			hdrs = {}
			for k,v in self._environ.iteritems():
				if k.startswith('HTTP_'):
					hdrs[k[5:].replace('_', '-').upper()] = v.decode('utf-8')
			self._headers = hdrs
		return self._headers

	@property
	def headers(self):
		return dict(**self._get_headers())

	def header(self, header, default=None):
		'''
		获取对应 header 的值
		'''
		return self._get_headers().get(header.upper(), default)

	# cookie ----------------------------#

	def _get_cookies(self):
		if not hasattr(self, '_cookies'):
			cookies = {}
			cookie_str = self._environ.get('HTTP_COOKIE')
			if cookie_str:
				for c in cookie_str.split(';'):
					pos = c.find('=')
					if pos>0:
						cookies[c[:pos].strip()] = _unquote(c[pos+1:])
			self._cookies = cookies 
		return self._cookies
	
	@property 
	def cookies(self):
		return Dict(**self._get_cookies())
	def cookie(self, name, default=None):
		return self._get_cookies().get(name, default)


	# environ 的其他参数 ----------------#

	@property
	def remote_addr(self):
		return self._environ.get('REMOTE_ADDR', '0.0.0.0')
	@property
	def document_root(self):
		return self._environ.get('DOCUMENT_ROOT', '')
	@property
	def query_string(self):
		return self._environ.get('QUERY_STRING', '')
	@property
	def environ(self):
		return self._environ
	@property
	def request_method(self):
		return self._environ['REQUEST_METHOD']
	@property
	def path_info(self):
		return urllib.unquote(self._environ.get('PATH_INFO', ''))
	@property
	def host(self):
		return self._environ.get('HTTP_HOST', '')


# Response对象 ---------------------------------------#

class Response(object):
	def __init__(self):
		self._status = '200 OK'
		self._headers = {'CONTENT-TYPE': 'text/html; charset=utf-8'}

	# header ----------------------------#
	@property
	def headers(self):
		'''
		以dict形式返回响应头部
		'''
		pass 

	def header(self, name):
		pass

	def set_header(self, name, value):
		pass

	def unset_header(self, name):
		'''
		删除header中对应的key值
		'''
		pass

	# content-type ---------------------#
	@property
	def content_type(self):
		return self.header('CONTENT-TYPE')
	@content_type.setter
	def content_type(self, value):
		if value:
			self.set_header('CONTENT-TYPE', value)
		else:
			self.unset_header('CONTENT-TYPE')

	@property
	def content_length(self):
		return self.header('CONTENT-LENGTH')
	@content_length.setter(self, value):
		self.set_header('CONTENT-LENGTH',str(value))

	# cookie --------------------------#
	def set_cookie():
		pass

	def unset_cookie():
		pass

	def delete_cookie(self, name):
		self.set_cookie(name, '__deleted__', expires=0)


	# status --------------------------#
	@property
	def status_code(self):
		return int(self._status[:3])
	@property
	def status(self):
		return self._status
	@status.setter
	def status(self, value):
		if isinstance(value, (int,long)):
			if value>=100 and value<=999:
				st = _RESPONSE_STATUSES.get(value, '')
				if st:
					self._status = '%d %s' % (value, st)
				else:
					self._status = str(value)
			else:
				raise ValueError('Bad response code: %d' % value)
        elif isinstance(value, basestring):
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            if _RE_RESPONSE_STATUS.match(value):
                self._status = value
            else:
                raise ValueError('Bad response code: %s' % value)
        else:
			raise TypeError('Bad type of response code.')


# Application对象-------------------------------------#

class WSGIApplication(object):
	def __init__(self, document_root=None, **kw):
		self._running = False
		self._document_root = document_root
		self._interceptors = []
		self._template_engine = None
		self._get_static = {}
		self._post_static = {}
		self._get_dynamic = []
		self._post_dynamic = []

	def _check_not_running(self):
		pass


	def add_module(self, mod):
		self._check_not_running()
		m = mod if type(mod)==types.ModuleType else _load_module(mod)
		loggin.info('Add module: %s' % m.__name__)
		for name in dir(m):
			fn = getattr(m,name)
			if callable(fn) and hasattr(fn, '__web_route__') and hasattr(fn, 'web_method__'):
				self.add_url(fn)

	def add_url(self, func):
		pass

	def run(self, port=9000, host='127.0.0.1'):
		from wsgiref.simple_server import make_server
		logging.info('application (%s) will start at %s:%s...' % (self._document_root, host, port))
		server = make_server(host,port, self.get_wsgi_application(debug=True))
		server.serve_forever()

	def get_wsgi_application(self, debug=False):
		self._check_not_running():
		if debug:
			self._get_dynamic.append(StaticFileROute())
		self._running = True

		_application = Dict(document_root=self._document_root)

		def fn_route():
			pass


		def wsgi(env, start_response):
			pass

		return wsgi



# Jinja2TemplateEngine -------------------------------#
class Jinja2TemplateEngine(object):
	pass


#-----------------------------------------#
def get(path):
	def _decorator(func):
		func.__web_route__ = path
		func.__web_method__ = 'GET'
		return func
	return _decorator

def post(path):
	def _decorator(func):
		func.__web_route__ = path
		func.__web_method__ = 'POST'
		return func
	return _decorator

def view(path):
	def _cecorator(func):
		@functools.wraps(func)
		def _wrapper(*args, **kw):
			pass

		return _wrapper
	return _decorator


#-----------------------------------------#
if __name__=="__main__":
	pass	