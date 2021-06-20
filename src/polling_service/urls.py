"""polling_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('polls.urls', namespace='polls')),
]

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

# kirillbogomolov.ric@yandex.ru
# alskdjfhg

# {
#     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyNDMwNzM3OSwianRpIjoiNjMxYzFmOGNkMGNhNDE0ODhhMTllY2U5N2YxYjJhNjQiLCJ1c2VyX2lkIjoxfQ.oSw-LyBfy5canJ5awn-hRcDG5eyz3BpsJRaPRyUwOYs",
#     "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI0MjIxMjc5LCJqdGkiOiIxNzJjZWIyZWM4NTk0MDUxYTMxYTQzMjgyYmNjNjdjMiIsInVzZXJfaWQiOjF9.NbwkqeZBv8_wwB1g-KzMWI8-rr-Rna629bdaLXEXCoQ"
# }

# важно - при использовании такой системы authenticated_classes нужно отключать в обработчиках
# refresh token по умолчанию один день
# access token по умолчанию 5 минут
# в настройках изменено

# в настройках меняется
# Получить refresh и access token:
# http://127.0.0.1:8000/api/token/ - post запрос
# в теле запроса:
# {"email": "kirillbogomolov.ric@yandex.ru",
# "password": "alskdjfhg"}

# получить доступ для контента:
# в postman выбираешь тип авторизации - Bearer Token и вводишь в поле access token
# протухает access token через несколько минут

# обновить access token когда он протух
# http://127.0.0.1:8000/api/token/refresh/ - post запрос
# в теле запроса:
# {"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyNDMwNTkyNiwianRpIjoiYzlmMjA5Y2NmODRlNDdjOGExZDdjMjZlZjI5Y2FkZjciLCJ1c2VyX2lkIjoxfQ.bVv5YYN8ucakAlTk2pIs-Cx_79_uYzZ-OQLZlaZ1FkE"}
# или другой refresh token если ты его поменял.