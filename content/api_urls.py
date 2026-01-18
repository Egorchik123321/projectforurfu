from django.urls import path, include # pyright: ignore[reportMissingModuleSource]
from rest_framework.routers import DefaultRouter # pyright: ignore[reportMissingImports]
from .api_views import (
    CategoryViewSet, ContentItemViewSet,
    RecommendationViewSet, UserViewSet, ParseContentView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'contents', ContentItemViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('parse/', ParseContentView.as_view(), name='api-parse'),
    path('search/external/', ExternalSearchView.as_view(), name='api-external-search'), # pyright: ignore[reportUndefinedVariable]
    path('analytics/', AnalyticsView.as_view(), name='api-analytics'), # pyright: ignore[reportUndefinedVariable]
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('visualizations/', VisualizationView.as_view(), name='api-visualizations'), # pyright: ignore[reportUndefinedVariable]
]