from django.http import JsonResponse
from django.shortcuts import render

from polls.models import Poll
from polls.utils import get_object_or_null, get_view_at_console1


def checking(request):
    poll = Poll.objects.latest('pk')
    # print(poll.start_date)
    # print(poll.start_date == None)
    # get_view_at_console1(request.user.is_staff)
    for attr, delimetr in (('get_full_path','!',),
                          ('get_full_path_info','@',),
                          ('path','#',),
                          ('path_info','$',),
                          ('get_raw_uri','%',),):
        # get_view_at_console1(getattr(request, attr), delimiter=delimetr)
        pass

    # get_view_at_console1(request.user.is_admin)
    get_view_at_console1(request.get_full_path(), delimiter='!')
    get_view_at_console1(request.get_full_path_info(), delimiter='@')
    get_view_at_console1(request.get_raw_uri(), delimiter='#')
    return JsonResponse({'status': 'ok', })

"""
get_full_path
get_full_path_info
path
path_info
get_raw_uri
"""