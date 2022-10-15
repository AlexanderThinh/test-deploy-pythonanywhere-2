from django.contrib import admin
from django.urls import path
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views
from .admin import admin_site

router = DefaultRouter()
router.register(prefix='loai-tour', viewset=views.LoaiTourViewSet, basename='loai-tour')
router.register(prefix='tours', viewset=views.TourViewSet, basename='tour')
router.register(prefix='users', viewset=views.UserViewSet, basename='user')
router.register(prefix='don-dat-tour', viewset=views.DonDatTourViewSet, basename='don-dat-tour')
router.register(prefix='tin-tuc', viewset=views.TinTucViewSet, basename='tin-tuc')
router.register(prefix='comments', viewset=views.CommentTourViewSet, basename='comment')
router.register(prefix='tour-images', viewset=views.TourImageViewSet, basename='tour-images')

urlpatterns = [
    path('', include(router.urls)),
    path('oauth-info/', views.AuthInfo.as_view()),
    path('admin/', admin_site.urls)
]