from django.urls import path

from polls.views import checking


app_name = 'polls'

urlpatterns = [
    path('checking/', checking, name='checking'),
]