from django.urls import path

from api.views import (UserViewSet,
                       PollsListAPIView,
                       PollDetailAPIView,
                       QuestionsListAPIView,
                       QuestionDetailAPIView,
                       ChoiceViewSet,
                       QuestionViewSet, )

app_name = 'api'

for_many_elements = {
    'get': 'list',
    'post': 'create',
}

for_one_element = {
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
}

urlpatterns = [
    # --- users
    path('users/', UserViewSet.as_view(for_many_elements), name='users_list'),
    path('users/<int:pk>/', UserViewSet.as_view(for_one_element), name='user_detail'),

    # --- polls
    path('polls/', PollsListAPIView.as_view(), name='polls_list'),
    path('polls/<int:pk>/', PollDetailAPIView.as_view(), name='poll_detail'),

    # --- questions
    # APIView
    # path('polls/<int:poll_id>/questions/', QuestionsListAPIView.as_view(), name='questions_list'),
    # path('polls/<int:poll_id>/questions/<int:pk>/',
    #      QuestionDetailAPIView.as_view(),
    #      name='question_detail'),

    # ViewSet
    path('polls/<int:poll_id>/questions/', QuestionViewSet.as_view(for_many_elements), name='questions_list'),
    path('polls/<int:poll_id>/questions/<int:pk>/',
         QuestionViewSet.as_view(for_one_element),
         name='question_detail'),

    # --- choices
    path('polls/<int:poll_id>/questions/<int:question_id>/choices/',
         ChoiceViewSet.as_view(for_many_elements),
         name='choices_list'),
    path('polls/<int:poll_id>/questions/<int:question_id>/choices/<int:pk>/',
         ChoiceViewSet.as_view(for_one_element),
         name='choice_detail'),
]
