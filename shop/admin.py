from django.contrib import admin

from shop.models import Item, OrderItem, Order

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)