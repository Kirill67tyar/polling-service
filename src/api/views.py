from collections import OrderedDict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.reverse import reverse_lazy
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     get_object_or_404, GenericAPIView)
from django.urls import reverse
from django.views.generic import ListView, CreateView

from polls.models import (Poll, Question, Choice, Answer, )
from polls.utils import get_view_at_console1, get_object_or_null
from api.permissions import IsOwnerOrAdmin, StartDateNotCreatedOrReadOnly
from api.serializers import (ThinPollModelSerializer, PollModelSerializer,
                             QuestionModelSerializer, ChoiceModelSerializer, )


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


class PollsListAPIView(ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollModelSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        qs = super().get_queryset()
        owner = self.request.user
        return qs.filter(owner=owner)

    def list(self, request, *args, **kwargs):
        owner = request.user
        polls = Poll.objects.filter(owner=owner)  # .select_related('questions')
        context = {'request': request, }
        serializer = ThinPollModelSerializer(instance=polls, many=True, context=context)
        # experiments(serializer.data)
        return Response(serializer.data, status=HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PollDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollModelSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        qs = super().get_queryset()
        owner = self.request.user
        return qs.filter(owner=owner)


class QuestionsListAPIView(ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsOwnerOrAdmin, StartDateNotCreatedOrReadOnly,)


    def get_queryset(self):
        qs = super().get_queryset()
        poll_id = self.kwargs['poll_id']
        qs = qs.select_related('poll', 'poll__owner')
        return qs.filter(poll_id=poll_id, poll__owner=self.request.user)

    def perform_create(self, serializer):
        get_view_at_console1(serializer.validated_data, unpack=0, delimiter='+')
        serializer.save(poll_id=self.kwargs['poll_id'])


class QuestionDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsOwnerOrAdmin, StartDateNotCreatedOrReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset()
        question_id = self.kwargs['pk']
        qs = qs.select_related('poll', 'poll__owner')
        return qs.filter(pk=question_id, poll__owner=self.request.user)


class ChoiceModelViewSet(ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceModelSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsOwnerOrAdmin, StartDateNotCreatedOrReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset()
        question_id = self.kwargs['question_id']
        return qs.filter(question_id=question_id)

    def perform_create(self, serializer):
        serializer.save(question_id=self.kwargs['question_id'])

    # def get_success_url(self):
    #     """Return the URL to redirect to after processing a valid form."""
    #     if self.success_url:
    #         url = self.success_url.format(**self.object.__dict__)
    #     else:
    #         # url = reverse_lazy('api:question_detail', kwargs={'poll_id': self.object.question.poll_id,
    #         #                                                   'pk': self.object.question_pk})
    #         url = reverse('api:question_detail', kwargs={'poll_id': self.kwargs['poll_id'],
    #                                                           'pk': self.object.kwargs['pk']})
    #         # try:
    #         #     url = self.object.get_absolute_url()
    #         # except AttributeError:
    #         #     raise ImproperlyConfigured(
    #         #         "No URL to redirect to.  Either provide a url or define"
    #         #         " a get_absolute_url method on the Model.")
    #     return url


"""
ограничение в изменении если start_date создан будем делать в кастомном пермишинсе
"""
