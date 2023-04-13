# #coding=utf-8
from email.mime.text import MIMEText#專門傳送正文
from email.mime.multipart import MIMEMultipart#傳送多個部分
from email.mime.application import MIMEApplication#傳送附件
import smtplib #傳送郵件


# 郵件發送地址＆授權碼＆內容
server_address = 'smtp.gmail.com'   #伺服器地址
send_user = 'learningddeep@gmail.com'   #發件人
receive_users = ['vxh440@gmail.com', 'racoffee33@gmail.com']
password = 'rxbhqplrguseawyb'   #授權碼/密碼（google > 安全性 > 應用程式密碼）

subject = 'Panda crawler daily report'  #郵件主題
email_text = 'Hi! this is your panda crawler daily report'   #郵件正文
file = 'out.txt' #附件路徑

# 連線設定
server = smtplib.SMTP('smtp.gmail.com',587) # STMP session
smtp_ttls = server.starttls() # start tls for security
smtp_login = server.login(send_user, password) # login


# 構造一個郵件體：正文 附件
msg = MIMEMultipart()
msg['Subject']=subject    #主題
msg['From']=send_user      #發件人
msg['To']=receive_users           #收件人

# 構建正文
part_text=MIMEText(email_text)
msg.attach(part_text)             #把正文加到郵件體裡面去

# 構建郵件附件
part_attach1 = MIMEApplication(open(file,'rb').read())   #開啟附件
part_attach1.add_header('Content-Disposition','attachment',filename=file) #為附件命名
msg.attach(part_attach1)   #新增附件


# # 傳送郵件 SMTP
server.sendmail(send_user, receive_users, msg.as_string())  # 傳送郵件
print('郵件傳送成功！')
