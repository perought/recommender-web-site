from django.shortcuts import render
from django.views import View
from .forms import RegisterForm


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", context={"user": "user1", "form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
        return render(request, "register.html", context={"user": "user1", "form": form})
