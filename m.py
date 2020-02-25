#!/usr/bin/python3
# encoding=utf-8

from selenium import webdriver
import json
import pymysql
import Qqun
import time
import random
import threading
import os
import traceback

sqlcon_data = {
	'host' : "localhost",
	'user' : 'root',
	'password' : '123456',
	'database' : 'qq',
	'charset' : 'utf8mb4'
}

global total_user_num
total_user_num = 0

st_time = time.time();
st_time_s = time.strftime('%Y-%m-%d %H %M %S')
def load_json_file(fn, pre = 'data/'):
	f = open(pre + fn, 'r', encoding='utf8');
	ret = json.loads(f.read());
	f.close();
	return ret;

def save_json_file(fn, d, pre = 'data/'):
	f = open(pre + fn, 'w', encoding='utf8');
	f.write(json.dumps(d));
	f.close();

def sql_query(cmd, sqlcon):
	cursor = sqlcon.cursor()
	cursor.execute(cmd);
	cursor.close()
	sqlcon.commit();
	ret = cursor.fetchall();
	return ret;

def sql_executemany(cmd, d, sqlcon):
	cursor = sqlcon.cursor()
	cursor.executemany(cmd, d);
	cursor.close()
	sqlcon.commit();

def str_g(g):
	return g.name + '(' + str(g.id) + ')';

def get_now():
	return time.strftime('%Y-%m-%d %H:%M:%S')

def get_v(l, s, i):
	while(1):
		if(s[i]):
			time.sleep(random.random())
		else:
			s[i] = 1
			ret = l[i]
			s[i] = 0
			return ret

def set_v(l, s, i, v):
	while(1):
		if(s[i]):
			time.sleep(random.random())
		else:
			s[i] = 1
			l[i] = v
			s[i] = 0
			return

def clone(l):
	ret = []
	for i in range(len(l)):
		ret.append(l[i])
	return ret

class Group_crewlar(threading.Thread):
	def __init__(self, cookie = {}, mode = 'INSERT', tid = 0, fg_list = [], nfg_list = []):
		threading.Thread.__init__(self)
		self.nfg_list = nfg_list 
		self.fg_list = fg_list 
		self.sqlcon = pymysql.connect(**sqlcon_data)
		set_v(grun, gsign, tid, 0) #是否正在运行的标志位
		set_v(gsatus, gsign, tid, 1) #1正常退出 0不正常退出
		self.tid = tid #进程ID
		self.Q = Qqun.Qqun(cookie, log_func = self.log)
		self.glistr = self.Q.get_group_list()
		self.glist = []
		self.suc = []
		self.fail = []
		if(mode == 'INSERT'):
			sql_gl = [i[0] for i in sql_query('select id from qq_groups', self.sqlcon)];
			for elm in self.glistr:
				if(elm.id in sql_gl or (fg_list != [] and elm.id not in fg_list) or elm.id in nfg_list):
					continue;
				self.glist.append(elm);
		elif(mode == 'UPDATE'): #这个模式未完成
			self.glist = self.glistr;
	
	def log(self, s): #输出日志的函数
		print('[' + get_now() + '][group_crewlar-' + str(self.tid) + ']' + s)
		fdir = 'log/' + st_time_s
		if(not os.path.exists(fdir)):
			os.mkdir(fdir)
		fn = fdir + '/group_c-' + str(self.tid) + '.txt'
		print(s, file = open(fn, 'a', encoding = 'utf8'))

	def run(self):
		set_v(grun, gsign, self.tid, 1)
		self.log('start.')
		try:
			self.work()
		finally:
			self.log('quit.')
			set_v(grun, gsign, self.tid, 0)

	def work(self):
		try:
			set_v(gsatus, gsign, self.tid, 0)
			gcmd = '''
				INSERT INTO qq_groups
				(id, name, owner_id, membern)
				VALUES
				(%s, %s, %s, %s)
			'''

			gmcmd = '''
				REPLACE INTO qq_groupmembers
				(id, gid, nick, card, role, join_time, last_speak_time, lv, point, qage, join_time_ts, last_speak_time_ts)
				VALUES
				(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			'''

			unlcmd = '''
				REPLACE INTO users_nl
				(id)
				VALUES
				(%s)
			'''
			sql_us_nl = [elm[0] for elm in sql_query('select id from users_nl', self.sqlcon)]
			sql_us = [elm[0] for elm in sql_query('select id from qq_users', self.sqlcon)]
			us_nl = []
			glen = len(self.glist);
			gn = 0;
			gmn = 0;
			for elm in self.glist:
				if(get_v(grun, gsign, self.tid) == 0):
					return
				gn += 1;
				self.log('|'.join(['[' + str(glen), str(gn) + ']']) + 'loading group ' + str_g(elm) + '...');
				elm.load_member_list();
				if(elm.fail):
					self.log('Fail to get ' + str_g(elm) + "'s info.")
					self.fail.append(elm);
					continue;
				self.log('executing sqlcmd...');
				d = elm.get_members_tuple()
				for _elm in d:
					id = _elm[0]
					if(id not in sql_us and id not in sql_us_nl):
						us_nl.append(id);
				sql_us_nl += us_nl
				sql_executemany(unlcmd, us_nl, self.sqlcon);
				us_nl.clear();
				sql_executemany(gmcmd, d, self.sqlcon)
				sql_executemany(gcmd, [elm.get_group_tuple()], self.sqlcon)
				self.suc.append(elm)

				gmn += elm.membern;
				self.log(str(gmn) + ' groupmembers loaded.');
			self.log(str(len(self.suc)) + ' group loaded.');
			if(len(self.fail) > 0):
				self.log('fail to load ' + str(len(self.fail)) + 'group.')
			set_v(gsatus, gsign, self.tid, 1)
		except Exception as e:
			self.log(traceback.format_exc())
			self.log(e)
		finally:
			self.sqlcon.commit()
			self.sqlcon.close()

