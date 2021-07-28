from collections import OrderedDict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse_lazy as r_l
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.generics import (ListAPIView,
                                     ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     get_object_or_404, GenericAPIView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.generic import ListView, CreateView

from polls.models import Poll, Question, Choice, Questionnaire, Answer
from polls.utils import get_view_at_console1, get_object_or_null, built_absolute_URL
from api.permissions import (MyIsAdminUser, IsOwnerOrAdmin,
                             StartDateNotCreatedOrReadOnly, )
from api.serializers import (UserSerializer, ThinUserSerializers,
                             ThinPollModelSerializer, PollModelSerializer,
                             ThinQuestionModelSerializer, QuestionModelSerializer,
                             ChoiceModelSerializer, ThinChoiceModelSerializer,
                             ExperimentThinChoiceModelSerializer,
                             SelectPollModelSerilaizer,
                             ThinSelectPollModelSerilaizer,
                             QuestionnaireModelSerializer,
                             QuestionnaireQuestionsModelSerializer,
                             QuestionnaireAnswersSerializer)

NOW = timezone.now()


def experiments(request):
    ## self здесь был экземпляр PollsListAPIView
    # get_view_at_console1(self.get_serializer_context(), unpack=0, dictionary=0)
    # get_view_at_console1(self.get_renderer_context(), delimiter='+', unpack=0, dictionary=0)
    # get_view_at_console1(self.get_renderers(), delimiter='@',  unpack=0, dictionary=0)
    # get_view_at_console1(self.get_parser_context(self.request), delimiter=')',  unpack=0, dictionary=0)
    # get_view_at_console1(self.get_exception_handler_context(), delimiter='&',  unpack=0, dictionary=0)
    # get_view_at_console1(self.get_content_negotiator(), delimiter='^',  unpack=0, dictionary=0)
    # get_view_at_console1(self, delimiter='^', unpack=0, dictionary=0)
    # get_view_at_console1(self, delimiter=':', unpack=0, dictionary=0, find_type=1)
    # get_view_at_console1(self, delimiter='!', unpack=0, dictionary=0, find_mro=1)
    get_view_at_console1(request.get_full_path(), delimiter=' - ', unpack=0, dictionary=0, find_mro=0)
    get_view_at_console1(request.get_full_path_info(), delimiter=' - ', unpack=0, dictionary=0, find_mro=0)
    get_view_at_console1(request.get_host(), delimiter=' - ', unpack=0, dictionary=0, find_mro=0)
    get_view_at_console1(request.get_port(), delimiter=' - ', unpack=0, dictionary=0, find_mro=0)
    get_view_at_console1(request.get_raw_uri(), delimiter=' - ', unpack=0, dictionary=0, find_mro=0)
    get_view_at_console1(request.path, delimiter=' p ', unpack=0, dictionary=0, find_mro=0)
    get_view_at_console1(request.path_info, delimiter=' p_i ', unpack=0, dictionary=0, find_mro=0)
    get_view_at_console1(request.scheme, delimiter=' sc ', unpack=0, dictionary=0, find_mro=0)
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
    serializer_class = ThinSelectPollModelSerilaizer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        get_view_at_console1(NOW)
        qs = Poll.objects.filter(start_date__lte=NOW, end_date__gte=NOW)
        if user.is_authenticated:
            questionnaires = list(Questionnaire.objects.filter(respondent=user))
            return qs.exclude(questionnaires__in=questionnaires)
        return qs


# Далее сделать обработчик-функцию, которая будет показывать выбранный
# poll и даст возможность записаться на него post запросом
@api_view(['GET', 'POST', ])
@permission_classes([IsAuthenticated, ])
def select_poll_view(request, pk):
    user = request.user
    kwargs = {
        'model': Poll,
        'pk': pk,
        'start_date__lte': NOW,
        'end_date__gte': NOW,
    }
    poll = get_object_or_null(**kwargs)
    if poll:
        if request.method == 'GET':
            context = {'request': request, }
            serializer = SelectPollModelSerilaizer(poll, context=context)
            return Response(serializer.data, status=HTTP_200_OK)

        elif request.method == 'POST':
            questionnaire = poll.questionnaires.filter(respondent=user)
            if questionnaire.exists():
                questionnaire = questionnaire.first()
                if not questionnaire.completed:
                    url = built_absolute_URL(request=request,
                                             viewname='api:questionnaire_questions_list',
                                             questionnaire_id=questionnaire.pk)
                    # experiments(request=request)
                    return Response({'status': 'Вы начали проходить этот опрос, но не закончили его',
                                     'go_on_questionnaire': url, })
                else:
                    # здесь добавить ссылку на удаление опроса !
                    pass
                    return Response({'status': 'Вы уже проходили этот опрос', })
            else:
                anonymous = request.POST.get('anonymous')
                kwargs = {
                    'poll': poll,
                    'respondent': user,
                    'anonymous': anonymous if anonymous else False,
                }
                questionnaire = Questionnaire.objects.create(**kwargs)
                questionnaire_id = questionnaire.pk
                url = built_absolute_URL(request=request,
                                         viewname='api:questionnaire_questions_list',
                                         questionnaire_id=questionnaire_id)
                data = {
                    'status': f'Вы начали опрос "{poll.title}"',
                    'questionnaire_id': questionnaire_id,
                    'go_on_questionnaire': url,
                }
                return Response(data, status=HTTP_200_OK)
    else:
        return Response(status=HTTP_404_NOT_FOUND)


# list, detail, delete questionnaire
class QuestionnairesListRetrieveAPIView(RetrieveModelMixin,
                                        DestroyModelMixin,
                                        ListModelMixin,
                                        GenericViewSet):
    model = Questionnaire
    queryset = model.objects.none()
    serializer_class = QuestionnaireModelSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'delete', 'head', 'options', 'trace',)

    def get_queryset(self):
        user = self.request.user
        return self.model.objects.filter(respondent=user)


