from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url

from django.conf import settings
from django.conf.urls.static import static  # 追加

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'api/', include('api.urls')),
    url(r'^', include('main.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
