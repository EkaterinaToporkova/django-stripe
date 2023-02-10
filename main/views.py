from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView

from shop.models import Item, Order


class ProductsListView(ListView):
    model = Item
    template_name = 'shop.html'


class ProductsDetailView(DetailView):
    model = Item
    template_name = 'shop-details.html'


@login_required(login_url=reverse_lazy('signin'))
def cart_view(request):
    cart = Order.get_cart(request.user)
    items = cart.orderitem_set.all()
    context = {
        'cart': cart,
        'items': items
    }
    return render(request, 'shop/cart.html', context)


