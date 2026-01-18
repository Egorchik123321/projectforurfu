from django.contrib import admin # pyright: ignore[reportMissingModuleSource]
from django.urls import path, include # pyright: ignore[reportMissingModuleSource]
from django.conf import settings # pyright: ignore[reportMissingModuleSource]
from django.conf.urls.static import static # pyright: ignore[reportMissingModuleSource]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('content.urls')),
    path('api/', include('content.api_urls')),  # Добавьте эту строку
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)