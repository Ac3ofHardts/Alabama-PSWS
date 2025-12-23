from django.shortcuts import redirect
from django.urls import reverse

class AnalysisRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "analysis" in request.path.lower():
            return redirect(reverse("under_construction"))
        return self.get_response(request)


