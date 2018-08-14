from celery_tasks.main import celery_app
from meiduo_mall.libs.yuntongxun.sms import CCP

# 发送短信验证码
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code, TEMP_ID):
    ccp = CCP()
    ccp.send_template_sms(mobile,sms_code,TEMP_ID)