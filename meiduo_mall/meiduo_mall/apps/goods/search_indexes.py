from haystack import indexes
from .models import SKU

class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """SKU索引数据模型类"""
    # 创建搜索的关键词
    # document指明text为搜索的关键词
    # use_template 在模板文件中指明要建立索引的字段
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
         """返回建立索引的模型类"""
         return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)
