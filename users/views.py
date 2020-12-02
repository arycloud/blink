import json
from django.contrib.auth.models import Permission
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from courses.models import Course, Subject
from .forms import *


def home(request):
    courses = Course.objects.all()
    # courses = Course.objects.prefetch_related("owner").all()
    subjects = Subject.objects.all()
    context = {'courses': courses, 'subjects': subjects}
    return render(request, 'base.html', context)


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(email=username, password=password)
            print(user)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse_lazy('home'))
        else:
            print(form.errors)
    else:

        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect(reverse_lazy('home'))

    return render(request, 'users/logout.html')


def registration_view(request):
    form = RegistrationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        print('get post req')
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            if form.cleaned_data['is_instructor'] is True:
                permission = Permission.objects.get(name='Can add course')
                instructor_group = Group.objects.get(name='instructor')
                user.groups.add(instructor_group)
                user.user_permissions.add(permission)
            else:
                permission = Permission.objects.get(name='Can view course')
                student_group = Group.objects.get(name='students')
                user.groups.add(student_group)
                user.user_permissions.add(permission)
            return HttpResponseRedirect(reverse_lazy('users:login'))
        else:
            print(form.errors)
    return render(request, 'users/register.html', {'form': form})


def user_profile(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            context = {}
            if request.user.is_instructor:
                courses = Course.objects.filter(owner=request.user.id)
                print(courses)
                context['courses'] = courses
            if request.user.courses_joined:
                courses_joined = Course.objects.filter(
                    students__courses_joined__students__exact=request.user)
                context['courses_joined'] = courses_joined
                print(courses_joined.values)
        return render(request, 'users/profile.html', context)
