from django.db.models import PositiveIntegerField


class CountAnswersField(PositiveIntegerField):

    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(CountAnswersField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        qs = self.model.objects.all()
        query = {field: getattr(model_instance, field) for field in self.for_fields}
        count_answers = qs.filter(**query).count() + 1
        questionnaire = model_instance.questionnaire
        if questionnaire.quantity_questions == count_answers:
            questionnaire.completed = True
        else:
            questionnaire.completed = False
        questionnaire.save()
        return count_answers


"""
    for_fields - список или тапл в котором должны содержаться
    названия моделей ForeignKey(ManyToOne для модели где определено поле),
    типа for_fields=['course', ]
    pre_save - метод уже есть в PositiveIntegerField (а может и вообще в Field)
    выполяется перед тем, как Django сохранит поле в бд
    в слуае с PositiveIntegerField возвращает значение поля, которое должно быть сохранено в бд
    возможно pre_save - это такой метод, который специально дает возможность поработать со значением поля
    перед сохранением в бд, т.е. метод для кастомных полей. Но это только возможно.
    вот как он выглядит в классе Field:
        def pre_save(self, model_instance, add):
            'Return field's value just before saving.'
            return getattr(model_instance, self.attname)
    model_instance - экземпляр модели, где определено поле
    self.attname - атрибут экземпляра класса поля,
    дает переменную атрибута в формате str, к которой мы присвоили наше поле
    self.model - модель где определено наше поле
    как создавать классы для полей модели:
    https://docs.djangoproject.com/en/3.2/howto/custom-model-fields/
"""
