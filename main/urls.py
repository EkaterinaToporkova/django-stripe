from django.contrib import admin
from django.urls import path

from main import views
from django.conf import settings
from django.conf.urls.static import static

from main.views import create_checkout_session

urlpatterns = [path("", views.ProductListView.as_view(), name="shop"),
               path("item/<id>/", views.ProductDetailView.as_view(), name='item'),
               path('buy/<id>/', create_checkout_session, name='api_checkout_session'),
               path('success/', views.PaymentSuccessView.as_view(), name='success'),
               path('failed/', views.PaymentFailedView.as_view(), name='failed'),
               path("admin/", admin.site.urls),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
