#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Xiushun Lu'

import os, re, time, base64, hashlib, logging

import markdown2

from transwarp.web import get, post, ctx, view, interceptor, seeother, notfound

from apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError

from models import User, Blog, Comment
from config import configs

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_MD5 = re.compile(r'^[0-9a-f]{32}$')


_COOKIE_NAME = 'awesession'
_COOKIE_KEY  = configs.session.secret


def make_signed_cookie(id, password, max_age):
    '''
    加密cookie
    "用户id" + "过期时间" + MD5("用户id" + "用户口令" + "过期时间" + "SecretKey")
    '''
    expires = str(int(time.time()+(max_age or 86400)))
    L = [id, expires, hashlib.md5('%s-%s-%s-%s' % (id, password, expires, _COOKIE_KEY)).hexdigest()]
    
    return '-'.join(L)


def parse_signed_cookie(cookie_str):
    '''
    解密cookie，并进行登录信息的验证
    '''
    L = cookie_str.split('-')
    if len(L) != 3:
        return None
    id, expires, md5 = L 
    if int(expires)<time.time():
        logging.info('cookie timeouted.')
        return None 
    user = User.get(id)
    if user is None:
        return None
    md5_2 = hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, _COOKIE_KEY)).hexdigest()
    if md5 != md5_2:
        logging.info('md5 mismatch.')
        return None 
    return user 


def check_admin():
    user = ctx.request.user
    if user and user.admin:
        return 
    raise APIPermissionError('No Permission.')


def _get_page_index():
    page_index = 1
    try:
        page_index = int(ctx.request.get('page', '1'))
    except ValueError:
        pass 
    return page_index


def _get_blogs_by_page():
    total = Blog.count_all();
    page = Page(total, _get_page_index())
    blogs = Blog.find_by('order by created_at desc limit ?,?', page.offset, page.limit)
    return blogs, page 


@interceptor('/')
def user_interceptor(next):
    '''
    利用拦截器在URL处理之前解析cookie，并将用户信息绑定到request对象上
    '''
    logging.info('try to bind user from session cookie...')
    user = None
    cookie = ctx.request.cookies.get(_COOKIE_NAME)
    # logging.info('cookie~~%s~~' % cookie)
    if cookie:
        logging.info('parse session cookie...')
        user = parse_signed_cookie(cookie)
        if user:
            logging.info('bind user <%s> to session...' % user.email)
    ctx.request.user = user
    return next()


# 拦截器接受一个next函数，这样，一个拦截器可以决定调用next()继续处理请求还是直接返回
@interceptor('/manage/')
def manage_interceptor(next):
    user = ctx.request.user 
    if user and user.admin:
        return next()
    raise seeother('/signin')


