from datetime import datetime

from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer, Serializer, CharField

from polls.utils import get_view_at_console1, get_object_or_null, my_custom_slugify
from polls.models import (Poll, Question, Choice, Worksheet, Answer, )


# https://www.django-rest-framework.org/api-guide/fields/
# https://www.django-rest-framework.org/api-guide/serializers/

# !!! когда будешь пилить сериализаторы для user прочти статью:
# https://www.django-rest-framework.org/api-guide/fields/#choice-selection-fields

# vvv=================vvv==================vvv  WORKSPACE  vvv================vvv=================vvv
def check_poll_data(validated_data):
    start_date = validated_data['start_date']
    end_date = validated_data['end_date']
    now = timezone.now()
    if start_date:
        if start_date <= now:
            raise ValidationError('Время начала опроса не должно быть прошедшим')
        if end_date:
            if end_date <= start_date:
                raise ValidationError('Время окончания опроса не должно начинаться раньше времени начала опроса')
    return True


# ----------------  CHOICES
class ExperimentThinChoiceModelSerializer(ModelSerializer):
    choice_detail = SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs_for_built_url = Choice.objects.values_list('pk', 'question__poll_id', 'question_id')
        self.kwargs_for_built_url = {item[0]: (item[1], item[-1],) for item in kwargs_for_built_url}
        super().__init__(*args, **kwargs)

    def get_choice_detail(self, obj):
        request = self.context['request']
        pk = obj.pk
        poll_id = self.kwargs_for_built_url[pk][0]
        question_id = self.kwargs_for_built_url[pk][1]
        return request.build_absolute_uri(reverse_lazy('api:choice_detail',
                                                       kwargs={'poll_id': poll_id,
                                                               'question_id': question_id,
                                                               'pk': pk, }))

    class Meta:
        model = Choice
        fields = ('pk', 'title', 'choice_detail',)


class ThinChoiceModelSerializer(ModelSerializer):
    # choice_detail = HyperlinkedIdentityField(view_name='api:choice_detail')
    choice_detail = SerializerMethodField(read_only=True)

    def get_choice_detail(self, obj):
        request = self.context['request']
        relative_url = request.get_full_path_info().split('/')
        poll_id = relative_url[4]  # change poll_id
        question_id = relative_url[6]  # change question_id
        return request.build_absolute_uri(reverse_lazy('api:choice_detail',
                                                       kwargs={'poll_id': poll_id,
                                                               'question_id': question_id,
                                                               'pk': obj.pk, }))

    class Meta:
        model = Choice
        fields = ('id', 'title', 'choice_detail',)


class ChoiceModelSerializer(ModelSerializer):
    question = SerializerMethodField(read_only=True)
    poll_id = SerializerMethodField(read_only=True)

    def get_question(self, obj):
        return str(obj.question)

    def get_poll_id(self, obj):
        request = self.context['request']
        return int(request.get_full_path_info().split('/')[4])  # change poll_id

    class Meta:
        model = Choice
        fields = ('id', 'title', 'question', 'poll_id',)


# ----------------  QUESTIONS
class ThinQuestionModelSerializer(ModelSerializer):
    question_detail = SerializerMethodField(read_only=True)

    def get_question_detail(self, obj):
        request = self.context['request']
        relative_url = request.get_full_path_info().split('/')
        poll_id = relative_url[4]  # change poll_id
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
        return request.get_full_path_info().split('/')[4]  # change poll_id

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
            poll_id = relative_url[4]  # change poll_id
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

    def get_owner(self, obj):
        return obj.owner.email

    def get_questions_list(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(reverse_lazy('api:questions_list', kwargs={'poll_id': obj.pk, }))

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
                  'questions_list',
                  'questions',
                  )
        extra_kwargs = {'slug': {'read_only': True, }, }

    def create(self, validated_data):
        check_poll_data(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        get_view_at_console1(validated_data)
        # slug = slugify(my_custom_slugify(str(validated_data['title'])))
        # instance.slug = slug
        check_poll_data(validated_data)
        return super().update(instance, validated_data)


# ----------------  USERS
class UserSerializer(ModelSerializer):
    # password2 = CharField(required=True, write_only=True, label='Введите пароль еще раз',
    #                       style={'input_type': 'password'})  # под вопросом. можно и без этого. тогда пароль будет виден

    # style={'input_type': 'password'} - влияет только на type input формы от drf. устанавливает type="password"

    class Meta:
        model = get_user_model()
        queryset = model.objects.all()
        fields = ('id', 'email', 'password', 'name', 'admin', 'staff', 'is_active',)  # 'password2'
        extra_kwargs = {'password': {'write_only': True,
                                     'style': {'input_type': 'password'}, }, }  # под вопросом. можно и без этого
        # 'admin': {'read_only': True, },
        # 'staff': {'read_only': True, },
        # 'is_active': {'read_only': True, }, }

    def create(self, validated_data):
        password = validated_data.pop('password', '')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user
        # password2 = validated_data.pop('password2', '')
        # if password == password2:
        #     user = self.Meta.model(**validated_data)
        #     user.set_password(password)
        #     user.save()
        #     return user
        # else:
        #     raise ValidationError('Пароли должны совпадать (Passwords must be identical)')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', '')
        instance.set_password(password)
        return super().update(instance, validated_data)
        # password2 = validated_data.pop('password2', '')
        # if password == password2:
        #     instance.set_password(password)
        #     return super().update(instance, validated_data)
        # else:
        #     raise ValidationError('Пароли должны совпадать (Passwords must be identical)')


class ThinUserSerializers(ModelSerializer):
    user_detail = HyperlinkedIdentityField(view_name='api:user_detail')

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'is_active', 'user_detail',)


