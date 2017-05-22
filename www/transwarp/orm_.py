#! 
# coding: utf-8
# http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001386820064557c69858840b4c48d2b8411bc2ea9099ba000

import time, logging
import db

class Field(object):
	'''
	保存数据库表的字段名和字段类型
	'''
	def __init__(self, name, column_type):
		self.name = name
		self.column_type =column_type
	def __str__(self):
		return '<%s:%s>' %(self.__class__.__name__, self.name)

class StringField(Field):
	def __init__(self, name):
		super(StringField, self).__init__(name, 'varchar(100)')

class IntegerField(Field):
	def __init__(self, name):
		super(IntegerField, self).__init__(name, 'bigint')


class ModelMetaClass(type):
	'''
	Model 的元类
	'''
	def __new__(cls, name, bases, attrs):
		'''
		在当前类中查找定义的类的所有属性，
		如果找到一个Field属性，就把它保存到一个__mappings__的dict中，
		同时从类属性中删除该Field属性，避免混淆
		'''

		if name=='Model':
			return type.__new__(cls, name, bases, attrs)

		mappings = dict()
		for k,v in attrs.iteritems():
			if isinstance(v, Field):
				mapping[k] = v

		for k in mapping.iterkeys():
			attrs.pop(k)
		attrs['__table__'] = name 
		attrs['__mappings__'] = mappings
		return type.__new__(cls, name, bases, attrs)



class Model(dict):
	'''
	所有ORM映射的基类
	'''

	__metaclass__ = ModelMetaClass

	def __init__(self, **kw):
		super(Model, self).__init__(**kw)
	
	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Model' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

    def save(self):
        fields = []
        params = []
        args = []
        for k, v in self.__mappings__.iteritems():
            fields.append(v.name)
            params.append('?')
            args.append(getattr(self, k, None))
        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))
        print('SQL: %s' % sql)
        print('ARGS: %s' % str(args))












