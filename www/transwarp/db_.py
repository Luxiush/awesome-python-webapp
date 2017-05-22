#! 
# coding:utf-8
# db.py

import mysql.connector


class _LasyConnection(object):
	def __init__(self):
		self.connection = None

	def cursor(self):
        if self.connection is None:
            connection = engine.connect()
            logging.info('open connection <%s>...' % hex(id(connection)))
            self.connection = connection
		return self.connection.cursor()


	def commit(self):
		self.connection.commit()

	'''
	todo:
		rollback()
		cleanup()

	'''

class _DbCtx(threading.local):
	'''
	* 持有数据库链接的上下文对象
	* 继承自threading.local，所以持有的连接对于每个现成都是不一样的
	'''
	def __init__(self):
		self.connection = None
		self.transactions = 0


	def init(self):
		logging.info('open lazy connection...')
		self.connection = _LasyConnection()
		self.transactions = 0

	'''
	todo:
		is_init()
		cleanup()
		cursor()
	'''

_db_ctx = _DbCtx()

#---------------------------------#

engine = None 

class _Engine(object):
	def __init__(self, connect):
		self._connect = connect

	def connect(self):
		return self._connect

def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
	'''
	建立连接
	'''
	import mysql.connector
	global engine
	pass

#---------------------------------#

class _ConnectionCtx(object):
	'''
	连接的自动建立和释放
	'''
	def __enter__(self):
		pass

	def __exit__(self):
		pass

def connection():
	'''
	为了能够使用with语句
	'''
	return _ConnectionCtx()

def with_connection(func):
	'''
	decorator的使用
	'''
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)
	return _wrapper


#----------------------#

class _TransactionCtx(object):
	'''
	事务的处理
	'''

	def __enter__(self):
		pass 

	def __exit__(self, exctype, excvalue, traceback):
		pass

	def commit(self):
		pass

	def rollback(self):
		pass 

def transaction():
	'''
	with
	'''
	return _TransactionCtx()

def with_transaction():
	'''
	decorator
	'''
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        _start = time.time()
        with _TransactionCtx():
            return func(*args, **kw)
        _profiling(_start)
	return _wrapper	


#----------------#
#数据库的基本操作

def _select(sql, first, *args):
	pass


@with_connection
def _update(sql, *args):
	global _db_ctx
	cursor = None 
	sql = sql.replace('?','%s')
	


#----------------#
#调试
if __name__=='__main__':
	logging.basicConfig(level=logging.DEBUG)
	create_engine('www-data', 'www-data', 'test')