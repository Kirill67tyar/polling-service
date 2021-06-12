from django.http import JsonResponse
from django.shortcuts import render

from polls.models import Poll
from polls.utils import get_object_or_null


def checking(request):
    poll = Poll.objects.latest('pk')
    print(poll.start_date)
    print(poll.start_date == None)
    return JsonResponse({'status': 'ok', })
