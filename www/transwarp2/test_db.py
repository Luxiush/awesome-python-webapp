#!/usr/bin/python
# coding: utf8

import logging, threading, json
import db

logging.basicConfig(level=logging.DEBUG)

db.create_engine('root', '14353222', 'test')

params = [{
        'sql': 'select * from users',
        'name': 'T-a',
        'res': None,
        'thread': None
    }, {
        'sql': 'select name, email from users',
        'name': 'T-b',
        'res': None,
        'thread': None
    }, {
        'sql': 'select name, id, user_id from blogs limit 3',
        'name': 'T-c',
        'res': None,
        'thread': None
    }]


def thread_func(i):
    print "current thread: %s" % threading.current_thread().name 
    params[i]['res'] = db.query(params[i]['sql'])
    print "query result: %s" % json.dumps(params[i]['res'])
    print "\n"


def test():
    print ">>>Creating threads."
    for i in range(len(params)):
        param = params[i]
        param['thread'] = threading.Thread(target=thread_func, args=(i,), name=param['name'])

    print ">>>Starting thread"
    for p in params:
        print ">>>thread %s is running." % p['name']
        p['thread'].start()

    print ">>>Waiting..."
    for p in params:
        p['thread'].join()
    
    print "Done"


if __name__ == '__main__':
    test()
