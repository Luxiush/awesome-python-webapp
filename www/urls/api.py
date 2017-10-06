#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Xiushun Lu'

import os, re, time, base64, hashlib, logging

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
    _COOKIE_KEY,
    _RE_EMAIL,
    _RE_MD5
)


@api
@post('/api/authenticate')
def api_authenticate():
    """验证用户的登录信息,并生成cookie"""
    i = ctx.request.input()
    email = i.email.strip().lower()
    password = i.password
    remember = i.remember
    user = User.find_first('where email=?', email)
    if user is None:
        raise APIError('auth:failed', 'email', 'Invalid email.')
    if password != user.password:
        raise APIError('auth:failed', 'password', 'Invalid password.')

    max_age = 604800
    cookie = make_signed_cookie(user.id, user.password, max_age)
    ctx.response.set_cookie(_COOKIE_NAME, cookie, max_age=max_age)
    user.password = '******'
    return user


@api
@post('/api/register')
def api_register():
    i = ctx.request.input(name='', email='', password='')
    email = i.email.strip().lower()
    password = i.password
    name = i.name.strip()

    if not name:
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not password or not _RE_MD5.match(password):
        raise APIValueError('password')
    user = User.find_first('where email=?', email)
    if user:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    user = User(name=name, email=email, password=password, image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email).hexdigest())
    user.insert()
    # make session cookie:
    cookie = make_signed_cookie(user.id, user.password, None)
    ctx.response.set_cookie(_COOKIE_NAME, cookie)
    return user


@api
@post('/api/signout')
def api_signout():
    ctx.response.delete_cookie(_COOKIE_NAME)


@api
@get('/api/blogs')
def api_get_blogs_by_page():
    blogs, page = _get_blogs_by_page()
    for blog in blogs:
        blog.content = markdown2.markdown(blog.content)
    return dict(blogs=blogs, page=page)


@api
@get('/api/blog/:blog_id')
def api_get_blog_by_id(blog_id):
    """
    根据id获取blog
    """
    blog = Blog.get(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')

    return dict(blog=blog)


@api
@post('/api/blog/edit')
def api_post_blog_edit():
    """
    提交博客的修改,
    如果是编辑还需传入一个blog_id
    """
    i = ctx.request.input(blog_id='', name='', summary='', content='')
    blog_id = i.blog_id.strip()
    name = i.name.strip()
    summary = i.summary.strip()
    content = i.content.strip()
    if not name:
        raise APIValueError('name', 'name cannot be empty.')
    if not summary:
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content:
        raise APIValueError('content', 'content cannot be empty.')

    user = ctx.request.user
    blog = Blog(user_id=user.id, user_name=user.name, name=name, summary=summary, content=content)

    if blog_id != '' and blog_id != '__new__':
        blog_old = Blog.get(blog_id)
        blog_old.delete()

    blog = blog.insert()

    return blog


# @api
# @post('/api/markdown/preview')
# def api_post_md_preview():
#     pass


# @api
# @get('/api/markdown/edit')
# def api_get_md_edit():
#     pass


@api
@get('/api/comments/:blog_id')
def api_get_comments_by_id(blog_id):
    """根据id获取对应博客的评论"""
    comments = Comment.find_by('where blog_id=? order by created_at desc limit 20', blog_id)
    return dict(comments=comments)


@api
@post('/api/comments/:blog_id')
def api_post_comment(blog_id):
    """提交评论"""
    i = ctx.request.input(content='')
    content = i.content.strip()
    if not content:
        raise APIValueError('content', 'content cannot be empty')
    user = ctx.request.user
    comment = Comment(blog_id=blog_id, user_id=user.id, user_name=user.name, user_image=user.image, content=content)
    comment.insert()
    return comment
