from django.http import JsonResponse
from django.shortcuts import render


def checking(request):
    return JsonResponse({'status': 'ok', })
