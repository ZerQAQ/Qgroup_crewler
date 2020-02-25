#!/usr/bin/python3
# encoding=utf-8

import time;
import json
import urllib.request
import random
import html
import traceback

def get_proxy():
	print('getting_ip...');
	s = urllib.request.urlopen('http://127.0.0.1:5010/get/');
	return (json.loads(s.read())['proxy']);

def delete_proxy(proxy):
    s = s = urllib.request.urlopen("http://127.0.0.1:5010/delete/?proxy={}".format(proxy));

def make_proxies(ip):
	return {'http': 'http://' + ip,
			'https': 'https://' + ip};

def cookie_dict_to_str(**cookie):
	return ''.join([i[0] + '=' + i[1] + '; ' for i in cookie.items()]);

def make_bkn(skey, __cache={}, **cookie):
    if skey in __cache:
        return __cache[skey]
    tk = 5381
    for c in skey:
        tk += (tk<<5) + ord(c)
    tk &= 0x7fffffff
    __cache[skey] = tk
    return tk

def make_g_tk(p_skey, __cache={}, **cookie):
    if p_skey in __cache:
        return __cache[p_skey]
    tk = 5381
    for c in p_skey:
        tk += (tk<<5) + ord(c)
    tk &= 0x7fffffff
    __cache[p_skey] = tk
    return tk

def make_url(url, **args):
	return url + '?' + '&'.join([i[0] + '=' + str(i[1]) for i in args.items()]);

def get_time(t):
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime((t)));

def load_json_file(fn, pre = 'data/'):
	f = open(fn, 'r', encoding='utf8');
	ret = json.loads(f.read());
	f.close();
	return ret;

def save_json_file(fn, d, pre = 'data/'):
	f = open(pre + fn, 'w', encoding='utf8');
	f.write(json.dumps(d));
	f.close();

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'
qqun_role = ['群主', '管理员', '群员'];
qqun_posid = load_json_file('posid.txt', pre = '')
qqun_genderid = {0: '', 1: '男', 2: '女'}
interval = 2;
interval_shake = 0.5;
timeout_sec = 2

def get_random_num():
	return interval + (random.random() - 0.5) * interval_shake;

def try_open_url(req, proxies):
	p_handler = urllib.request.ProxyHandler(proxies);
	opener = urllib.request.build_opener(p_handler);
	s = opener.open(req, timeout = timeout_sec);
	return s;

def open_url(req, log):
	try_n = 0
	while(1):
		if(try_n >= 5):
			return -1;
		try:
			try_n += 1;
			s = urllib.request.urlopen(req, timeout = timeout_sec);
			return s;
		except Exception as e:
			log(traceback.format_exc())
			log(str(e))
		finally:
			pass;
		

class Media:
	def __init__(self, url):
		self.url = url;

	def open(self):
		req = urllib.request.Request(self.url, headers = {'User-Agent': UA})
		d = urllib.request.urlopen(req);
		return d.read();

