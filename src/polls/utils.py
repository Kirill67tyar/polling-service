from django.db.models.query import QuerySet
from django.db.models.manager import BaseManager

cyrillic_letters = {
    u'а': u'a',
    u'б': u'b',
    u'в': u'v',
    u'г': u'g',
    u'д': u'd',
    u'е': u'e',
    u'ё': u'e',
    u'ж': u'zh',
    u'з': u'z',
    u'и': u'i',
    u'й': u'i',
    u'к': u'k',
    u'л': u'l',
    u'м': u'm',
    u'н': u'n',
    u'о': u'o',
    u'п': u'p',
    u'р': u'r',
    u'с': u's',
    u'т': u't',
    u'у': u'u',
    u'ф': u'f',
    u'х': u'h',
    u'ц': u'ts',
    u'ч': u'ch',
    u'ш': u'sh',
    u'щ': u'sch',
    u'ь': u'',
    u'ы': u'y',
    u'ъ': u'',
    u'э': u'e',
    u'ю': u'u',
    u'я': u'ya',

}


def my_custom_slugify(text: str):
    text = text.replace(' ', '-')
    slug = ''
    for char in text:
        slug += cyrillic_letters.get(char, char)
    return slug


def get_view_at_console(obj, delimiter='*', unpack=False, sep='\n'):
    """
    :param obj: объект который нужно вывести в консоль
    :param delimiter: то каким символом разделять вывод в консоли сверху и снизу. Можно указать False
    :param unpack: распаковывать эдемент на методы и атрибуты или нет (помещать в dir())
    :param sep: по умолчанию равен '\n'
    :return:
    """

    name = getattr(obj, '__name__') + ' :' if hasattr(obj, '__name__') else ''
    if unpack:
        args = [sep, name, *dir(obj), sep]
    else:
        args = [sep, name, obj, sep]
    if delimiter:
        delimiter = delimiter * 25 * 2
        args.insert(1, delimiter)
        args.insert(-1, delimiter)
    return print(*args, sep='\n')


def get_view_at_console1(obj, delimiter='*', unpack=False, dictionary=False, find_type=None, find_mro=False, sep='\n'):
    """
    :param obj: объект который нужно вывести в консоль
    :param delimiter: то каким символом разделять вывод в консоли сверху и снизу. Можно указать False
    :param unpack: распаковывать эдемент на методы и атрибуты или нет (помещать в dir())
    :param sep: по умолчанию равен '\n'
    :return:
    """

    name = getattr(obj, '__name__') + ' :' if hasattr(obj, '__name__') else ''
    if unpack:
        if issubclass(type(obj), dict):
            args = [sep, name, *obj.items(), sep]
        else:
            args = [sep, name, *dir(obj), sep]
    elif dictionary:
        args = [sep, name, *obj.items(), sep]
    elif find_type:
        args = [sep, name, type(obj), sep]
    elif find_mro:
        args = [sep, name, obj.mro(), sep]
    else:
        args = [sep, name, obj, sep]
    if delimiter:
        delimiter = delimiter * 25 * 2
        args.insert(1, delimiter)
        args.insert(-1, delimiter)
    return print(*args, sep='\n')


def get_object_or_null(model, **kwargs):
    if isinstance(model, QuerySet) or isinstance(model, BaseManager):
        return model.filter(**kwargs).first()
    return model.objects.filter(**kwargs).first()
