#-*- coding:utf-8 -*-
from proxydb import r
import threading
import functools
import sys

INT_OR_TERM=False
lock=threading.Lock()

def with_lock(func):
	@functools.wraps(func)
	def wrapper(*arg,**kw):
		lock.acquire()
		res=func(*arg,**kw)
		lock.release()
		if isinstance(res,tuple):
			return res[0],res[1]
		elif:
			return res
	return wrapper
	
@with_lock	
def pop(key,ws=False):
	'''
	从任务池或代理池左侧获得第一个元素，并删除；
	'''
	tp=r.type(key).decode('ascii')
	if tp=='list':
		return r.lpop(key).decode('ascii')
	elif tp=='zset':
		if ws:
			ele,score=r.zrange(key,0,0,withscores=ws)[0]
			r.zrem(key,ele)
			return ele.decode('ascii'),score
		else:
			ele=r.zrange(key,0,0)[0]
			r.zrem(key,ele)
			return ele.decode('ascii')
	else:
		print('只接受列表（list）或有序集合（zset）!')

@with_lock
def push(key,value,score=None):
	'''
	向任务池右侧添加一个元素；或向代理池添加一个元素并自动排序；
	'''
	tp=r.type(key).decode('ascii')
	if tp=='list' or score is None:
		r.rpush(key,value)
	elif tp=='zset' or not score is None:
		r.zadd(key,value,score)

@with_lock
def pool_del(key):
	'''
	删除一个任务池或代理池；
	'''
	r.delete(key)

def copy_proxy(dest_key,key):
	'''
	复制一个代理池
	'''
	r.zunionstore(dest_key,{key:0,dest_key:1})
	
def pool_empty(key):
	'''
	检验代理池或任务池是否已空
	'''
	if r.exists(key):
		return False
	else:
		return True

# def pool_swallow(key,thres):
	# '''
	# 检验代理池是否代理数过少
	# '''
	# if r.zcard(key)<thres:
		# return True
	# else:
		# return False

def cprint(*args):
	print(*args)
	sys.stdout.flush()