class User_crewlar(threading.Thread):
	def __init__(self, id_list = [], cookie = {}, tid = 0):
		threading.Thread.__init__(self)
		self.sqlcon = pymysql.connect(**sqlcon_data)
		set_v(urun, usign, tid, 0)
		self.tid = tid
		self.id_list = id_list;
		self.cookie = cookie;
		self.suc = []
		self.fail = []
		set_v(usatus, usign, tid, 1)

	def log(self, s):
		print('[' + get_now() + '][user_crewlar-' + str(self.tid) + ']' + s)
		fdir = 'log/' + st_time_s
		if(not os.path.exists(fdir)):
			os.mkdir(fdir)
		fn = fdir + '/users_c-' + str(self.tid) + '.txt'
		print(s, file = open(fn, 'a', encoding = 'utf8'))

	def run(self):
		set_v(urun, usign, self.tid, 1)
		self.log('start.')
		self.work()
		self.log('quit.')
		set_v(urun, usign, self.tid, 0)
		self.sqlcon.commit()
		self.sqlcon.close()

	def sql(self, ins_val, del_val):
		sql_executemany(self.cmd1, ins_val, self.sqlcon)
		sql_executemany(self.cmd2, del_val, self.sqlcon)

	def work(self):
		global total_user_num
		set_v(usatus, usign, self.tid, 0)
		self.cmd1 = '''
			REPLACE INTO qq_users
			(id, nick, country, province, city, addr,
			h_country, h_province, h_city, h_addr,
			pic, gender, phone, birthday, birth_year, birth_month, birth_day,
			college, age, lnick)
			VALUES
			(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
			'''
		
		self.cmd2 = '''
			DELETE from users_nl where id = %s
			'''
		total = len(self.id_list)
		suc = 0
		fail = 0
		ins_val = []
		del_val = []
		for id in self.id_list:
			if(total != len(self.id_list)):
				self.log('[ERROR]total not equ idlistlen. ' + 'idlistlen = ' + str(len(self.id_list)))
			if(get_v(urun, usign, self.tid) == 0):
				self.log('killed by main.')
				return
			U = Qqun.User(id, self.cookie, log_func = self.log)
			self.log('|'.join(['[' + str(total), str(suc), str(fail) + ']']) + 'getting ' + str(id) + "'s info...")
			if(U.fail):
				if(U.fail == 1):
					self.log('network error.')
				elif(U.fail == 2):
					self.log('cookie fail.')
				fail += 1;
				self.fail.append((id, U.fail));
				continue
			elif(U.cant):
				self.log('cant find user.')
				fail += 1
				del_val.append(U.id)
				continue
			ins_val.append(U.get_tuple())
			del_val.append((U.id))
			suc += 1;
			if(len(ins_val) >= 5 or len(del_val) >= 5):
				total_user_num += len(ins_val)
				self.log('executing sqlcmd...')
				self.sql(ins_val, del_val)
				ins_val.clear()
				del_val.clear()
		
		if(len(ins_val) > 0 or len(del_val) > 0):
			self.log('executing sqlcmd...')
			self.sql(ins_val, del_val)
			self.log(str(suc) + ' users loaded.');
		if(fail > 0):
			self.log('fail to load ' + str(fail) + 'users.');
		set_v(usatus, usign, self.tid, 1)

