from rest_framework.permissions import BasePermission, SAFE_METHODS

from polls.utils import get_view_at_console1, get_object_or_null
from polls.models import Poll, Question, Choice


class IsOwnerOrAdmin(BasePermission):

    # def has_permission(self, request, view):
    #     return bool(request.user and request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.user.is_authenticated:
            if not user.is_admin:
                if isinstance(obj, Poll):
                    return user == obj.owner
                elif isinstance(obj, Question):
                    return user == obj.poll.owner
                elif isinstance(obj, Choice):
                    return user == obj.question.poll.owner
                else:
                    return request.method in SAFE_METHODS
            else:
                return user.is_admin


class StartDateNotCreatedOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        url = request.get_full_path_info().split('/')
        poll_id = url[3]
        poll = get_object_or_null(Poll, pk=poll_id)
        if poll:
            return bool(
                request.method in SAFE_METHODS or
                bool(not poll.start_date)
            )

    def has_object_permission(self, request, view, obj):
        # get_view_at_console1(view)
        if request.method in SAFE_METHODS:
            return True
        # return False
        elif isinstance(obj, Question):
            return not obj.poll.start_date
        elif isinstance(obj, Choice):
            return not obj.question.poll.start_date
        return False
