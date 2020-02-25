'''
	QQ用户黄页的后端
'''

from flask import Flask
from flask import request
import json
import pymysql
app = Flask(__name__)

__sql = pymysql.connect(
	host = "localhost",
	user = 'sel',
	password = '123456',
	database = 'qq',
	charset = 'utf8mb4'
)
cursor = __sql.cursor();

def sql_query(cmd, cursor):
	cursor.execute(cmd);
	ret = cursor.fetchall();
	return ret;

@app.route('/furry')
def index():
	with open('web/index.html', encoding = 'utf8') as f:
		return f.read();

@app.route('/nav.js')
def nav_js():
	with open('web/nav.js', encoding = 'utf8') as f:
		return f.read();

def parse_str(s):
	if(s == ''):
		return 'is not null'
	else:
		return " = '" + s + "'"

def parse_int(i):
	if(i == ''):
		return 'is not null'
	else:
		return i

@app.route('/sql')
def sql():
	city = request.args.get('city');
	province = request.args.get('province');
	age = request.args.get('age');
	gid = request.args.get('gid');
	deg = request.args.get('deg');
	cmd = 'select id, nick, gender, age, addr, h_addr, pic from ';
	cmd += ' (select * from qq_users where id in (select id from qq_groupmembers group by id having count(*) > ' + str(deg) +')) as t'
	cmd += ' where '
	l = 0
	if(city != ''):
		cmd += ' (city = \'' + city + '\' or h_city  = \'' + city + '\') '
		l = 1
	if(province != ''):
		if(l):
			cmd += ' and '
		cmd += ' (province = \'' + province + '\' or h_province = \'' + province + '\') '
		l = 1
	if(age != ''):
		if(l):
			cmd += ' and '
		cmd += ' (age ' + age + ' ) '
	if(gid != ''):
		cmd = 'select u.id, u.nick, u.gender, u.age, u.addr, u.h_addr, u.pic from qq_users u, qq_groupmembers gm'
		cmd += ' where gm.gid = ' + str(gid) + ' and gm.id = u.id'
	print(cmd);
	return json.dumps(sql_query(cmd, cursor));


app.run(debug=True)

cursor.close();