# ^^^=================^^^==================^^^  WORKSPACE  ^^^================^^^=================^^^

class QuestionnaireModelSerializer(ModelSerializer):
    class Meta:
        model = Worksheet
        fields = ('poll', 'respondent', 'anonymous', 'anonymous',)
        extra_kwargs = {'respondent': {'read_only': True, }, }

    def create(self, validated_data):
        # может достаточно только этого:
        validated_data['respondent'] = self.context['request'].user
        return super().create(validated_data)
        # # но если нет, то:
        # instance = self.Meta.model(**validated_data)
        # instance.save()
        # return instance


"""
class Worksheet(Model):
    poll = ForeignKey(Poll, on_delete=CASCADE, related_name='worksheets')
    respondent = ForeignKey(to=User,
                            on_delete=CASCADE,
                            related_name='answers',
                            verbose_name='Респондент')
    anonymous = BooleanField(default=False, verbose_name='Аноним')
    completed = BooleanField(default=False)
    quantity_questions = PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Прохождение опроса'
        # unique_together = ('poll', 'respondent',)

    def __str__(self):
        return f'Respondent: {self.respondent}. Poll: {self.poll.pk}){self.poll}. Completed: {self.completed}'

    def save(self, *args, **kwargs):
        if not self.quantity_questions:
            self.quantity_questions = self.poll.questions.count()
        quantity_answers = self.answers.count()
        if self.quantity_questions == quantity_answers:
            self.completed = True
        else:
            self.completed = False
        return super().save(*args, **kwargs)


class Answer(Model):
    worksheet = ForeignKey(to=Worksheet, on_delete=CASCADE, related_name='answers')
    question = ForeignKey(to=Question, on_delete=CASCADE, related_name='answers')
    text = TextField(blank=True, null=True)
    radio = ForeignKey(to=Choice, on_delete=CASCADE, blank=True, null=True)
    checkbox = ManyToManyField(to=Choice, related_name='checkbox_answers', blank=True)

    class Meta:
        unique_together = ('worksheet', 'question',)class Worksheet(Model):
    poll = ForeignKey(Poll, on_delete=CASCADE, related_name='worksheets')
    respondent = ForeignKey(to=User,
                            on_delete=CASCADE,
                            related_name='answers',
                            verbose_name='Респондент')
    anonymous = BooleanField(default=False, verbose_name='Аноним')
    completed = BooleanField(default=False)
    quantity_questions = PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Прохождение опроса'
        # unique_together = ('poll', 'respondent',)

    def __str__(self):
        return f'Respondent: {self.respondent}. Poll: {self.poll.pk}){self.poll}. Completed: {self.completed}'

    def save(self, *args, **kwargs):
        if not self.quantity_questions:
            self.quantity_questions = self.poll.questions.count()
        quantity_answers = self.answers.count()
        if self.quantity_questions == quantity_answers:
            self.completed = True
        else:
            self.completed = False
        return super().save(*args, **kwargs)


class Answer(Model):
    worksheet = ForeignKey(to=Worksheet, on_delete=CASCADE, related_name='answers')
    question = ForeignKey(to=Question, on_delete=CASCADE, related_name='answers')
    text = TextField(blank=True, null=True)
    radio = ForeignKey(to=Choice, on_delete=CASCADE, blank=True, null=True)
    checkbox = ManyToManyField(to=Choice, related_name='checkbox_answers', blank=True)

    class Meta:
        unique_together = ('worksheet', 'question',)
"""

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
