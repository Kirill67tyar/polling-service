# from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import (Model, CharField, SlugField, TextField,
                              DateTimeField, BooleanField, PositiveIntegerField,
                              ForeignKey, OneToOneField, ManyToManyField, CASCADE, )

User = settings.AUTH_USER_MODEL


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


class Question(Model):
    CHOICES = (
        ('text', 'Text',),
        ('radio', 'Radio',),
        ('checkbox', 'Checkbox',),
    )
    poll = ForeignKey(to=Poll,
                      on_delete=CASCADE,
                      related_name='questions',
                      verbose_name='Вопрос')
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


# Разные стратегии, как альтернатива GenericForeignKey:
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
    checkbox = ManyToManyField(to=Choice, related_name='checkbox_answers', blank=True, null=True)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def render(self):
        pass


## ------------------------------------------------------------------------------------------
## Альтернатива с ContentType (GenericForeignKey)
# class AlternativeAnswer(Model):
#     question = ForeignKey(to=Question,
#                           on_delete=CASCADE,
#                           related_name='answers',
#                           verbose_name='Вопрос')
#     respondent = ForeignKey(to=User,
#                             on_delete=CASCADE,
#                             related_name='answers',
#                             verbose_name='Респондент')
#     anonymous = BooleanField(default=False, verbose_name='Аноним')
#     answer_type = ForeignKey(to=ContentType,
#                              on_delete=CASCADE,
#                              limit_choices_to={'model__in': ('textanswer',
#                                                              'radioanswer',
#                                                              'checkboxanswer',)}, )
#     object_id = PositiveIntegerField()
#     item = GenericForeignKey('answer_type', 'object_id')
#
#     class Meta:
#         verbose_name = 'Ответ'
#         verbose_name_plural = 'Ответы'
#
#
# class BaseItem(Model):
#     class Meta:
#         abstract = True
#
#     def render(self):
#         pass
#
#
# class TextAnswer(BaseItem):
#     text = TextField()
#
#
# class RadioAnswer(BaseItem):
#     # был OneToOne но он здесь не подходит
#     radio = ForeignKey(to=Choice, on_delete=CASCADE, related_name='radio_answers')
#
#
# class CheckBoxAnswer(BaseItem):
#     # ManyToManyField здесь не подходит
#     checkbox = ManyToManyField(to=Choice, related_name='checkbox_answers')


"""
Poll
    owner
    title
    start_date
    end_date
    description
    created?
    active?
    
Question
    poll (ForeignKey Poll)
    text
    type_question choices=CHOICES
    ИЛИ
    тоже здесь создать обобщенную связь
    
Choice
    question (ForeignKey Question)
    title
    
Answer
    question (ForeignKey - Question)
    respondent (ForeignKey - User)
    anonymous (BooleanField (default=False))
    
    Трио обобщенной связи на три модели:
    
    TextAnswer
        text = (CharField)
        
    RadioAnswer
        radio = (OneToOneField Choice)
        
    CheckBoxAnswer
        checkbox = (ManyToManyField Choice)
        
    
 
    
    (В tz написано 'один пользователь 
может участвовать в любом количестве опросов'
Я прежлагаю сделать так - пользователь может проходить уже пройденные опросы,
но старый результат сбрасывается. И должно быть помечено, что пользователь проходит заново)
"""
