from django.urls import path # pyright: ignore[reportMissingModuleSource]
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('content/', views.content_list, name='content_list'),
    path('content/add/', views.add_content, name='add_content'),
    path('content/<int:pk>/', views.content_detail, name='content_detail'),
    path('content/<int:pk>/edit/', views.edit_content, name='edit_content'),
    path('content/<int:pk>/delete/', views.delete_content, name='delete_content'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('statistics/', views.statistics, name='statistics'),
]