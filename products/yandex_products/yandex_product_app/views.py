import typing

from rest_framework import generics, status
from rest_framework.response import Response
from datetime import datetime, timedelta

from .models import Product, ProductHistory
from .serializers import ShopUnitImportRequestSerializer, ShopUnitStatisticSerializer, \
    ProductImportSerializer, \
    ProductSerializer


def update_price_and_date(product: Product, price: typing.AnyStr, update_date: datetime.date):
    pass


class Imports(generics.CreateAPIView):
    """View imports."""
    queryset = Product.objects.all()
    serializer_class = ShopUnitImportRequestSerializer

    """CREATE Method"""

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_200_OK, headers=headers)



class Statistic(generics.RetrieveAPIView):
    """View statistic."""
    queryset = Product.objects.all()
    serializer_class = ShopUnitStatisticSerializer

    """Собираем информацию о инзменениях товаров"""
    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        """Обрабатываем агрументы и преобразуем к Datetime формату"""
        try:
            query_from = request.query_params.get('dateStart')
            query_to = request.query_params.get('dateEnd')

            date_from = datetime.strptime(query_from, '%Y-%m-%dT%H:%M:%S.%fZ')
            date_to = datetime.strptime(query_to, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            return Response({"code": 400, "message": "Validation Failed"}, status=status.HTTP_400_BAD_REQUEST)

        """Смотрим на текущие данные и данные в ProductHistory и сохраняем, если подходят под требования."""
        products = ProductHistory.objects.filter(oldId=pk)
        cur = Product.objects.get(pk=pk)

        to_stat = list()

        if date_to > cur.date >= date_from:
            to_stat.append(cur)
        for cur_product in products:
            current_date = cur_product.date

            if date_to > current_date >= date_from:
                to_stat.append(cur_product)

                """Преобразуем в JSON формат."""
        return Response({"items": ShopUnitStatisticSerializer(to_stat, many=True).data}, status=status.HTTP_200_OK)


class Sales(generics.RetrieveAPIView):
    """View sales."""
    queryset = Product.objects.all()
    serializer_class = ShopUnitStatisticSerializer

    """Получаем продажи за последние 24 часа."""

    def get(self, request, *args, **kwargs):
        """Обрабатываем агрументы и преобразуем к Datetime формату"""
        try:
            param_of_query = request.query_params.get('date')
            date_to = datetime.strptime(param_of_query, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            return Response({"code": 400, "message": "Validation Failed"}, status=status.HTTP_400_BAD_REQUEST)
        """Получаем объекты"""
        date_from = date_to - timedelta(hours=24)
        products = []
        for item in Product.objects.all():
            if date_from <= item.date < date_to:
                products.append(item)

                """Преобразуем в JSON формат."""
        return Response({"items": ShopUnitStatisticSerializer(products, many=True).data}, status=status.HTTP_200_OK)


class Node(generics.RetrieveAPIView):
    """View nodes."""
    serializer_class = ProductSerializer

    """Получаем категорию и ее детей."""

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"code": 400, "message": "Validation Failed"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = Product.objects.get(pk=pk)

        except Product.DoesNotExist:
            return Response({"code": 404, "message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        data = ProductSerializer(instance).data
        return Response(data, status=status.HTTP_200_OK)


class Delete(generics.DestroyAPIView):
    """View delete."""
    serializer_class = ProductSerializer
    """Удаляем категории и ее детей ко id"""
    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)

        if not pk:
            return Response({"code": 400, "message": "Validation Failed"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
        except Product.DoesNotExist:
            return Response({"code": 404, "message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)
