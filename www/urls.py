#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 实现URL的处理函数

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
	expires = str(int(time.time() + (max_age or 86400))) 
	L = [id, expires, hashlib.md5('%s-%s-%s-%s'%(id, password, expires, _COOKIE_KEY)).hexdigest()]
	return '-'.join(L)

def parse_signed_cookie(cookie_str):
	'''
	解密cookie，并进行登录信息的验证
	'''
#	try:
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
'''	except:
		logging.info('unknown exception.')
		return None
'''
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


#----------- interceptor -----------------#

@interceptor('/')
def user_interceptor(next):
	'''
	利用拦截器在URL处理之前解析cookie，并将用户信息绑定到request对象上
	'''
	logging.info('try to bind user from session cookie...')
	user = None
	cookie = ctx.request.cookies.get(_COOKIE_NAME)
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


#---------------- view --------------------#	

##---------------- users

@view('signin.html')
@get('/signin')
def signin():
	return dict()

@view('/signout')
def signout():
	ctx.response.delete_cookie(_COOKIE_NAME)
	raise seeother('/')

@view('register.html')
@get('/register')
def register():
	return dict()

##---------------- blogs

@view('index.html')
@get('/')
def index():
	blogs = Blog.find_all()
	return dict(blogs=blogs, user=ctx.request.user)

@view('blog.html')
@get('/blog/:blog_id')
def detail(blog_id):
	blog = Blog.get(blog_id)
	if blog is None:
		raise notfound()
	blog.html_content = markdown2.markdown(blog.content)
	comments = Comment.find_by('where blog_id=? order by created_at desc limit 100', blog_id)
	return dict(blog=blog, comments=comments, user=ctx.request.user)

##---------------- manage

@view('manage_blog_edit.html')
@get('/manage/blogs/create')
def manage_blogs_create():
	return dict(id=None, action='/api/blogs', redirect='/manage/blogs', user=ctx.request.user)

@view('manage_blog_list.html')
@get('/manage/blogs')
def manage_blogs():
	return dict(page_index=_get_page_index(), user=ctx.request.user)



#---------------- api -----------------------#

##---------------- users

@api 
@get('/api/users')
def api_get_users():
	users = User.select('select * from users order by created_at desc')
	for u in users:
		u.password = '******'
	return dict(users=users)

@api
@post('/api/users')
def register_user():
	'''
	用户注册，
	数据库中保存的密码是经过MD5计算后的32位hash字符串
	'''
	i = ctx.request.input(name='', email='', password='')
	name = i.name.strip()
	email = i.email.strip().lower()
	password = i.password

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
@post('/api/authenticate')
def authenticate():
	'''
	用户登录验证
	验证用户的邮箱和密码，然后将用户的登录信息返回
	'''
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

##---------------- blogs

@api 
@post('/api/blogs') 
def api_create_blogs():
	'''
	创建blog
	'''
	check_admin();
	i = ctx.request.input(name='',summary='',content='')
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
	blog = Blog(user_id=user.id, user_name=user.name, summary=summary, content=content)
	blog.insert()
	return blog 

@api 
@get('/api/blogs')
def api_get_blogs():
	'''
	分页浏览
	'''
	format = ctx.request.get('format', '')
	blogs, page = _get_blogs_by_page()
	if format=='html':
		for blog in blogs:
			blog.content = markdown2.markdown(blog.content)
	return dict(blogs=blogs, page=page)

@api 
@get('/api/blogs/:blog_id')
def api_get_blog(blog_id):
	blog = Blog.get(blog_id)
	if blog:
		return blog 
	raise APIResourceNotFoundError('Blog')


@api 
@post('/api/blogs/:blog_id/delete')
def api_delete_blog(blog_id):
	check_admin()
	blog = Blog.get(blog_id)
	if blog is None:
		raise APIResourceNotFoundError('Blog')
 	blog.delete()
 	return dict(id=blog_id)

##---------------- comments

@api 
@get('/api/comments')
def api_get_comments():
	'''
	获取评论
	'''
	blog_id = ctx.request.get('blog_id','').strip()
	if blog_id:
		comments = Comment.select('select * from comments where blog_id=? order by created_at desc', blog_id)
		return dict(blog_id=blog_id, comments=comments)
	raise APIValueError('blog_id', 'blog_id cannot be empty')


@api 
@post('/api/blogs/:blog_id/comments')
def api_create_comment(blog_id):
	'''
	创建评论
	'''
	i = ctx.request.input(content='')
	content = i.content.strip()
	if not content:
		raise APIValueError('content', 'content cannot be empty')
	user = ctx.request.user
	comment = Comment(blog_id=blog_id, user_id=user.id, user_name=user.name, user_image=user.image, content=content)
	comment.insert()
	return comment 

@api 
@post('/api/comments/:comment_id/delete')
def api_delete_comment(comment_id):
	'''
	删除评论
	'''
	user = ctx.request.user
	if not user:
		raise APIPermissionError('Permission denied.')
	comment = Comment.get(comment_id)
	if comment is None:
		raise APIResourceNotFoundError('Comment')
	if comment.user_id != user.id and user.admin==False:
		raise APIPermissionError('Permission denied.')

	comment.delete()
	return dict(comment_id=comment_id)


