from django.urls import path

from api.views import (UserViewSet,
                       PollsListAPIView,
                       PollDetailAPIView,
                       QuestionsListAPIView,
                       QuestionDetailAPIView,
                       ChoiceViewSet,
                       QuestionViewSet,
                       SelectPollListAPIView,
                       QuestionnairesListRetrieveAPIView,
                       select_poll_view,
                       questionnaire_questions_view,
                       give_answer_view,
                       change_answer_view, )

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
    # --- USERS
    path('users/', UserViewSet.as_view(for_many_elements), name='users_list'),
    path('users/<int:pk>/', UserViewSet.as_view(for_one_element), name='user_detail'),
    path('questionnaires/', QuestionnairesListRetrieveAPIView.as_view({'get': 'list', }),
         name='questionnaires_list'),
    path('questionnaires/<int:pk>/',
         QuestionnairesListRetrieveAPIView.as_view({'get': 'retrieve', 'delete': 'destroy', }),
         name='questionnaire_detail'),
    path('questionnaires/<int:questionnaire_id>/questions/',
         questionnaire_questions_view, name='questionnaire_questions_list'),

    path('questionnaires/<int:questionnaire_id>/questions/<int:question_id>/give-an-answer/',
         give_answer_view, name='give_answer'),
    path('questionnaires/<int:questionnaire_id>/answers/<int:answer_id>/change-answer/',
         change_answer_view, name='change_answer'),

    # --- POLLS
    path('workspace/polls/', PollsListAPIView.as_view(), name='polls_list'),
    path('workspace/polls/<int:pk>/', PollDetailAPIView.as_view(), name='poll_detail'),

    # --- QUESTIONS
    # APIView
    # path('workspace/polls/<int:poll_id>/questions/', QuestionsListAPIView.as_view(), name='questions_list'),
    # path('workspace/polls/<int:poll_id>/questions/<int:pk>/',
    #      QuestionDetailAPIView.as_view(),
    #      name='question_detail'),

    # ViewSet
    path('workspace/polls/<int:poll_id>/questions/', QuestionViewSet.as_view(for_many_elements), name='questions_list'),
    path('workspace/polls/<int:poll_id>/questions/<int:pk>/',
         QuestionViewSet.as_view(for_one_element),
         name='question_detail'),

    # --- CHOICES
    path('workspace/polls/<int:poll_id>/questions/<int:question_id>/choices/',
         ChoiceViewSet.as_view(for_many_elements),
         name='choices_list'),
    path('workspace/polls/<int:poll_id>/questions/<int:question_id>/choices/<int:pk>/',
         ChoiceViewSet.as_view(for_one_element),
         name='choice_detail'),

    path('polls/', SelectPollListAPIView.as_view(), name='select_poll_list'),
    path('polls/<int:pk>/select/', select_poll_view, name='select_poll'),

]
