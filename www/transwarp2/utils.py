#!/usr/bin/python
# coding: utf8

class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
       super(Dict, self).__init__(**kw)

       for k, v in zip(names, values):
           self[k] = v

    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v