class User:
	def __init__(self, id, cookie, log_func = print):
		self.log = log_func
		self.id = id;
		self.fail = 0; #0 正常 1 网络错误 2 曲奇过期
		self.cant = 0;
		self.cookie = cookie;
		self.parse(id);
	
	def parse(self, id): #查找好友接口
		time.sleep(get_random_num());
		url = make_url('http://cgi.find.qq.com/qqfind/buddy/search_v3',
						keyword = id,
						ldw = make_bkn(**self.cookie));
		
		req = urllib.request.Request(url, headers = {'Cookie': cookie_dict_to_str(**self.cookie), 'User-Agent': UA})
		st = time.time();

		s = open_url(req, log = self.log);
		if(s == -1):
			self.fail = 1;
			return;
		ed = time.time();
		dr = json.loads(s.read().decode(errors = 'surrogateescape'));
		if(dr['retcode'] == 100000):
			self.fail = 2;
			return;
		if((dr['retcode'] == 0 and 'count' in dr['result'] and dr['result']['count'] == 0) or dr['retcode'] == 13):
			# 13 ?
			self.cant = 1;
			return;
		try:
			d = dr['result']['buddy']['info_list'][0];
			self.phone = d['phone'];
			self.gender = qqun_genderid[d['gender_id']];
			self.birthday = str(d['birthday']['year']) + '-' + str(d['birthday']['month']) + '-' + str(d['birthday']['day']);
			self.birth_year = d['birthday']['year'];
			self.birth_month = d['birthday']['month'];
			self.birth_day = d['birthday']['day'];
			self.age = 2020 - int(d['birthday']['year']);
			self.college = d['college'];
			self.id = d['uin'];
			self.country = d['country'];
			self.province = d['province'];
			self.city = d['city'];
			self.pic_url = d['url'];
			self.pic = Media(self.pic_url);
			self.lnick = html.unescape(d['lnick']);
			if(len(self.lnick) > 150):
				self.lnick = self.lnick[0:150];

			if(d['h_country'] != '1'):
				self.h_country = d['h_country'];
			else:
				self.h_country = '中国';
			if(str(d['h_province']) in qqun_posid['p']):
				self.h_province = qqun_posid['p'][str(d['h_province'])];
			else:
				self.h_province = d['h_province'];
				self.log('h_province id ' + str(d['h_province']) + ' is not find.')
			try:
				self.h_city = qqun_posid['c'][self.h_province][str(d['h_city'])];
			except:
				self.h_city = d['h_city'];
				self.log('h_city id ' + str(d['h_city']) + ' is not find.')

			self.nick = html.unescape(d['nick']);
			if(len(self.nick) > 50):
				self.nick = self.nick[0:50];
			self.addr = self.country + ' ' + self.province + ' ' + self.city;
			self.h_addr = self.h_country + ' ' + self.h_province + ' ' + self.h_city;
		except Exception as e:
			self.log('[ERROR]Unexpected ERROR')
			self.log(str(e))
			self.log(traceback.format_exc())
			self.log(str(dr))

	def parse2(self, id): #QQ空间接口
		time.sleep(get_random_num(1, 2));
		url = make_url('https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all',
						uin = id,
						vuin = cookie['uin'][1:],
						fupdate = 1,
						g_tk = make_g_tk(**self.cookie));
		req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**self.cookie), 'User-Agent': UA});
		s = open_url(req, log = self.log);
		dr = json.loads(s.read().decode(errors = 'surrogateescape')[10:-2]);
		if(dr['message'] != '获取成功'):
			self.fail = 1;
			return;
		d = dr['data'];
		self.nick = html.unescape(d['nickname']);
		if(len(self.nick) > 50):
			self.nick = self.nick[0:50];
		self.gender = qqun_genderid[d['sex']];
		self.age = d['age'];
		self.birthday = str(d['birthyear']) + '-' + d['birthday'];
		self.country = d['country'];
		self.province = d['province'];
		self.city = d['city'];
		self.h_country = d['hco'];
		self.h_province = d['hp'];
		self.h_city = d['hc'];
		self.addr = self.country + ' ' + self.province + ' ' + self.city;
		self.h_addr = self.h_country + ' ' + self.h_province + ' ' + self.h_city;

	def get_tuple(self):
		return (self.id, self.nick, self.country, self.province,
		self.city, self.addr, self.h_country, self.h_province, self.h_city,
		self.h_addr, self.pic_url, self.gender, self.phone, self.birthday,
		self.birth_year, self.birth_month, self.birth_day,
		self.college, self.age, self.lnick);

	def get_tuple2(self):
		return (self.id, self.nick, self.country, self.province,
		self.city, self.addr, self.h_country, self.h_province, self.h_city,
		self.h_addr, self.gender, self.age);

	def __str__(self):
		s = self.nick + '(' + str(self.id) + ') ' + self.gender + '\n';
		s += '所在地: ' + self.country + ' ' + self.province + ' ' + self.city + '\n';
		s += '故乡: ' + self.h_country + ' ' + self.h_province + ' ' + self.h_city + '\n';
		s += '生日: ' + time.strftime("%Y-%m-%d", time.localtime((self.birthday))) + '\n';
		s += '年龄: ' + str(2020 - self.birthday['year']) + '\n';
		return s;

class Member:
	def __init__(self, data):
		self.parse(data);
	
	def parse(self, data):
		self.id = data['uin'];
		self.nick = html.unescape(data['nick']);
		self.card = html.unescape(data['card']);
		self.role = data['role']; #0群主 1管理员 2群员
		self.join_time = data['join_time'];
		self.last_speak_time = data['last_speak_time'];
		self.lv = data['lv'];
		self.qage = data['qage'];
	
	def __str__(self):
		s = qqun_role[self.role] + ' ' + self.nick + '(' + str(self.id) + ')\n'
		s += '群昵称: ' + self.nick + '\n'
		s += '等级/分数: ' + str(self.lv['level']) + '/' + str(self.lv['point']) + '\n'
		s += '入群时间: ' + get_time(self.join_time) + '\n'
		s += '最后发言时间: ' + get_time(self.last_speak_time) + '\n'
		s += 'Q龄: ' + str(self.qage) + '\n';
		return s;


