from django.contrib import admin

from polls.models import (Poll, Question, Answer, Choice)


class ChoiceInline(admin.StackedInline):
    model = Choice


# class QuestionInline(admin.StackedInline):
#     model = Question


@admin.register(Poll)
class PollModelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'owner',)
    list_filter = ('active',)
    search_fields = ('title', 'slug', 'description',)
    prepopulated_fields = {'slug': ('title',), }
    # inlines = (QuestionInline, )


@admin.register(Question)
class QuestionModelAdmin(admin.ModelAdmin):
    list_filter = ('type_question',)
    inlines = (ChoiceInline,)


@admin.register(Answer)
class AnswerModelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'question', 'respondent',)
    list_filter = ('anonymous',)
