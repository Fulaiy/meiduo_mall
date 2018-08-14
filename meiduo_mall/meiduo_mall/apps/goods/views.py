from django.shortcuts import render
from rest_framework.generics import ListAPIView

from goods.models import SKU
from .serializers import SKUSerializer, SKUIndexSerializer
from rest_framework.filters import OrderingFilter
from drf_haystack.viewsets import HaystackViewSet


class SKUListView(ListAPIView):
    """sku列表数据"""
    serializer_class = SKUSerializer
    # REST framework 提供了对于排序的支持 OrderingFilter
    filter_backends = (OrderingFilter,)
    # 使用ordering_fields属性来指明进行排序的字段
    ordering_fields = ('create_time', 'price', 'sale')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class SKUSearchViewSet(HaystackViewSet):
    """SKU搜索"""
    # 指明要使用的检索类
    index_models = [SKU]
    # 通过序列化器指明要返回的字段
    serializer_class = SKUIndexSerializer


