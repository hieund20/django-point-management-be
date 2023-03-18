from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('score', views.ScoreViewSet, basename='score')
router.register('course', views.CourseViewSet, basename='course')
router.register('user', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('csv-handle/import-score/', views.CSVHandleView.as_view(), name='csv_handle'),
]
