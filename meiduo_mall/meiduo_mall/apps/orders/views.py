from decimal import Decimal
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django_redis import get_redis_connection

from goods.models import SKU
from .serializers import OrderSettlementSerializer, SaveOrderSerializer
from rest_framework.response import Response
class OrderSettlementView(APIView):
    """订单结算"""
    # 首先肯定得是认证通过的用户
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取"""
        user = request.user
        #  从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s'%user.id)
        print(redis_cart)
        cart_selected = redis_conn.smembers('cart_selected_%s'%user.id)
        print(cart_selected)
        cart = {}
        # 获取每个被勾选的sku_id 对应的 count
        for sku_id in cart_selected:
            # sku_id 为byte类型
            cart[int(sku_id)] = int(redis_cart[sku_id])
        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            # sku.count 为用户需要购买的数量
            sku.count = cart[sku.id]

        # 运费
        freight = Decimal('10.00')
        data = {
            'freight':freight,
            'skus':skus
        }
        serializer = OrderSettlementSerializer(data)

        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """保存订单(提交订单)"""
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer
