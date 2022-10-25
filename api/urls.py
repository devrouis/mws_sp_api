from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from .views import *

app_name = 'api'

router = routers.SimpleRouter()
router.register('requests', ScrapeRequestViewSet)

urlpatterns = router.urls