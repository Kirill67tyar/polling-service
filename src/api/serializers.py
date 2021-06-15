from django.contrib.auth import get_user_model
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


# ----------------  CHOICES
class ThinChoiceModelSerializer(ModelSerializer):
    choice_detail = SerializerMethodField(read_only=True)

    def get_choice_detail(self, obj):
        request = self.context['request']
        relative_url = request.get_full_path_info().split('/')
        poll_id = relative_url[3]
        question_id = relative_url[5]
        return request.build_absolute_uri(reverse_lazy('api:choice_detail',
                                                       kwargs={'poll_id': poll_id,
                                                               'question_id': question_id,
                                                               'pk': obj.pk, }))

    class Meta:
        model = Choice
        fields = ('pk', 'title', 'choice_detail',)


class ChoiceModelSerializer(ModelSerializer):
    question = SerializerMethodField(read_only=True)
    poll_id = SerializerMethodField(read_only=True)

    def get_question(self, obj):
        return str(obj.question)

    def get_poll_id(self, obj):
        request = self.context['request']
        return request.get_full_path_info().split('/')[5]

    class Meta:
        model = Choice
        fields = ('id', 'title', 'question', 'poll_id',)


# ----------------  QUESTIONS
class ThinQuestionModelSerializer(ModelSerializer):
    question_detail = SerializerMethodField(read_only=True)

    def get_question_detail(self, obj):
        request = self.context['request']
        relative_url = request.get_full_path_info().split('/')
        poll_id = relative_url[3]
        if isinstance(obj, Question):
            return request.build_absolute_uri(reverse_lazy('api:question_detail',
                                                           kwargs={'poll_id': poll_id,  # obj.poll.pk,
                                                                   'pk': obj.pk, }))
        return None

    class Meta:
        model = Question
        fields = ('id', 'title', 'type_question', 'question_detail',)


class QuestionModelSerializer(ModelSerializer):
    poll_id = SerializerMethodField(read_only=True)

    # choices = ThinChoiceModelSerializer(many=True, read_only=True)

    def take_poll_id(self):
        request = self.context['request']
        return request.get_full_path_info().split('/')[5]

    def get_poll_id(self, obj):
        return obj.poll.pk

    # возвращает OrderedDict одного instance
    # который будет рендериться
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # get_view_at_console1(ret, delimiter='N')
        type_question = ret['type_question']
        request = self.context['request']
        if type_question in ('radio', 'checkbox',):
            pk = ret.get('id')
            relative_url = request.get_full_path_info().split('/')
            poll_id = relative_url[3]
            ret['choices_list'] = request.build_absolute_uri(reverse_lazy('api:choices_list',
                                                                          kwargs={'poll_id': poll_id,
                                                                                  'question_id': pk, }))
        return ret

    class Meta:
        model = Question
        fields = ('id', 'poll_id', 'title', 'type_question',)  # 'choices',)


# ----------------  POLLS
class ThinPollModelSerializer(ModelSerializer):
    poll_detail = HyperlinkedIdentityField(view_name='api:poll_detail')
    quantity_questions = SerializerMethodField(read_only=True)
    owner = SerializerMethodField(read_only=True)

    def get_quantity_questions(self, obj):
        return obj.questions.count()

    def get_owner(self, obj):
        return obj.owner.email

    class Meta:
        model = Poll
        fields = ('id', 'title', 'owner', 'quantity_questions', 'poll_detail',)


class PollModelSerializer(ModelSerializer):
    questions = ThinQuestionModelSerializer(many=True, read_only=True)
    owner = SerializerMethodField(read_only=True)
    questions_list = SerializerMethodField(read_only=True)
    slug = SerializerMethodField(read_only=True)

    def get_owner(self, obj):
        return obj.owner.email

    def get_questions_list(self, obj):
        request = self.context['request']
        relative_url = request.get_full_path_info().split('/')
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
                  'questions_list',
                  'questions',
                  )


# ----------------  USERS
class UserSerializer(ModelSerializer):
    # polls_list_second = HyperlinkedIdentityField(view_name='api:polls_list')
    polls_list = SerializerMethodField(read_only=True)

    def get_polls_list(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(reverse_lazy('api:polls_list'))

    class Meta:
        model = get_user_model()
        queryset = model.objects.all()
        fields = 'id', 'email', 'password', 'name', 'admin',  # 'polls_list_second',
        extra_kwargs = {'password': {'write_only': True, }, }

    def create(self, validated_data):
        password = validated_data.pop('password', '')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.set_password(validated_data.pop('password', ''))
        return super().update(instance, validated_data)


class ThinUserSerializers(ModelSerializer):
    user_detail = SerializerMethodField(read_only=True)

    def get_user_detail(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(reverse_lazy('api:user_detail'), kwargs={'pk': obj.pk})

    class Meta:
        model = get_user_model()
        fields = 'id', 'email', 'is_active', 'polls_list',


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
