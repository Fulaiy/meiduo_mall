from rest_framework import serializers
from django_redis import get_redis_connection

class ImageCodeCheckSerializer(serializers.Serializer):
    """
    图片验证码校验序列化器
    """
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        """
        校验
        """
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        # 查询真实图片验证码
        redis_conn = get_redis_connection('verify_codes')
        real_text = redis_conn.get('img_%s'%image_code_id)

        if not real_text:
            raise serializers.ValidationError("图片验证码无效")

        # 删除图片验证码
        redis_conn.delete('img_%s'%image_code_id)

        # 比较图片验证码
        real_text = real_text.decode()
        if real_text.lower() != text.lower():
            raise serializers.ValidationError("图片验证码错误")

        # 判断是否在60秒内发送过短信
        # 在提供序列化器对象的时候，rest framework会向对象的
        # context属性补充三个数据：request format view

        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get("send_flag_%s"%mobile)

        return attrs

