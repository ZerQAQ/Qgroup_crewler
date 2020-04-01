# qgroup_crawler (QQ群爪巴虫)

![](https://i.loli.net/2019/11/27/3Y7TBWXwzhrbGum.jpg)

目前功能主要为爬取QQ用户的群、群员以及用户资料。

# 运行环境

python3

在项目目录下执行以安装依赖。

```
pip install -r requirements.txt
```

需要sql数据库，请在m.py中的sqlcon_data中设置host等参数。

```
sqlcon_data = {
	'host' : "localhost",
	'user' : 'root',
	'password' : '123456',
	'database' : 'qq',
	'charset' : 'utf8mb4'
}
```

并在database下创建以下表：

```sql
qq_groups:
+----------+-------------+------+-----+---------+-------+
| Field    | Type        | Null | Key | Default | Extra |
+----------+-------------+------+-----+---------+-------+
| id       | bigint      | NO   | PRI | NULL    |       |
| name     | varchar(50) | YES  |     | NULL    |       |
| owner_id | bigint      | YES  |     | NULL    |       |
| membern  | int         | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+

qq_groupmembers:
+--------------------+-------------+------+-----+---------+-------------------+
| Field              | Type        | Null | Key | Default | Extra             |
+--------------------+-------------+------+-----+---------+-------------------+
| id                 | bigint      | NO   | PRI | NULL    |                   |
| gid                | bigint      | NO   | PRI | NULL    |                   |
| nick               | varchar(50) | YES  |     | NULL    |                   |
| card               | varchar(50) | YES  |     | NULL    |                   |
| role               | tinyint     | YES  |     | NULL    |                   |
| join_time          | varchar(20) | YES  |     | NULL    |                   |
| last_speak_time    | varchar(20) | YES  |     | NULL    |                   |
| lv                 | tinyint     | YES  |     | NULL    |                   |
| point              | int         | YES  |     | NULL    |                   |
| qage               | tinyint     | YES  |     | NULL    |                   |
| join_time_ts       | int         | YES  |     | NULL    |                   |
| last_speak_time_ts | int         | YES  |     | NULL    |                   |
| type               | int         | YES  |     | 0       | DEFAULT_GENERATED |
+--------------------+-------------+------+-----+---------+-------------------+

qq_users:
+-------------+--------------+------+-----+---------+-------+
| Field       | Type         | Null | Key | Default | Extra |
+-------------+--------------+------+-----+---------+-------+
| id          | bigint       | NO   | PRI | NULL    |       |
| nick        | varchar(50)  | YES  |     | NULL    |       |
| country     | varchar(20)  | YES  |     | NULL    |       |
| province    | varchar(20)  | YES  |     | NULL    |       |
| city        | varchar(20)  | YES  |     | NULL    |       |
| addr        | varchar(50)  | YES  |     | NULL    |       |
| h_country   | varchar(20)  | YES  |     | NULL    |       |
| h_province  | varchar(20)  | YES  |     | NULL    |       |
| h_city      | varchar(20)  | YES  |     | NULL    |       |
| h_addr      | varchar(50)  | YES  |     | NULL    |       |
| pic         | varchar(200) | YES  |     | NULL    |       |
| gender      | varchar(5)   | YES  |     | NULL    |       |
| birthday_st | int          | YES  |     | NULL    |       |
| birthday    | varchar(15)  | YES  |     | NULL    |       |
| college     | varchar(50)  | YES  |     | NULL    |       |
| age         | int          | YES  |     | NULL    |       |
| phone       | varchar(20)  | YES  |     | NULL    |       |
| lnick       | varchar(150) | YES  |     | NULL    |       |
| birth_year  | int          | YES  |     | NULL    |       |
| birth_month | int          | YES  |     | NULL    |       |
| birth_day   | int          | YES  |     | NULL    |       |
+-------------+--------------+------+-----+---------+-------+

users_nl: --（用于缓存未加载的用户用户）
+-------+--------+------+-----+---------+-------+
| Field | Type   | Null | Key | Default | Extra |
+-------+--------+------+-----+---------+-------+
| id    | bigint | NO   | PRI | NULL    |       |
+-------+--------+------+-----+---------+-------+
```

# 用法

## m.py

将用于抓取用户信息的cookie放在ucookie/下，命名格式为cookie0, cookie1...

将用于抓取群信息的cookie放在gcookie/下，命名格式为cookie0, cookie1...

然后创建一个main_crewler来创建一个主线程，可选的传入参数有：

 - gcn： group_crewler的线程数，默认为1，请设置成gcookie下的cookie个数。
 - ucn： users_crewler的线程数，默认为3，清设置成ucookie下的cookie格式。
 - gcd： 获取gcookie的目录。
 - ucd： 获取ucookie的目录。
 - nfg_list： not furry group list 传入一个list，其中包含禁止group_crewler抓取的群的群号。
 - fg_list： furry group lsit 传入一个list，group_crewler只会抓取这个群号在这个list中的群。

通过调用main_crewler.work()来启动主线程。

程序会在根目录下创建data和log来保存数据和日志。

## Qqun.py

通过传入cookies创建一个Qqun对象，调用get_group_list()可以获得一个list，其中包含若干个Group对象。

Group对象表示一个群，有以下属性：

 - id：群号
 - ownerid：群主Q号
 - membern：群人数

调用Group中的get_member_list()可以获得一个list，其中包含若干个Member对象。

Merber对象表示QQ群成员，有以下属性：

- id：QQ号
- nick：昵称
- card：群昵称
- role：身份（一个整数 0群主 1管理员 2群员）
- join_time：Unix时间戳 加入群的时间
- last_speak_time：Unix时间戳 最后发言时间
- lv：一个dict，lv['leve']是群等级 lv['point']是群内分数
- qage：Q龄


通过传入QQ号（int）可以创建一个User对象。
User对象代表一个QQ用户，包含以下属性：

- id：QQ号
- gender：性别
- nick：昵称
- pic：头像的url
- age：年龄
- lnick：说说
- country：所在地国家
- province：所在地省份
- city：所在地城市
- addr：所在地
- h_country：故乡国家
- h_province：故乡省份
- h_city：故乡城市
- h_addr：故乡
- phone：电话
- birthday：生日
- birth_year：生日年份
- birth_month：生日月份
- birth_dat：生日日期
- college：学校