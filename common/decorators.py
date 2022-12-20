from django.http import HttpResponseBadRequest


def is_ajax(request):
    """Пре определил метод так как он устарел"""
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def ajax_required(f):
    """Код ошибки – 400,если запрос не является AJAX-запросом"""

    def wrap(request, *args, **kwargs):
        if not is_ajax(request=request):
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
