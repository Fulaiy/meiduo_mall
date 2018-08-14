from django.shortcuts import render

# Create your views here.
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from oauth.exceptions import QQAPIError
from .utils import OAuthQQ
from .models import OAuthQQUser
from .serializers import OAuthQQUserSerializer

class QQAuthURLView(APIView):
    """获取QQ登录的url"""

    def get(self, request):

        next = request.query_params.get('next')
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_qq_login_url()

        return Response({'login_url': login_url})


class QQAuthUserView(CreateAPIView):
    """QQ登录的用户"""

    serializer_class = OAuthQQUserSerializer

    def get(self,request):
        """获取qq登录的用户数据"""

        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        oauth = OAuthQQ()
        # 获取用户openid
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_openid(access_token)
        except QQAPIError:
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 判断用户是否存在
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 用户第一次登录
            token = oauth.generate_save_user_token(openid)
            return Response({'access_token':token})
        else:
            # 找到用户，生成token
            user = qq_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
            # 合并购物车
            response = merge_cart_cookie_to_redis(request, user, response)

            return response


    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # 合并购物车
        response = merge_cart_cookie_to_redis(request, self.user, response)
        return response