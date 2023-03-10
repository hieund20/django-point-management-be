from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('score', views.ScoreViewSet, basename='score')
router.register('course', views.CourseViewSet, basename='course')
router.register('user', views.UserViewSet, basename='user')
# router.register('', views.CSVHandleView, basename='score_import')

urlpatterns = [
    path('', include(router.urls)),
    path('score/import', views.CSVHandleView.as_view(), name='csv_handle'),
]
