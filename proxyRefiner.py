#-*- coding:utf-8 -*-
import requests
import time
import logging
from proxydb import r
import proxyController as c


def refine_proxy(protocol,refresh=False):
	if refresh:
		pKey='%s-valid'%protocol
		dKey='%s-temp'%pKey
		c.copy_proxy(dKey,pKey)
		pKey=dKey
	else:
		pKey='%s-proxy'%protocol
		
	while not (c.INT_OR_TERM or c.pool_empty(pKey)):
		proxy=c.pop(pKey)
		user_agent='Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'
		
		headers={'user-agent':user_agent}
		proxies={'%s'%protocol:'%s://%s'%(protocol,proxy)}
		t1=time.time()
		try:
			if protocol=='http':
				page=requests.get('http://www.qidian.com/',headers=headers,proxies=proxies)
			else:
				page=requests.get('https://www.baidu.com/',headers=headers,proxies=proxies)
			
			if page.status_code==200:
				timeused=time.time()-t1
				print('IP%s延时:%.3f秒,写入可用代理池。'%(proxy,timeused))
				c.push('%s-valid'%protocol,proxy,timeused)
			else:
				print('IP%s不可用，已丢弃。'%proxy)
		except Exception as e:
			logging.exception(e)
			print('IP%s不可用，已丢弃。'%proxy)
	
	if c.INT_OR_TERM:
		print('收到SIGINT或SIGTERM信号，退出。')
	else:
		print('任务已完成，退出。')
	