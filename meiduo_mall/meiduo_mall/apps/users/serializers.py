import re

from rest_framework import serializers
from rest_framework.settings import api_settings

from goods.models import SKU
from users import constants
from users.models import User, Address

from django_redis import get_redis_connection
from celery_tasks.email.tasks import send_verify_email

class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    # write_only=True 只能写不能读 意思就是不能把密码给别人看
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    # 增加token字段
    token = serializers.CharField(label='登录状态token', read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }


    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value


    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':  # 注意是字符串格式的
            raise serializers.ValidationError('请同意用户协议')
        return value


    def validate(self, data):
        # 判断两次密码
        print(data['password2'])
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s'%mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():   # 注意要解码
            raise serializers.ValidationError('短信验证码错误')

        return data

    def create(self, validated_data):
        """创建用户"""
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        user = super().create(validated_data)

        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()

        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user



class UserDetailSerializer(serializers.ModelSerializer):
    """用户详细信息序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """邮箱序列化器"""
    class Meta:
        model = User
        fields = ('email', 'email_active')
        extra_kwargs = {
            'email':{
                'required':True
            }
        }


    def update(self, instance, validated_data):
        email = validated_data['email']
        instance.email = email
        # 生成激活url
        verify_url = instance.generate_verify_email_url()
        # 发送邮件 使用异步celery
        send_verify_email(email,verify_url)

        instance.save()

        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """用户地址序列化器"""
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        # 不需要显示的字段
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')
        return value


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)


class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """添加用户浏览历史序列化器"""
    sku_id = serializers.IntegerField(label='商品SKU编号', min_value=1)

    def validate_sku_id(self, value):
        """检验sku_id是否存在"""
        try:
            SKU.objects.get(id=value)
            # print('lll')
        except SKU.DoesNotExist:
            raise serializers.ValidationError("该商品不存在")
        return value

    def create(self, validated_data):
        """保存记录到redis
            格式：history_user_id:[sku_id]
            第一步：获取user_id
            第二步：获取sku_id
            第三步：保存到redis
            第四步：返回数据
        """
        # 怎样获取user_id 提供序列化器对象的时候
        # 对象的context属性包含：request,format,view 三个数据
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']

        conn = get_redis_connection('history')
        p = conn.pipeline()
        # 删除已经存在的本商品浏览记录 count=0 删除所有的这个商品记录，count>0 从左到右查询 删除count的值的个数 count<0 反之
        p.lrem('history_%s'%user_id, 0, sku_id)
        # 添加新的浏览记录 lpush 在列表的左边加入 rpush 反之
        # 最新的记录在左边
        p.lpush('history_%s'%user_id, sku_id)
        # 只保存最多五条数据
        p.ltrim('history_%s'%user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT-1)

        p.execute()
        # print('kkk')

        return validated_data