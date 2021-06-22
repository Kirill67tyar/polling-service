from django.contrib import admin

from polls.models import (Poll, Question, Choice, Questionnaire, Answer, )


# class ChoiceInline(admin.StackedInline):
#     model = Choice
#
#
# class AnswerInline(admin.StackedInline):
#     model = Answer
#
#
# @admin.register(Poll)
# class PollModelAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'title', 'owner',)
#     search_fields = ('title', 'slug', 'description',)
#     prepopulated_fields = {'slug': ('title',), }
#     # inlines = (QuestionInline, )
#
#
# @admin.register(Question)
# class QuestionModelAdmin(admin.ModelAdmin):
#     list_filter = ('type_question',)
#     inlines = (ChoiceInline,)
#
#
# @admin.register(Questionnaire)
# class WorksheetModelAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'poll', 'respondent', 'completed', 'quantity_questions',)
#     list_filter = ('anonymous', 'completed',)
#     inlines = (AnswerInline,)
