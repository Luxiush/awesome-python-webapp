awesome-python-webapp
=====================

A python webapp tutorial.

### 登录界面
@view(/signin.html)
@get(/signin)
def get_signin():
    返回html页面

@api
@post(/api/authenticate)
def api_authenticate()
    验证登录界面提交的用户信息


### 注册界面
@view(register.html)
@get(/register)
def get_register():
    返回html注册页面

@api
@post(/api/register)
def api_register():
    保存用户的注册信息


### 主界面
@view(index.html)
@get(/)
def get_index():
    返回网站homepage(待定)

@view(blogs_index.html)
@get(/blogs)
def get_blogs_index():
    返回博客主界面
    显示最近发表的一页博客
 
@api
@get(/api/blogs/)
api_get_blogs_by_page():
    通过前端提供的page_num返回指定的几条blog摘要
 
blogs_index.html中的js通过api加载指定的blog


### 博客显示界面
@view(blog_disp.html)
@get(blog/:blog_id)
def get_blog_disp_frame():
    返回blog对象,根据blog生存HTML页面

@api
@get(/api/comments/:blog_id)
def api_get_comments_by_id():
    返回对应blog的评论

blog_disp.html中的js通过api获取blog对应的`评论`

@api
@post(/api/comments/)
def api_post_comment():
    提交评论
    

### 博客编辑界面
@view(blog_edit.html)
@get(/blogs/:blog_id/edit)
def get_blog_edit():
    返回html页面
    
@api
@get(/api/blog/:blog_id)
def api_get_blog_by_id():
    返回对应blog的详情

@api
@post(/api/blogs/edit)
def post_blog():
    """提交博客(编辑和新建),编辑还需传入一个blog_id"""



### 发表博客界面