class Group:
	def __init__(self, data = {}, id = None, cookie = {}, log_func = print):
		self.cookie = cookie
		self.fail = 0
		self.log = log_func
		if(id != None):
			self.parse(data = {'gc': id})
		else:
			self.parse(data);

	def parse(self, data):
		self.id = data['gc'];
		if('gn' in data):
			self.name = html.unescape(data['gn']);
		if('owner' in data):
			self.ownerid = data['owner'];
		self.members = [];
		self.users = [];
		self.loaded = 0;
		self.membern = 5000;
		self.notd = 1;

	def load(self):
		self.load_member_list();

	def load_user_list(self):
		for elm in self.members:
			self.users.append(User(elm.id));

	def load_member_list(self, t = 1000):
		self.loaded = 1;
		getn = 0;
		while(True):
			t -= 1;
			if(getn == 0):
				self.log("loading " + str(getn) + '~' + str(getn + 20));
			else:
				self.log("loading " + str(getn) + '~' + str(getn + 20) + '/' + str(self.membern));
			
			'''
			try:
				d = try_load_json_file(str(self.id) + 'memberdata-' + str(getn));
			except:
			'''
			time.sleep(get_random_num());
			url = make_url('https://qun.qq.com/cgi-bin/qun_mgr/search_group_members',
							gc = self.id,
							st = getn,
							end = min(getn + 20, self.membern - 1),
							sort = 11,
							bkn = make_bkn(**self.cookie));
			req = urllib.request.Request(url, headers = {'Cookie': cookie_dict_to_str(**self.cookie), 'User-Agent': UA});
			s = open_url(req, log = self.log);
			if(s == -1):
				self.fail = 1
				return;
			d = json.loads(s.read().decode(errors = 'surrogateescape'));
			#save_json_file(str(self.id) + 'memberdata-' + str(getn), d);
			self.membern = d['count'];
			if(t == 0):
				break
			for elm in d['mems']:
				self.members.append(Member(elm));
			getn += 21;
			if(self.membern <= getn):
				break;
	
	def get_members_tuple(self):
		if(self.loaded == 0):
			self.load_member_list();
		ret = [];
		for elm in self.members:
			ret.append((elm.id, self.id, elm.nick, elm.card,
			elm.role, get_time(elm.join_time), get_time(elm.last_speak_time), 
			elm.lv['level'], elm.lv['point'], elm.qage, elm.join_time, elm.last_speak_time));
		return ret;
	
	def get_member_list(self):
		if(self.loaded == 0):
			self.load_member_list();
		return members;

	def get_group_tuple(self):
		return (self.id, self.name, self.ownerid, self.membern);

	def __str__(self):
		s = '群名/群号: ' + self.name + '/' + str(self.id) + '\n';
		if(self.loaded):
			s += '群人数：' + str(self.membern) + '\n';
			s += '\n'.join(map(str, self.members)) + '\n';
			s += '\n'.join(map(str, self.users)) + '\n';
		return s;

class Qqun:
	def __init__(self, cookie, log_func = print):
		self.log = log_func
		self.cookie = cookie;
		self.fail = 0;
	
	def get_group_list(self):
		self.log('getting group list...');
		url = make_url('https://qun.qq.com/cgi-bin/qun_mgr/get_group_list',
						bkn = make_bkn(**self.cookie));
		
		req = urllib.request.Request(url, headers = {'Cookie': cookie_dict_to_str(**self.cookie), 'User-Agent': UA});
		s = open_url(req, log = self.log)
		if(s == -1):
			self.log('[ERROR]network error')
			self.fail = 1;
			return;
		d = json.loads(s.read().decode(errors = 'surrogateescape'));
		if(d['ec'] == 4):
			self.log('[ERROR]cookie out of date');
		l = []
		if('join' in d):
			l += d['join']
		if('manage' in d):
			l += d['manage']
		if('create' in d):
			l += d['create']
		return [ Group(data = elm, cookie = self.cookie, log_func = self.log) for elm in l ]

