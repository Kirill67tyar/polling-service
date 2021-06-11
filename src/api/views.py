from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     get_object_or_404, GenericAPIView)

from polls.utils import get_view_at_console1
from polls.models import (Poll, Question, Choice, Answer, )
from api.serializers import (ThinPollModelSerializer,
                             PollModelSerializer,
                             QuestionModelSerializer,
                             ChoiceModelSerializer, )


class PollsListAPIView(ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = ThinPollModelSerializer


class PollDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollModelSerializer


class QuestionsListAPIView(ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        poll_id = self.kwargs['poll_id']
        return qs.filter(poll_id=poll_id)


class QuestionDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        question_id = self.kwargs['pk']
        return qs.filter(pk=question_id)


class ChoiceModelViewSet(ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceModelSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        question_id = self.kwargs['question_id']
        return qs.filter(question_id=question_id)

