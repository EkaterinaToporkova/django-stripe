
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from main import views
from django.conf import settings
from django.conf.urls.static import static

from .views import CreateCheckoutSession, ProductsDetailView





urlpatterns = [
    path('', views.ProductsListView.as_view(), name='shop'),
    path("admin/", admin.site.urls),
    path('item/<int:pk>', ProductsDetailView.as_view(), name='item'),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('cancel/', views.CancelView.as_view(), name='cancel'),
    path('buy/<int:pk>/', CreateCheckoutSession.as_view(), name='create-checkout-session')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
