from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject
from datetime import datetime

from django.db import models

from .models import Product, ProductHistory

"""Преобразование строки к нужному формату"""
class DateTimeFieldMS(serializers.DateTimeField):
    def to_representation(self, value):
        return value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + value.strftime("Z")


class ShopUnitImport:
    """Обмен информации с клиентом"""

    def __init__(self, id, name, parentId, type, price):
        self.id = id
        self.name = name
        self.parentId = parentId
        self.type = type
        self.price = price

"""Тип объекта"""
class ShopUnitType:
    def __init__(self, type):
        self.type = type

"""Тип запроса на импорт"""
class ShopUnitImportRequest:
    def __init__(self, items, updateDate):
        self.items = items
        self.updateDate = updateDate

"""Получение статистики"""
class ShopUnitStatisticResponse:
    def __init__(self, items):
        self.items = items

"""Сериализация статистики"""
class ShopUnitStatisticSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    parentId = serializers.CharField(allow_null=True)
    type = serializers.CharField()
    price = serializers.IntegerField(required=False, allow_null=True)
    date = serializers.CharField()

"""Сериализация объекта"""
class ProductSerializer(serializers.ModelSerializer):
    parentId = serializers.PrimaryKeyRelatedField(read_only=True)
    children = serializers.SerializerMethodField()
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        models.DateTimeField: DateTimeFieldMS,
    }
    """Определение ребенка"""
    def get_children(self, obj: Product):
        obj_children = obj.children

        if obj_children.all():
            return ProductSerializer(obj_children, many=True).data

        if obj.type == Product.Type.OFFER:
            return None
        return []

    class Meta:
        model = Product
        depth = 10
        fields = '__all__'


"""Модели для добавление категорий и товаров"""
class ProductImportSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    parentId = serializers.CharField(allow_null=True)
    type = serializers.CharField()
    price = serializers.IntegerField(required=False)

    def create(self, validated_data):
        return ShopUnitImport(**validated_data)

    def to_internal_value(self, data):
        # data['date'] = data['updateDate']

        obj = super(ProductImportSerializer, self).to_internal_value(data)
        return obj

    def to_representation(self, instance):
        return None


"""Сериализация истории объекта"""
class ShopUnitHistorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False)

    class Meta:
        model = ProductHistory
        fields = '__all__'

"""Сериализация запроса"""
class ShopUnitImportRequestSerializer(serializers.Serializer):
    items = ProductImportSerializer(many=True)
    updateDate = DateTimeFieldMS()

    def dfs(self, parent_item):
        to_update = []
        result_price = 0
        children_count = 0
        child_res = 0

        if parent_item.type == "OFFER":
            """Возвращаем два значения (цену всех товаров в дочерних категориях и их количество)."""
            return parent_item.price, 1

        if parent_item.children.all().count() == 0:
            parent_item.price = 0
            parent_item.save()
            return -1, -1




        for cur_item in parent_item.children.all():
            to_update += [cur_item]
            new_price, child_res =  self.dfs(cur_item)
            result_price += new_price
            children_count += child_res
        if child_res == 0:
            parent_item.price = None
        else:
            parent_item.price = result_price / children_count

        """Устанавливаем самую новую дату."""
        for cur_item in to_update:
            cur_datetime = cur_item.date
            previous_datetime = parent_item.date

            if cur_datetime > previous_datetime:
                parent_item.date = cur_datetime

        parent_item.save()

        return result_price, children_count

    def create(self, validated_data):
        items_data = validated_data.get('items')

        for item in items_data:
            item['date'] = validated_data.get('updateDate')
            if item.get('parentId'):
                item['parentId'] = Product.objects.get(pk=item.get('parentId'))

            if Product.objects.filter(pk=item.get('id')).exists():
                previous = Product.objects.get(pk=item.get('id'))
                previous_data = ProductSerializer(previous).data
                previous_data["oldId"] = previous_data["id"]
                previous_data.pop("id")
                previous_data.pop("children")

                ProductHistory.objects.create(**previous_data)

                previous.delete()

                Product.objects.create(**item)
            else:
                Product.objects.create(**item)

        parents = Product.objects.filter(parentId=None)
        for par in parents:
            self.dfs(par)
        return ShopUnitImportRequest(**validated_data)

