import random

from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

# from celery_tasks.sms.yuntongxun import CCP
from meiduo_mall.libs.captcha.captcha import captcha
from varifications import serializers
from . import constants

from celery_tasks.sms.tasks import send_sms_code

class ImageCodeView(APIView):
    """
    图片验证码
    """

    def get(self,request,image_code_id):
        # 利用第三方库captcha 生成验证码图片
        text, image = captcha.generate_captcha()
        print(text)

        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s"%image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type="image/jpg")


class SMSCodeView(GenericAPIView):
    """
    短信验证码
    传入参数：
        mobile, image_code_id, text
    """

    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self,request,mobile):
        """
        创建短信验证码
        """
        # 判断图片验证码 判断是否在60秒内发送过短信
        serializer = self.get_serializer(data = request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = "%06d"%random.randint(0,999999)
        print(sms_code)

        redis_conn = get_redis_connection('verify_codes')

        # 使用管道来存储操作的命令，pipeline相当于队列
        # 存储所有的操作，然后一次执行，减少redis的操作次数
        p1 = redis_conn.pipeline()
        # 保存生成的短信验证码
        p1.setex('sms_%s'%mobile,constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送的记录
        p1.setex('send_flag_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行管道中的命令
        p1.execute()

        # 发送短信验证码
        # ccp = CCP()
        # ccp.send_template_sms(mobile,sms_code,constants.TEMP_ID)
        send_sms_code.delay(mobile,sms_code,constants.TEMP_ID)

        # 返回
        return Response({'message':'ok'})