# нужно сделать так, чтобы выдавался список вопросов, с дополнительным полем в каждом из них
# есть ли ответ на вопрос, или нет
# если ответ есть, и опросник не закончен, то добавить возможность изменить ответ
# поле (change_answer) ссылке на измнение ответа
# если овтета нет, то добавить поле give_answer - ссылку на то, чтобы дать ответ.
# Далее, если опросник завершен, то изменять ответы нельзя.

# Если опросник закончился по дате, то и опросник заново перепроходить нельзя,
# но это уже нюансы.

"""
'questionnaires/<int:questionnaire_id>/questions/'
"""


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def questionnaire_questions_view(request, questionnaire_id):
    user = request.user
    questionnaire = get_object_or_null(Questionnaire, pk=questionnaire_id, respondent=user)
    if questionnaire:
        poll_id = questionnaire.poll.pk
        poll = get_object_or_null(Poll, pk=poll_id)
        questions = poll.questions.all()
        context = {'request': request, }
        serializer = QuestionnaireQuestionsModelSerializer(questions, many=True, context=context)
        return Response(serializer.data, status=HTTP_200_OK)
    else:
        return Response(status=HTTP_404_NOT_FOUND)


"""
для give_answer
1 - проверить что опрос, еще действительный по дате
2 - проверить что ответа на этот вопрос еще не дано
3 - проверить что опросник не закончен (все ответы даны). 
Если ответа на этот вопрос нет, то и опросник не закончен, поэтому 3й пункт можно опустить.
4 - сделать запрос в бд, достать вопрос, который соответствует опросу, и ссылке
"""


