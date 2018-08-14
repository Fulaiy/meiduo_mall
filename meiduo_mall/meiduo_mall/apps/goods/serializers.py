from rest_framework import serializers

from goods.search_indexes import SKUIndex
from .models import SKU
from drf_haystack.serializers import HaystackSerializer

class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    # SKUIndexSerializer序列化器中的object字段是用来向前端返回数据时序列化的字段。
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')