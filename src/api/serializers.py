from rest_framework.reverse import reverse_lazy
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer, Serializer

from polls.utils import get_view_at_console1, get_object_or_null
from polls.models import (Poll, Question, Choice, Answer)


# https://www.django-rest-framework.org/api-guide/fields/
# https://www.django-rest-framework.org/api-guide/serializers/

# !!! когда будешь пилить сериализаторы для user прочти статью:
# https://www.django-rest-framework.org/api-guide/fields/#choice-selection-fields

class ChoiceModelSerializer(ModelSerializer):
    update_choice = SerializerMethodField(read_only=True)
    question = SerializerMethodField(read_only=True)

    def get_update_choice(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(reverse_lazy('api:question_detail_choice_detail',
                                                       kwargs={'poll_id': obj.question.poll.pk,
                                                               'question_id': obj.question.pk,
                                                               'pk': obj.pk, }))

    def get_question(self, obj):
        return str(obj.question)

    class Meta:
        model = Choice
        fields = ('id', 'question', 'title', 'update_choice',)


class QuestionModelSerializer(ModelSerializer):
    complete_question = SerializerMethodField(read_only=True)

    choices = SerializerMethodField(read_only=True)

    def get_complete_question(self, obj):
        request = self.context['request']
        if isinstance(obj, Question):
            return request.build_absolute_uri(reverse_lazy('api:question_detail',
                                                           kwargs={'poll_id': obj.poll.pk,
                                                                   'pk': obj.pk, }))
        return None

    def get_choices(self, obj):
        if isinstance(obj, Question):
            if obj.type_question in ('radio', 'checkbox',):
                return list(obj.choices.values())
            return 'Variants cannot be added because the question type is text"'
        return None

    # возвращает OrderedDict одного instance
    # который будет рендериться
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        get_view_at_console1(ret, delimiter='N')
        type_question = ret['type_question']
        request = self.context['request']
        if type_question in ('radio', 'checkbox',):
            pk = ret.get('id')
            question = get_object_or_null(Question, pk=pk)
            if question:
                ret['add_choice'] = request.build_absolute_uri(reverse_lazy('api:question_detail_choice_list',
                                                                            kwargs={'poll_id': question.poll.pk,
                                                                                    'question_id': question.pk, }))
        return ret

    class Meta:
        model = Question
        fields = ('id', 'title', 'type_question', 'complete_question', 'choices',)


class ThinQuestionModelSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'title', 'type_question',)


class ThinPollModelSerializer(ModelSerializer):
    update_poll = HyperlinkedIdentityField(view_name='api:poll_detail')
    quantity_questions = SerializerMethodField(read_only=True)

    def get_quantity_questions(self, obj):
        return obj.questions.count()

    owner = SerializerMethodField(read_only=True)

    def get_owner(self, obj):
        return obj.owner.email

    class Meta:
        model = Poll
        fields = ('id', 'title', 'owner', 'quantity_questions', 'update_poll',)


class PollModelSerializer(ModelSerializer):
    questions = ThinQuestionModelSerializer(many=True, read_only=True)
    owner = SerializerMethodField(read_only=True)
    add_question = SerializerMethodField(read_only=True)
    slug = SerializerMethodField(read_only=True)

    def get_owner(self, obj):
        return obj.owner.email

    def get_add_question(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(reverse_lazy('api:questions_list', kwargs={'poll_id': obj.pk, }))

    def get_slug(self, obj):
        return obj.slug

    class Meta:
        model = Poll
        fields = ('id',
                  'owner',
                  'title',
                  'slug',
                  'description',
                  'start_date',
                  'end_date',
                  'created',
                  # 'active',
                  'add_question',
                  'questions',
                  )


"""
class Poll(Model):
    owner = ForeignKey(to=User, on_delete=CASCADE,
                       related_name='polls_created',
                       verbose_name='Автор')
    title = CharField(max_length=255, db_index=True, verbose_name='Название опроса')
    slug = SlugField(max_length=250, unique=True, db_index=True, verbose_name='Slug опроса')
    description = TextField(verbose_name='Описание опроса')
    start_date = DateTimeField(verbose_name='Начало опроса', blank=True, null=True)
    end_date = DateTimeField(verbose_name='Конец опроса', blank=True, null=True)
    created = DateTimeField(auto_now_add=True, verbose_name='Опрос создан')
    active = BooleanField(default=False, verbose_name='Опрос менять нельзя')

    class Meta:
        # https://docs.djangoproject.com/en/3.2/ref/models/options/
        ordering = ['title', ]
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(my_custom_slugify(str(self.title)))
        return super(Poll, self).save(*args, **kwargs)


class Question(Model):
    CHOICES = (
        ('text', 'Text',),  # 1
        ('radio', 'Radio',),  # 2
        ('checkbox', 'Checkbox',),  # 3
    )
    poll = ForeignKey(to=Poll,
                      on_delete=CASCADE,
                      related_name='questions',
                      verbose_name='Опрос')
    title = CharField(max_length=255, db_index=True, verbose_name='Вопрос')
    type_question = CharField(max_length=8,
                              choices=CHOICES,
                              default='text',
                              verbose_name='Тип вопроса')

    class Meta:
        # https://docs.djangoproject.com/en/3.2/ref/models/options/
        ordering = ['title', ]
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.title


class Choice(Model):
    question = ForeignKey(to=Question,
                          on_delete=CASCADE,
                          related_name='choices',
                          verbose_name='Вопрос')
    title = CharField(max_length=255, db_index=True, verbose_name='Вариант ответа')

    def __str__(self):
        return self.title


# Разные стратегии, как альтернатива для GenericForeignKey:
# https://djbook.ru/examples/88/
class Answer(Model):
    question = ForeignKey(to=Question,
                          on_delete=CASCADE,
                          related_name='answers',
                          verbose_name='Вопрос')
    respondent = ForeignKey(to=User,
                            on_delete=CASCADE,
                            related_name='answers',
                            verbose_name='Респондент')
    anonymous = BooleanField(default=False, verbose_name='Аноним')
    text = TextField(blank=True, null=True)
    radio = ForeignKey(to=Choice, on_delete=CASCADE, blank=True, null=True)
    checkbox = ManyToManyField(to=Choice, related_name='checkbox_answers', blank=True)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def render(self):
        pass
"""