class main_crewlar():
	def __init__(self, gcn = 1, ucn = 3, gcd = 'gcookie/', ucd = 'ucookie/', nfg_list = [], fg_list = []):
		self.nfg_list = nfg_list
		self.fg_list = fg_list
		self.log('initing...')
		self.gcn = gcn
		self.ucn = ucn
		self.g_crewlar = []
		self.u_crewlar = []
		self.u_list_al = []
		self.u_list_p = []
		self.sqlcon = pymysql.connect(**sqlcon_data)
		global grun
		global gsatus
		global gsign
		global urun
		global usatus
		global usign
		grun = []
		gsatus = []
		gsign = []
		urun = []
		usatus = []
		usign = []
		for i in range(gcn):
			grun.append(0)
			gsign.append(0)
			gsatus.append(1)
			gcookie = load_json_file(fn = 'cookie' + str(i), pre = gcd)
			self.g_crewlar.append(Group_crewlar(cookie = gcookie, tid = i, nfg_list = self.nfg_list, fg_list = self.fg_list))
		for i in range(ucn):
			urun.append(0)
			usign.append(0)
			usatus.append(1)
			ucookie = load_json_file(fn = 'cookie' + str(i), pre = ucd)
			self.u_crewlar.append(User_crewlar(cookie = ucookie, tid = i))
			self.u_list_p.append([])
		if(not os.path.exists('log')):
			os.mkdir('log')
		if(not os.path.exists('data')):
			os.mkdir('data')

	def get_u_nl_num(self):
		cmd = 'select count(1) from users_nl'
		nln = sql_query(cmd, self.sqlcon)[0][0]
		return nln

	def gc_finish(self): #检查group crewlar是否完成工作
		for elm in self.g_crewlar:
			if(get_v(grun, gsign, elm.tid)):
				return 0
		return 1

	def distribute(self):
		cmd = 'select id from users_nl'
		self.u_list_al = [elm[0] for elm in sql_query(cmd, self.sqlcon)]
		for elm in self.u_list_p:
			elm.clear()
		for id in self.u_list_al:
			k = id % self.ucn;
			self.u_list_p[k].append(id)


	def log(self, s):
		print('[' + get_now() + '][main-crewlar]' + s)
		fdir = 'log/' + st_time_s
		if(not os.path.exists(fdir)):
			os.mkdir(fdir)
		fn = fdir + '/main-c.txt'
		print(s, file = open(fn, 'a', encoding = 'utf8'))

	def work(self):
		try:
			self.log('start')
			self.log('launching g_crewlar...')
			for elm in self.g_crewlar:
				elm.start()
			time.sleep(5)
			while(1):
				#检查uc和gc是否正常
				self.log('checking ERROR..')
				for i in range(self.gcn):
					gc = self.g_crewlar[i]
					if(get_v(grun, gsign, gc.tid) == 0 and get_v(gsatus, gsign, gc.tid) == 0):
						self.log('[ERROR] unexpected ERROR happen in group_crewlar' + str(i))
				for i in range(self.ucn):
					uc = self.u_crewlar[i]
					if(get_v(urun, usign, uc.tid) == 0 and get_v(usatus, usign, uc.tid) == 0):
						self.log('[ERROR] unexpected ERROR happen in user_crewlar' + str(i))
				#给uc分配任务
				nln = self.get_u_nl_num()
				self.log(str(nln) + ' users not load.')
				if(nln > 0):
					self.distribute()
					for i in range(self.ucn): #ucn是线程数
						uc = self.u_crewlar[i]
						if(get_v(urun, usign, uc.tid) == 0):
							self.log('distributing u_crewlar-' + str(uc.tid) + "'s work..." )
							newuc = User_crewlar(id_list = clone(self.u_list_p[i]), #新线程
								cookie = self.u_crewlar[i].cookie,
								tid = i)
							self.u_crewlar[i] = newuc; #顶替旧线程
							self.u_crewlar[i].start()
						time.sleep(0.5)
				#任务完成
				if(self.gc_finish() and nln == 0):
					break;
				self.log('sleep.')
				time.sleep(100)
			self.log(str(total_user_num) + ' users loaded.')
			self.log('end')
		except Exception as e:
			self.log(traceback.format_exc())
			self.log(str(e))
		finally:
			for elm in self.g_crewlar:
				set_v(grun, gsign, elm.tid, 0)
			for elm in self.u_crewlar:
				set_v(urun, usign, elm.tid, 0)

def ud_us_nl():
	sqlcon = pymysql.connect(**sqlcon_data)
	d = sql_query('select distinct id from qq_groupmembers where id not in (select id from qq_users)', sqlcon)
	sql_executemany('insert into users_nl (id) values (%s)', d, sqlcon)
	sqlcon.commit()
	sqlcon.close()

try:
	#ud_us_nl()
	master = main_crewlar(fg_list = fg_list, gcn = 1)
	master.work()
finally:
	end_time = time.time();
	print('work ' + str((end_time - st_time) // 1) + ' seconds');