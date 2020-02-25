from selenium import webdriver
import json
import time
import Qqun
import sys

from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True

def get_cookie(fn):
	def if_elm_exsit(c):
		try:
			driver.find_element_by_class_name(c)
		except:
			return 0
		else:
			return 1
	
	driver = webdriver.Firefox()
	driver.get(web_url)
	try:
		time.sleep(0.5)
		driver.find_element_by_css_selector("a[cmd = login]").click();
		driver.switch_to.frame('login_frame')
		time.sleep(1)
		qrcode_img = driver.find_element_by_css_selector('#qrlogin_img')
		qrcode_url = qrcode_img.get_attribute('src')

		M = Qqun.Media(qrcode_url)
		f = open('qrcode.png', 'wb')
		f.write(M.open())
		f.close()

		#show_pic('qrcode.png')
	except:
		pass
	while(1):
		driver.switch_to.default_content()
		if(if_elm_exsit('user-nick')):
			break
		time.sleep(0.1)
	cookie = {};
	for elm in driver.get_cookies():
		cookie[elm['name']] = elm['value'];
	print(cookie);
	f = open(fn, "w");
	f.write(json.dumps(cookie));
	f.close();
	driver.quit();


fnp = sys.argv[1]
cn = sys.argv[2]
web_url = 'https://qun.qq.com/'
for i in range(int(cn)):
	fn = fnp + 'cookie/' + 'cookie' + str(i)
	get_cookie(fn)