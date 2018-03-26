#!/usr/bin/python
# coding: utf8

import logging, functools, threading, uuid, json
import mysql.connector
from utils import Dict

logging.basicConfig(level=logging.DEBUG)


class DbError(Exception):
    pass

class Engine(object):
    '''
    一个Engine对象持有一个已经配置好的闭包,
    相当于一个还没有打开的连接.
    当调用connect方法时才真正建立连接.
    '''

    def __init__(self, connect):
        self._connect = connect


    def connect(self):
        return self._connect()


engine = None
def create_engine(user, password, database,
           host="127.0.0.1", port=3306, **kw):
    global engine
    if engine is not None:
        logging.info("engine <%s> is already exist." % hex(id(engine)))
        return

    params = dict(user=user, password=password, database=database, host= host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False)
    for k, v in defaults.iteritems():
        params[k] = kw.pop(k, v)
    params.update(kw)
    params['buffered'] = True

    def connect():
        return mysql.connector.connect(**params)

    engine = Engine(connect)
    logging.info("new engine: <%s>" % hex(id(engine)))



class _DbCtx(threading.local):
    '''
    保存一个已经打开的连接
    '''
    def __init__(self):
        self.connection = None

    def _connect(self):
        if not self.connection:
            if not engine:
                raise DbError("engine has not been initialed yet.")
            self.connection = engine.connect()
            logging.info("open connection <%s>" % hex(id(self.connection)))
        else:
            logging.info("connection <%s> is already exist." % hex(id(self.connection)))

    def _close(self):
        if self.connection:
            logging.info("closing connection <%s> ..." % hex(id(self.connection)))
            self.connection.close()
            self.connection = None
        else:
            logging.info("no connection is opening.")

    def cursor(self):
        if self.connection:
            return self.connection.cursor()
        else:
            logging.info("no connection is opening.")
            return None

_ctx = _DbCtx()


class ConnectionCtx(object):
    def __init__(self):
        return

    def __enter__(self):
        _ctx._connect()
        return self

    def __exit__(self, exctype, excvalue, traceback):
        _ctx._close()


def with_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        with ConnectionCtx():
            return func(*args, **kw)
    return wrapper


@with_connection
def query(sql):
    cursor = _ctx.cursor()
    cursor.execute(sql)
    names = []
    if cursor.description:
        names = [x[0] for x in cursor.description]

    res = [Dict(names, x) for x in cursor.fetchall()]
    cursor.close()
    return res


@with_connection
def update(sql):
    cursor = _ctx.cursor()
    cursor.execute(sql)
    r = cursor.rowcount
    cursor.close()
    return r

# ---------------------------------------------

def test():
    create_engine('root', '14353222', 'test')
    sql = 'select * from users'

    res = query(sql)

    print "result for '%s': " % sql
    print "%s" % json.dumps(res, ensure_ascii=False)


if __name__ == '__main__':
   test()
