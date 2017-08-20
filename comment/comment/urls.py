from django.conf.urls import url, include
from rest_framework import routers
from django.contrib import admin
from backend import views as backend_views

router = routers.DefaultRouter()
router.register(r'articles', backend_views.BlogArticleViewSet)
router.register(r'pages', backend_views.PageViewSet)
router.register(r'comments', backend_views.CommentViewSet)
router.register(r'history', backend_views.CommentHistoryViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
]
