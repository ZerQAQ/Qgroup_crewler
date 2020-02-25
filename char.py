#!/usr/bin/python3
# encoding=utf-8

from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts import types as tp
import pymysql
import json

def load_json_file(fn, pre = 'data/'):
	f = open(pre + fn, 'r', encoding='utf8');
	ret = json.loads(f.read());
	f.close();
	return ret;

def save_json_file(fn, d, pre = 'data/'):
	f = open(pre + fn, 'w', encoding='utf8');
	f.write(json.dumps(d));
	f.close();

__sql = pymysql.connect(
	host = "localhost",
	user = 'root',
	password = '123456',
	database = 'qq',
	charset = 'utf8mb4'
)

def unique(l):
	ret = []
	for elm in l:
		if(elm not in ret):
			ret.append(elm)
	return ret

def sql_query(cmd, sqlcon):
	cursor = sqlcon.cursor();
	cursor.execute(cmd);
	ret = cursor.fetchall();
	return ret;
	cursor.close();

def age_table():
	dr = sql_query('select age from \
	(select * from qq_users where id in (select id from qq_groupmembers group by id having count(*) > 0)) as t',
	 __sql)
	age = [i[0] for i in dr]

	col = [i for i in range(0, 51)]
	aged = []
	for i in range(0, 51):
		aged.append(age.count(i))

	bar = (
	    Bar()
	    .add_xaxis(col)
	    .add_yaxis("人数", aged, label_opts=opts.LabelOpts(color= '#fff', is_show=0),
					category_gap= '10%')
	    .set_global_opts(title_opts=opts.TitleOpts(title="兽圈QQ用户年龄分布"), 
						xaxis_opts= opts.AxisOpts(split_number=1000))
		#.set_series_opts(markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max", name="最大值")],))
	)
	bar.render()
sp_city = ['北京', "上海", "重庆", "天津"]
def location_d():
	dr = sql_query('select h_city, city, gender from qq_users', __sql)
	wdr = [elm[:2] for elm in dr if elm[2] == '女']
	mdr = [elm[:2] for elm in dr if elm[2] == '男']
	d = []
	for elm in wdr:
		d += elm
	for elm in mdr:
		d += elm
	ud = unique(d)
	loca_dict = {}
	for elm in ud:
		loca_dict[elm] = 0
	for elm in d:
		loca_dict[elm] += 1
	#print([loca_dict[elm] for elm in sp_city])
	loca_dict['天津'] = 428
	loca_dict['重庆'] = 892
	loca_dict['上海'] = 1343
	loca_dict['北京'] = 1418
	loca_dict['东城'] = 0
	loca_dict = sorted(loca_dict.items(), key = lambda x:x[1], reverse=True)
	loca_dict = loca_dict[2:20];
	for (k, v) in loca_dict:
		s = '{name: ' + "'" + k + "'"
		s += ', value: ' + str(v) + '},'
	print([elm[0] for elm in loca_dict])
	print([elm[1] for elm in loca_dict])

	province_s = [elm[0] for elm in loca_dict]
	print(province_s)

	md = []
	for elm in mdr:
		md += elm
	umd = unique(md)
	mloca_dict = {}
	for elm in umd:
		mloca_dict[elm] = 0
	for elm in md:
		mloca_dict[elm] += 1
	mloca_dict['北京'] = 1080
	mloca_dict['上海'] = 1022
	mloca_dict['重庆'] = 739
	mloca_dict['天津'] = 334
	print([mloca_dict[elm] for elm in province_s])

	wd = []
	for elm in wdr:
		wd += elm
	uwd = unique(wd)
	wloca_dict = {}
	for elm in uwd:
		wloca_dict[elm] = 0
	for elm in wd:
		wloca_dict[elm] += 1
	wloca_dict['北京'] = 337
	wloca_dict['上海'] = 321
	wloca_dict['重庆'] = 153
	wloca_dict['天津'] = 94
	print([wloca_dict[elm] for elm in province_s])

	
def gender():
	dr = sql_query('select gender from qq_users', __sql);
	d = [elm[0] for elm in dr]
	print(d.count('男'))
	print(d.count('女'))

def age():
	province_s = ['广东', '浙江', '四川', '江苏', '湖南', '湖北', '山东', '福建', '广西', '河南', '辽宁', '河北', '安徽', '江西', '黑龙江', '陕西', '云南', '贵州']
	dr = sql_query('select province, h_province, age from qq_users', __sql)
	cmdp = "or".join([' province = "' + elm + '" ' for elm in sp_city])
	cmd = 'select province, h_province, age from qq_users where ' + cmdp + 'or' + cmdp.replace('province', 'h_province')
	#dr2 = sql_query(cmd, __sql)
	#dr = dr1 + dr2
	ages_dict = {}
	age_dict = {}
	for elm in province_s:
		ages_dict[elm] = []
		age_dict[elm] = []
	for elm in dr:
		if(elm[0] in province_s):
			ages_dict[elm[0]].append(elm[2])
		if(elm[1] in province_s):
			ages_dict[elm[1]].append(elm[2])
	area = [12, 16, 19, 22, 30]

	for elm in province_s:
		for i in range(4):
			al = area[i]
			ah = area[i + 1]
			v = 0
			for j in range(al, ah):
				v += ages_dict[elm].count(j)
			age_dict[elm].append(v)
		age_dict[elm].append(0)
		for i in range(4):
			age_dict[elm][4] += age_dict[elm][i]
	province_s = sorted(province_s, key = lambda x: age_dict[x][4], reverse= 1)
	print(province_s)
	for i in range(4):
		print([age_dict[elm][i] for elm in province_s])
	for i in range(4):
		print(sum( [age_dict[elm][i] for elm in province_s] ))

age_table()