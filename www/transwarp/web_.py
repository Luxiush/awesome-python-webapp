#
# coding: utf-8
# web.py

import types, os, re, cgi, sys, time, datetime, functools, mimetypes, threading, logging, urllib, traceback

try:
    from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

# 全局ThreadLocal对象：
ctx = threading.local()

# HTTP错误类:
class HttpError(Exception):
    pass


def _to_str(s):
	pass 

def _to_unicode(s, encoding='utf-8'):
	pass 

def _quote(s, encoding='utf-8'):
	pass

def _unquote(s, encoding='utf-8'):
	'''
	>>> _unquote('http%3A//example/test%3Fa%3D1+')
    u'http://example/test?a=1+'
	'''
	return urllib.unquote(s).decode(encoding)

class MultipartFile(object):
	def __init__(self, storage):
		self.filename = _to_unicode(storage.filename)
		self.file = storage.file

# request对象:
class Request(object):
	def __init__(self, environ):
		self._environ = environ

	#解析http请求中的参数列表（a=1&b=M%20M&c=ABC&c=XYZ&e=）
	def _parse_input(self):
		def _convert(item):
			if isinstance(item, list):
				return [_to_unicode(i.value) for i in item]
			if item.filename:
				return MultipartFile(item)
			return _to_unicode(item.value)

		fs = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ, keep_blank_values=True)
        inputs = dict()
        for key in fs:
            inputs[key] = _convert(fs[key])
		return inputs

	def _get_raw_input(self):
		if not hasattr(self, '_raw_input'):
			self._raw_input = self._parse_input()
		return self._raw_input

	def __getitem__(self, key):
		'''
		获取参数的值
		'''
		r = self._get_raw_input()[key]
		if isinstance(r,list):
			return r[0]
		return r 


    # 根据key返回value:
    def get(self, key, default=None):
        r = self._get_raw_input().get(key, default)
        if isinstance(r, list):
        	reutrn r[0]
        return r 
    def gets(self, key):
    	r = self._get_raw_input()[key]
    	if isinstance(r, list):
    		return r[:]
    	return [r]

    # 返回key-value的dict:
    def input(self, **kw):
        copy = Dict(**kw)
        raw = self._get_raw_input()
        for k,v in raw.iteritem():
        	copy[k] = v[0] if isinstance(v,list) else v
        return copy

    def get_body(self):
    	'''
		获取POST的body部分
    	'''
    	fp = self._environ['wsgi.input']
    	return fp.read()


    # 返回URL的path:
    @property
    def path_info(self):
        return urllib.unquote(self._environ.get('PATH_INFO', ''))

	# 返回HTTP Headers:
    def _get_headers(self):
    	if not hasattr(self, '_headers'):
    		hdrs = {}
    		for k,v in self._environ.iteritem():
    			if k.startwith('HTTP_'):
    				hdrs[k[5:].replace('_','-').upper()] = v.decode('utf-8')
    		self._headers = hdrs 
    	return self._headers
    @property
    def headers(self):
        return dict(**self._get_headers())
    def header(self, header, default=None):
    	return self._get_headers().get(header.upper(), default)

    # 根据key返回Cookie value:
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



# response对象:
class Response(object):
	def __init__(self):
		self._status = '200 OK'
		self._headers = {'CONTENT-TYPE': 'text/html; charset=utf-8'}

	@property
	def headers(self):
		L = [(_RESPONSE_HEADER_DICT.get(k,k),v) for k,v in self._headers.iteritems()]
		if hasattr(self, '_cookies'):
			for v in self._cookies.itervalues():
				L.append(('Set-Cookie', v))
		L.append(_HEADER_X_POWERED_BY)
		return L

	def headre(self, name):
		key = name.upper()
		if not key in _RESPONSE_HEADER_DICT:
			key = name
		return self._headers.get(key)


    # 设置header:
    def set_header(self, name, value):
    	key = name.upper()
    	if not key in _RESPONSE_HEADER_DICT:
    		key = name
    	self._headers[key] = _to_str(value)
        

    def unset_header(self, name):
    	key = name.upper()
    	if not key in _RESPONSE_HEADER_DICT:
    		key = name
    	if key in self._headers:
    		del self._headers[key]

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
    	pass
    @content_length.setter
    def content_length(self, value):
    	pass

    # 设置Cookie:
    def set_cookie(self, name, value, max_age=None, expires=None, path='/', domain=None, secure=False, http_only=True):
        '''
		max_age: cookie的最长存活时间
		expires: cookie的存活时间
        '''
        if not hasattr(self, '_cookies'):
        	self._cookies = {}
        L = ['%s=%s' % (_quote(name), _quote(value))]
        if expires is not None:
        	if isinstance(expires, (float, int, long)):
                L.append('Expires=%s' % datetime.datetime.fromtimestamp(expires, UTC_0).strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
            if isinstance(expires, (datetime.date, datetime.datetime)):
				L.append('Expires=%s' % expires.astimezone(UTC_0).strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
		elif isinstance(max_age, (int, long)):
			L.append('Max-Age=%d' % max_age) 
		L.append('Path=%s' % path) 
		if domain:
            L.append('Domain=%s' % domain)
        if secure:
            L.append('Secure')
        if http_only:
            L.append('HttpOnly')
		self._cookies[name] = '; '.join(L)  
	def unset_cookie(self, name):
		if hasattr(self, '_cookies'):
			if name in self._cookies:
				del self._cookies[name]
    def delete_cookie(self, name):
    	self.set_cookie(name, '__deleted__', expires=0)

    @property
    def status_code(self):
    	return int(self._status[:3])

    # 设置status:
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        pass

# 定义GET:
def get(path):
	def _decorator(func):
		func.__web_route__ = path 
		func.__web_method__ = 'GET'
		return func 
	return _decorator
# 定义POST:
def post(path):
    def _decorator(func):
		func.__web_route__ = path 
		func.__web_method__ = 'POST'
		return func 
	return _decorator

# 定义模板:
def view(path):
    pass

# 定义拦截器:
def interceptor(pattern):
    pass

# 定义模板引擎:
class TemplateEngine(object):
    def __call__(self, path, model):
        pass

# 缺省使用jinja2:
class Jinja2TemplateEngine(TemplateEngine):
    def __init__(self, templ_dir, **kw):
        from jinja2 import Environment, FileSystemLoader
        self._env = Environment(loader=FileSystemLoader(templ_dir), **kw)

    def __call__(self, path, model):
        return self._env.get_template(path).render(**model).encode('utf-8')


class WSGIApplication(object):
	def __init__(self):
		pass 

	def run(self, port=9000, host='127.0.0.1'):
		from wsgiref.simple_server import make_server

		server = make_server(host, port, self.get_wsgi_application(debug=True))
		server.serve_forever()


	def get_wsgi_application(self, debug=False):
		pass

if __name__=='__main__':
    sys.path.append('.')
    import doctest
	doctest.testmod()