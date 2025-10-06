from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('category/<slug:slug>/', views.BlogCategoryView.as_view(), name='category'),
    path('tag/<slug:slug>/', views.BlogTagView.as_view(), name='tag'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='post_detail'),
]
