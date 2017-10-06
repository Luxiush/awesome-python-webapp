# coding: utf-8
#fabfile.py
import os, re 
from datetime import datetime 

from fabric.api import *

# 登录服务器的用户名
env.user = 'luxiushun'
env.sudo_user = 'root'
env.hosts = ['192.168.201.222']
env.password = '14353222-vm'

db_user = 'root'
db_password = '14353222'

_TAR_FILE = 'dist-awesome.tar.gz'

def build():
	'''
	打包工程
	'''
	includes = ['static', 'templates', 'transwarp', '*.py']
	excludes = ['test', '.*', '*.pyc', '*.pyo']
	local('rm -f dist/%s' % _TAR_FILE)

	with lcd(os.path.join(os.path.abspath('.'), 'www')):
		cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
		cmd.extend(['--exclude=\'%s\''% ex for ex in excludes])
		cmd.extend(includes)
		local(' '.join(cmd))


_REMOTE_TMP_TAR = '~/srv/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '~/srv/awesome'

def deploy():
	'''
	解压工程
	'''
	# 上传
	newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')
	run('rm -f %s' % _REMOTE_TMP_TAR)
	put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)

	# 解压
	with cd(_REMOTE_BASE_DIR):
		sudo('mkdir %s'% newdir)
	with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
		sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)

	# 重置软链接 
	with cd(_REMOTE_BASE_DIR):
		sudo('rm -f www')
		sudo('ln -s %s www' % newdir)

	# 重启Python服务器和nginx服务器
	with settings(warn_only=True):
		sudo('supervisorctl stop awesome')
		sudo('supervisorctl start awesome')
		sudo('/etc/init.d/nginx reload')

