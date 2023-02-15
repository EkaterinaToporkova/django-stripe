from django.shortcuts import render
from django.views.generic import ListView

from shop.models import Item


class ProductListView(ListView):
    model = Item
    template_name = 'shop.html'

