from django.shortcuts import render, reverse
from django.views import View
from .forms import RegisterForm
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", context={"user": "user1", "form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse('recommender:index'))

        return render(request, "register.html", context={"user": "user1", "form": form})