@api_view(['GET', 'POST', ])
@permission_classes([IsAuthenticated, ])
def give_answer_view(request, questionnaire_id, question_id):
    user = request.user
    questionnaire = get_object_or_null(Questionnaire, pk=questionnaire_id, respondent=user)
    if questionnaire:
        poll = questionnaire.poll
        if poll.start_date < NOW < poll.end_date:
            question = poll.questions.filter(pk=question_id)
            if question.exists():
                question = question.first()
                if not question.answers.filter(questionnaire=questionnaire).exists():
                    if request.method == 'GET':
                        context = {'request': request, }
                        serializer = QuestionnaireQuestionsModelSerializer(question, context=context)
                        return Response(serializer.data, status=HTTP_200_OK)
                    # Если post-запрос:
                    else:
                        type_question = question.type_question
                        if type_question in ('checkbox', 'radio',):
                            question_choices_ids = set(question.choices.values_list('pk', flat=True))
                            answer_choices_ids = set(request.data['answer'])
                            if answer_choices_ids and answer_choices_ids.issubset(question_choices_ids):
                                if type_question == 'checkbox':
                                    answer = Answer.objects.create(questionnaire=questionnaire, question=question)
                                    choices_qs = list(Choice.objects.filter(pk__in=answer_choices_ids))
                                    answer.checkbox.add(*choices_qs)
                                    return Response({'status': 'answer accepted'}, status=HTTP_200_OK)

                                # если тип вопроса - radio
                                elif type_question == 'radio' and len(answer_choices_ids) == 1:
                                    answer_choice_for_radio = list(Choice.objects.filter(pk__in=answer_choices_ids))[0]
                                    Answer.objects.create(questionnaire=questionnaire,
                                                          question=question,
                                                          radio=answer_choice_for_radio)
                                    return Response({'status': 'answer accepted'}, status=HTTP_200_OK)
                                else:
                                    return Response(status=HTTP_400_BAD_REQUEST)
                            else:
                                return Response(status=HTTP_400_BAD_REQUEST)

                        # если тип вопроса - text
                        elif type_question == 'text':
                            kwargs = {
                                'questionnaire': questionnaire,
                                'question': question,
                                'text': request.data['answer'],
                            }
                            Answer.objects.create(**kwargs)
                            return Response({'status': 'answer accepted'}, status=HTTP_200_OK)

                        # если тип вопроса не checkbox/radio/text:
                        else:
                            return Response(status=HTTP_400_BAD_REQUEST)

                else:
                    # перенаправляет на change_answer
                    answer_id = question.answers.filter(questionnaire=questionnaire).first().pk
                    kwargs = {
                        'request': request,
                        'viewname': 'api:change_answer',
                        'questionnaire_id': questionnaire_id,
                        'answer_id': answer_id,
                    }
                    url_to_change_answer = built_absolute_URL(**kwargs)
                    # можно прямо здесь редирект устроить, а можно послать url на редирект
                    return Response({'status': 'the answer has already been',
                                     'change_answer': url_to_change_answer, }, status=HTTP_200_OK)
            else:
                return Response(status=HTTP_404_NOT_FOUND)
        else:
            return Response(status=HTTP_404_NOT_FOUND)
    else:
        return Response(status=HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT', ])
@permission_classes([IsAuthenticated, ])
def change_answer_view(request, questionnaire_id, answer_id):
    user = request.user
    questionnaire = get_object_or_null(Questionnaire, pk=questionnaire_id, respondent=user)
    if questionnaire:
        poll = questionnaire.poll
        if poll.start_date < NOW < poll.end_date:
            answer_qs = Answer.objects.filter(pk=answer_id)
            if answer_qs.exists():
                answer = answer_qs.first()
                if answer.questionnaire.pk == questionnaire_id:
                    kwargs = {
                        'instance': answer,
                        'context': {
                            'request': request,
                        },
                    }
                    serializer = QuestionnaireAnswersSerializer(**kwargs)
                    return Response(serializer.data, status=HTTP_200_OK)
                else:
                    pass

            else:
                pass
        else:
            pass
    else:
        return Response(status=HTTP_404_NOT_FOUND)


"""
{"answer": [1,3]}
text = TextField(blank=True, null=True)
    radio = ForeignKey(to=Choice, on_delete=CASCADE, blank=True, null=True)
    checkbox
"""
