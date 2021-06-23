from collections import OrderedDict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse_lazy
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import (ListAPIView,
                                     ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     get_object_or_404, GenericAPIView)
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import ListView, CreateView

from polls.models import Poll, Question, Choice, Questionnaire, Answer
from polls.utils import get_view_at_console1, get_object_or_null
from api.permissions import (MyIsAdminUser, IsOwnerOrAdmin,
                             StartDateNotCreatedOrReadOnly, )
from api.serializers import (UserSerializer, ThinUserSerializers,
                             ThinPollModelSerializer, PollModelSerializer,
                             ThinQuestionModelSerializer, QuestionModelSerializer,
                             ChoiceModelSerializer, ThinChoiceModelSerializer,
                             ExperimentThinChoiceModelSerializer,
                             SelectPollModelSerilaizer,
                             QuestionnaireModelSerializer, )

now = timezone.now()

def experiments(self):
    ## self здесь был экземпляр PollsListAPIView
    # get_view_at_console1(self.get_serializer_context(), unpack=0, dictionary=0)
    # get_view_at_console1(self.get_renderer_context(), delimiter='+', unpack=0, dictionary=0)
    # get_view_at_console1(self.get_renderers(), delimiter='@',  unpack=0, dictionary=0)
    # get_view_at_console1(self.get_parser_context(self.request), delimiter=')',  unpack=0, dictionary=0)
    # get_view_at_console1(self.get_exception_handler_context(), delimiter='&',  unpack=0, dictionary=0)
    # get_view_at_console1(self.get_content_negotiator(), delimiter='^',  unpack=0, dictionary=0)
    get_view_at_console1(self, delimiter='^', unpack=0, dictionary=0)
    get_view_at_console1(self, delimiter=':', unpack=0, dictionary=0, find_type=1)
    get_view_at_console1(self, delimiter='!', unpack=0, dictionary=0, find_mro=1)
    return JsonResponse({'status': 'ok', })


# ----------------  POLLS
class PollsListAPIView(ListCreateAPIView):
    model = Poll
    queryset = model.objects.none()
    serializer_class = PollModelSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return self.model.objects.all()
        return self.model.objects.filter(owner=user)  # .select_related('questions')

    def list(self, request, *args, **kwargs):
        polls = self.get_queryset()
        context = {'request': request, }
        serializer = ThinPollModelSerializer(instance=polls, many=True, context=context)
        # experiments(serializer.data)
        return Response(serializer.data, status=HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PollDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollModelSerializer
    permission_classes = (IsOwnerOrAdmin,)


# ----------------  QUESTIONS
class QuestionsListAPIView(ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = ThinQuestionModelSerializer
    permission_classes = (IsOwnerOrAdmin, StartDateNotCreatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        poll_id = self.kwargs['poll_id']
        qs = qs.select_related('poll', 'poll__owner').prefetch_related('choices')
        if user.is_admin:
            return qs.filter(poll_id=poll_id)
        return qs.filter(poll_id=poll_id, poll__owner=self.request.user)

    def perform_create(self, serializer):
        get_view_at_console1(serializer.validated_data, unpack=0, delimiter='+')
        serializer.save(poll_id=self.kwargs['poll_id'])


class QuestionDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    permission_classes = (IsOwnerOrAdmin, StartDateNotCreatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        question_id = self.kwargs['pk']
        qs = qs.select_related('poll', 'poll__owner')
        if user.is_admin:
            return qs.filter(pk=question_id)
        return qs.filter(pk=question_id, poll__owner=user)


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.none()
    serializer_class = QuestionModelSerializer
    permission_classes = (IsOwnerOrAdmin, StartDateNotCreatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return ThinQuestionModelSerializer
        return QuestionModelSerializer

    def get_queryset(self):
        user = self.request.user
        poll_id = self.kwargs['poll_id']
        qs = Question.objects.select_related('poll', 'poll__owner').prefetch_related('choices')
        if user.is_admin:
            return qs.filter(poll_id=poll_id)
        return qs.filter(poll_id=poll_id, poll__owner=self.request.user)

    def perform_create(self, serializer):
        get_view_at_console1(serializer.validated_data, unpack=0, delimiter='+')
        serializer.save(poll_id=self.kwargs['poll_id'])


# ----------------  CHOICES
class ChoiceViewSet(ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceModelSerializer
    permission_classes = (IsOwnerOrAdmin, StartDateNotCreatedOrReadOnly,)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace',)

    def get_serializer_class(self):
        if self.action == 'list':
            return ThinChoiceModelSerializer
            # return ExperimentThinChoiceModelSerializer
        return ChoiceModelSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        question_id = self.kwargs['question_id']
        return qs.filter(question_id=question_id)

    def perform_create(self, serializer):
        serializer.save(question_id=self.kwargs['question_id'])


# ----------------  USERS
class UserViewSet(ModelViewSet):
    model = get_user_model()
    queryset = model.objects.all()
    serializer_class = UserSerializer
    permission_classes = (MyIsAdminUser,)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace',)

    def get_serializer_class(self):
        if self.action == 'list':
            return ThinUserSerializers
        return UserSerializer


class SelectPollListAPIView(ListAPIView):
    model = Questionnaire
    queryset = model.objects.none()
    serializer_class = SelectPollModelSerilaizer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        get_view_at_console1(now)
        qs = Poll.objects.filter(start_date__lte=now, end_date__gte=now)
        if user.is_authenticated:
            questionnaires = list(Questionnaire.objects.filter(respondent=user))
            return qs.exclude(questionnaires__in=questionnaires)
        return qs


# Далее сделатть обработчик-функцию, которая будет показывать выбранный
# poll и даст возможность записаться на него post запросом
# этот ниже убрать
class SelectPollViewSet(ListCreateAPIView):
    model = Questionnaire
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireModelSerializer

    def list(self, request, *args, **kwargs):
        now = timezone.now()
        user = request.user
        questionnaires = list(Questionnaire.objects.filter(respondent=user))
        polls = Poll.objects.exclude(questionnaires__in=questionnaires).filter(start_date__lte=now, end_date__gte=now)
        serializer = SelectPollModelSerilaizer(polls, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
