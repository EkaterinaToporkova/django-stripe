from django.contrib import admin
from django.urls import path

from main import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [path("", views.ProductListView.as_view(), name="shop"),
               path("admin/", admin.site.urls),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
