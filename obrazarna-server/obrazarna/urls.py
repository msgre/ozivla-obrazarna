from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from rest_framework.routers import DefaultRouter

from pictures.api import PictureViewSet, DimensionsView
from performance.api import PerformanceViewSet
from accompaniments.api import AccompanimentViewSet
from performance.views import index, PanelView


# api
router = DefaultRouter()
router.register(r'pictures', PictureViewSet)
router.register(r'performance', PerformanceViewSet)
router.register(r'accompaniments', AccompanimentViewSet)

urlpatterns = [
    path('', index),
    path('panel/', PanelView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/dimensions/', DimensionsView.as_view()),
]

# media/uploads
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
