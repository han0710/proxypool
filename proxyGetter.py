#-*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import logging
import time
import proxyController as c
from proxydb import r
import random

class baseC(object):
	'''
	爬虫基类；
	kw接受参数：page_num
	'''
	def __init__(self,task_name,use_proxy=True,**kw):
		# 属性
		self._tName=task_name
		self._uKey='%s-urls'%task_name
		self._user_agent='Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'
		if use_proxy:
			self._pKey='%s-proxies'%task_name
		else:
			self._pKey=None
		if kw.get('page_num'):
			self._pageNum=kw.get('page_num')
	    
		# 方法
		self.add_urls()
		if use_proxy:
			self.add_proxies()
		
	def add_urls(self):
		'''
		向任务池添加任务；
		1.如果任务池不存在，则初始化
		2.如果任务池存在，则添加
		'''
		pass
	
	def add_proxies(self):
		'''
		向代理池添加代理；
		1.如果代理池不存在，则初始化
		2.如果代理池存在，则添加
		'''
		pass 
		
	def _pageC(self):
		'''
		1.构造请求
		2.获得响应
		3.解析网页
		4.获取数据
			[2-4].1. 如果响应/解析/数据异常，则归还本任务
		5.归还代理
			5.1. 如果未使用代理，则跳过
		6.添加新链
			6.1. 如果无需动态添加任务链接，则跳过
		'''
		pass
		
	def end(self):
		if not c.pool_empty(self._uKey):
			i=input('是否删除任务池？（Y/N）：')
			if i=='Y':
				c.pool_del(self._uKey)
		if not c.pool_empty(self._pKey):
			j=input('是否删除代理池？（Y/N）：')
			if j=='Y':
				c.pool_del(self._pKey)
				
	def start(self):
		while True:
			self._pageC()
			time.sleep(random.uniform(10,15))
			if c.pool_empty(self._uKey) or c.INT_OR_TERM:
				break
			if c.pool_empty(self._pKey) and self._pKey is not None:
				self._pKey=None	
	
		if c.INT_OR_TERM:
			print('收到SIGINT或SIGTERM信号，退出。')
		else:
			print('任务已完成，退出。')
			
class xiciC(baseC):
	def add_urls(self):
		if c.pool_empty(self._uKey):
			base_url='http://www.xicidaili.com/nn'
			n=0
			while n<=self._pageNum:
				n+=1
				url='%s/%s'%(base_url,n)
				c.push(self._uKey,url)
	
	def add_proxies(self):
		c.copy_proxy(self._pKey,'http-valid')
			
	def _pageC(self):
		# 构造请求
		url=c.pop(self._uKey)
		print('任务开始：%s正在被处理。'%url)
		headers={'user-agent':self._user_agent}
		try:
			if self._pKey is not None:
				proxy,score=c.pop(self._pKey,ws=True)
				proxies={'http':'http://%s'%proxy}
				#获得响应
				page=requests.get(url,headers=headers,proxies=proxies)
			else:
				page=requests.get(url,headers=headers)
			# 解析网页
			soup=BeautifulSoup(page.text,'html.parser')
			trs=soup.find('table',{'id':'ip_list'}).findAll('tr')
			for tr in trs[1:]:
				tds=tr.findAll('td')
				ip=tds[1].text.strip()
				port=tds[2].text.strip()
				protocol=tds[5].text.strip()
				
				item='%s:%s'%(ip,port)
				print('任务成功：得到IP>%s。'%item)
				# 获取数据
				if protocol=='HTTP':
					c.push('http-proxy',item,0)	
				if protocol=='HTTPS':
					c.push('https-proxy',item,0)
			# 归还代理			
			if self._pKey is not None:
				c.push(self._pKey,proxy,score+1)
		except Exception as e:
			logging.exception(e)
			# 归还任务
			print('任务失败：%s已归还。'%url)
			c.push(self._uKey,url)

class kuaiC(baseC):
	def add_urls(self):
		if c.pool_empty(self._uKey):
			base_url='http://www.kuaidaili.com/free/inha'
			n=0
			while n<=self._pageNum:
				n+=1
				url='%s/%s'%(base_url,n)
				c.push(self._uKey,url)
	
	def add_proxies(self):
		c.copy_proxy(self._pKey,'http-valid')
			
	def _pageC(self):
		# 构造请求
		url=c.pop(self._uKey)
		print('任务开始：%s正在被处理。'%url)
		headers={'user-agent':self._user_agent}
		try:
			if self._pKey is not None:
				proxy,score=c.pop(self._pKey,ws=True)
				proxies={'http':'http://%s'%proxy}
				#获得响应
				page=requests.get(url,headers=headers,proxies=proxies)
			else:
				page=requests.get(url,headers=headers)
			# 解析网页
			soup=BeautifulSoup(page.text,'html.parser')
			trs=soup.find('table',{'id':'ip_list'}).findAll('tr')
			for tr in trs[1:]:
				tds=tr.findAll('td')
				ip=tds[0].text.strip()
				port=tds[1].text.strip()
				protocol=tds[3].text.strip().split(',')
				protocol=[i.strip() for i in protocol]
				
				item='%s:%s'%(ip,port)
				print('任务成功：得到IP>%s。'%item)
				# 获取数据
				if 'HTTP' in protocol:
					c.push('http-proxy',item,0)	
				if 'HTTPS' in protocol:
					c.push('https-proxy',item,0)
			# 归还代理			
			if self._pKey is not None:
				c.push(self._pKey,proxy,score+1)
		except Exception as e:
			logging.exception(e)
			# 归还任务
			print('任务失败：%s已归还。'%url)
			c.push(self._uKey,url)	
			
class sfipC(baseC):		
	def add_urls(self):
		if c.pool_empty(self._uKey):
			base_url='http://superfastip.com/welcome/getips'
			n=0
			while n<=self._pageNum:
				n+=1
				url='%s/%s'%(base_url,n)
				c.push(self._uKey,url)
	
	def add_proxies(self):
		c.copy_proxy(self._pKey,'http-valid')
			
	def _pageC(self):
		# 构造请求
		url=c.pop(self._uKey)
		print('任务开始：%s正在被处理。'%url)
		headers={'user-agent':self._user_agent}
		try:
			if self._pKey is not None:
				proxy,score=c.pop(self._pKey,ws=True)
				proxies={'http':'http://%s'%proxy}
				#获得响应
				page=requests.get(url,headers=headers,proxies=proxies)
			else:
				page=requests.get(url,headers=headers)
			# 解析网页
			soup=BeautifulSoup(page.text,'html.parser')
			trs=soup.find('table',{'id':'ip_list'}).findAll('tr')
			for tr in trs[:]:
				tds=tr.findAll('td')
				ip=tds[1].text.strip()
				port=tds[2].text.strip()
				protocol=tds[5].text.strip()
				
				item='%s:%s'%(ip,port)
				print('任务成功：得到IP>%s。'%item)
				# 获取数据
				if protocol=='HTTP':
					c.push('http-proxy',item,0)	
				if protocol=='HTTPS':
					c.push('https-proxy',item,0)
			# 归还代理			
			if self._pKey is not None:
				c.push(self._pKey,proxy,score+1)
		except Exception as e:
			logging.exception(e)
			# 归还任务
			print('任务失败：%s已归还。'%url)
			c.push(self._uKey,url)

	
	
	
		