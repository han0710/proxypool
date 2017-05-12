#-*- coding:utf-8 -*-
from proxyGetter import xiciC,kuaiC,sfipC
from proxyRefiner import refine_proxy
import proxyController as c
from proxydb import r
import threading
import signal
import time

def crawl_ip():
	xici=xiciC('xici',page_num=100)
	kuai=kuaiC('kuai',page_num=100)
	sfip=sfipC('sfip',page_num=45)
	
	threads=[]
	threads.extend(multi_threads(3,xici.start))
	threads.extend(multi_threads(3,kuai.start))
	threads.extend(multi_threads(3,sfip.start))
	threads_join(threads)
	
	xici.end()
	kuai.end()
	sfip.end()
	
def validate_ip():
	threads=[]
	threads.extend(multi_threads(5,refine_proxy,args=('http',)))
	threads.extend(multi_threads(5,refine_proxy,args=('https',)))
	threads_join(threads)

def update_ip():
	threads=[]
	threads.extend(multi_threads(2,refine_proxy,args=('http',True,)))
	threads.extend(multi_threads(2,refine_proxy,args=('https',True,)))
	threads_join(threads)
	
def multi_threads(thr_num,target,args=()):
	threads=[]
	for i in range(thr_num):
		thr=threading.Thread(target=target,args=args)
		threads.append(thr)
		thr.daemon=True
		thr.start()
	return threads
	
def threads_join(threads):
	while True:
		alive=False
		for t in threads:
			alive=alive or t.isAlive()
		if not alive:
			break
			
def signal_handler(signum,frame):
	c.INT_OR_TERM=True
	print('收到SIGINT或SIGTERM信号，中断多线程。')

if __name__=='__main__':
	signal.signal(signal.SIGINT,signal_handler)
	signal.signal(signal.SIGTERM,signal_handler)
	
	c.INT_OR_TERM=False
	
	t1=time.time()
	# 抓取
	crawl_ip()
	# 验证有效性
	validate_ip()
	# 更新
	update_ip()
	timeused=time.time()-t1
	print('任务完成，总耗时%f.3秒'%timeused)
	
