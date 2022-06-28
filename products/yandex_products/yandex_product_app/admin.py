from django.contrib import admin

from yandex_product_app.models import Product, ProductHistory

admin.site.register(Product)
admin.site.register(ProductHistory)