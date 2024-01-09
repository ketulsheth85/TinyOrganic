from apps.core.views import CoreView
from django.urls import re_path

urlpatterns = [

    re_path(f'.*', CoreView.as_view()),
]
