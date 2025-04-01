import threading

from django.http import HttpResponsePermanentRedirect


class RequestMiddleware:

    def __init__(self, get_response, thread_local=threading.local()):
        self.get_response = get_response
        self.thread_local = thread_local
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        self.thread_local.current_request = request

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
    
class WwwRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().partition(":")[0]
        print("host",host)
        if host == "www.motrum.yuriyzhidkov.ru":
            return HttpResponsePermanentRedirect("https://motrum.yuriyzhidkov.ru" + request.path)
        elif host == "www.localhost":
            return HttpResponsePermanentRedirect("http://localhost:8000" + request.path)
        elif host == "www.test.motrum.ru":
            return HttpResponsePermanentRedirect("https://test.motrum.ru" + request.path)
        elif host == "www.motrum.ru":
            return HttpResponsePermanentRedirect("https://motrum.ru" + request.path)
        else:
            return self.get_response(request)
