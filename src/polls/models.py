from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import (Model, CharField, SlugField, TextField,
                              DateTimeField, BooleanField, PositiveIntegerField,
                              ForeignKey, ManyToManyField, URLField, CASCADE, SET_NULL,)

from polls.utils import my_custom_slugify
from polls.fields import CountAnswersField

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

    class Meta:
        # https://docs.djangoproject.com/en/3.2/ref/models/options/
        ordering = ['title', ]
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(my_custom_slugify(str(self.title)))
        return super(Poll, self).save(*args, **kwargs)


"""
возможно здесь придется переписать type_question чтобы был обычный CharField. 
А дальше на уровне сохранения serializer(create) если не checkbox/radio/text
то сохранять type_question как text
"""


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


class Questionnaire(Model):
    poll = ForeignKey(Poll, on_delete=SET_NULL, null=True, related_name='questionnaires')
    respondent = ForeignKey(to=User,
                            on_delete=CASCADE,
                            related_name='questionnaires',
                            verbose_name='Респондент')
    anonymous = BooleanField(default=False, verbose_name='Аноним')
    completed = BooleanField(default=False)
    quantity_questions = PositiveIntegerField(blank=True, null=True)
    questions_list = URLField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Прохождение опроса'
        unique_together = ('poll', 'respondent',)

    def __str__(self):
        return f'Respondent: {self.respondent}. Poll: {self.poll.pk}){self.poll}. Completed: {self.completed}'

    def save(self, *args, **kwargs):
        if not self.quantity_questions:
            self.quantity_questions = self.poll.questions.count()
        return super().save(*args, **kwargs)


class Answer(Model):
    questionnaire = ForeignKey(to=Questionnaire, on_delete=CASCADE, related_name='answers')
    question = ForeignKey(to=Question, on_delete=CASCADE, related_name='answers')
    count_answers = CountAnswersField(blank=True, null=True, for_fields=['questionnaire', ])
    text = TextField(blank=True, null=True)
    radio = ForeignKey(to=Choice, on_delete=CASCADE, blank=True, null=True)
    checkbox = ManyToManyField(to=Choice, related_name='checkbox_answers', blank=True)

    class Meta:
        unique_together = ('questionnaire', 'question',)



"""
убрать поле active из Poll - оно там нигде не используется.

сделать дополнительный url api/polls-workspace/..
и возможно перенести весь функционал для админа и staff туда,
а в обычном polls сдулать функционал для обычных пользователей.

в функционале для пользователя нужно иметь получить список активных опросов
критерии активного опроса:
список из опросов с созданным start_date. start_date должен начинаться раньше сегодняшней даты.
end_date не обязателен, но если он есть, то сегодняшняя дата должны быть между start_date и end_date
только такой опрос должен считаться активным


теперь модели для обычных юзеров:
вместо одной Answer сделать две модели - Questionnaire, Answer

Answer ссылается на Questionnaire по ForeignKey
нужно сделать так, чтобы Questionnaire был привязан к Poll и к User по ForeignKey
а Answer к Question по ForeignKey

!!! Нужно придумать такой механизм, чтобы если отвечены не все вопросы Опроса,
то прохождение опроса (Questionnaire) считался не завершенным.
Можно подумать о поле на уровне модели. 
poll_instance.questions.count() - будет кол-во вопросов в конкретном опросе
Questionnaire_instance.answers.count() - будет кол-во ответов данных на опрос.

можно подумать о создании своего поля в Questionnaire который при создании экземпляра Questionnaire
будет брать кол-во ответов и сверять их с количеством вопросов в опросе
кол-во опросов в опросе можно сохранять тогда в отдельное поле в Questionnaire
!!!

class Questionnaire(Model):
    poll = ForeignKey(Poll, on_delete=CASCADE, related_name='Questionnaires')
    respondent = ForeignKey(to=User,
                            on_delete=CASCADE,
                            related_name='answers',
                            verbose_name='Респондент')
    anonymous = BooleanField(default=False, verbose_name='Аноним')
    quantity_questions = PositiveIntegerField (под вопросом)
    custom_field
    
class Answer(Model):
    Questionnaire = ForeignKey(Questionnaire, on_delete=CASCADE, related_name='answers')
    question = ForeignKey(to=Question, on_delete=CASCADE)
    
    class Meta:
        unique_together = ('Questionnaire', 'question',)
        
        
        
course = ForeignKey('Course', on_delete=CASCADE, related_name='modules')
order = OrderField(blank=True, for_fields=['course', ])


!!!
Может стоит при выводе данных в JSON сделать ключ meta-data и в 
этом ключе, допустим для choice detail, выводить poll_id, question_id, user_id
"""

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
