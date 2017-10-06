#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Xiushun Lu'

import os, re, time, base64, hashlib, logging

import time

import markdown2

from transwarp.web import get, post, ctx, view, interceptor, seeother, notfound

from apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError

from models import User, Blog, Comment
from config import configs

from utils import(
    make_signed_cookie,
    parse_signed_cookie,
    check_admin,
    _get_page_index,
    _get_blogs_by_page,
    _COOKIE_NAME,
    _COOKIE_KEY
)


@view('signin.html')
@get('/signin')
def get_signin():
    """返回html页面"""
    return dict()


@view('register.html')
@get('/register')
def get_register():
    """返回html注册页面"""
    return dict()


@view('index.html')
@get('/')
def get_index():
    """web homepage"""
    return dict()


@view('blogs_index.html')
@get('/blogs')
def get_blog_index():
    """blogs homepage"""
    blogs, page = _get_blogs_by_page()

    return dict(
            user=ctx.request.user,
            blogs=blogs,
            page=page
        )


@view('blog_disp.html')
@get('/blog/:blog_id')
def get_blog_disp_frame(blog_id):
    blog = Blog.get(blog_id)
    if blog is None:
        raise notfound()

    blog.content = markdown2.markdown(blog.content)

    return dict(blog=blog, user=ctx.request.user)

@view('blog_edit.html')
@get('/blog/:blog_id/edit')
def get_blog_edit(blog_id):
    return dict(blog_id=blog_id, user=ctx.request.user)


@view('blog_edit.html')
@get('/blog/new')
def get_blog_new():
    return dict(blog_id='', user=ctx.request.user)
    # return dict(blog=Blog(), user=ctx.request.user)
