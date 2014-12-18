# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view

from mark2cure.account.models import UserProfile
from mark2cure.common.models import Task, UserQuestRelationship
from .forms import UserCreateForm, UserNameChangeForm, UserProfileForm

from brabeion import badges
from brabeion.models import BadgeAward

import datetime
import os


@login_required
def settings(request):
    """"
        Use this endpoint for strict user setting modifications
        like password (auth.user)
    """
    user_change_form = UserNameChangeForm(instance=request.user, data=request.POST or None)
    user_profile_form = UserProfileForm(instance=request.user.profile, data=request.POST or None)
    user_password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        user_change_form.save()
        user_profile_form.save()
        user_password_form.save()
        return redirect('mark2cure.account.views.settings')

    return TemplateResponse(request,
            'account/settings.jade',
            {'user_change_form': user_change_form,
             'user_profile_form': user_profile_form,
             'user_password_form': user_password_form})


@api_view(['GET'])
@login_required
def user_points(request):
    points_badge = BadgeAward.objects.filter(user=request.user, slug='points').last()
    skill_badge =  BadgeAward.objects.filter(user=request.user, slug='skill').last()

    return Response({
        'points': request.user.userprofile.rating_score,
        'points_level': points_badge.name,
        'skill_level': skill_badge.name
    })


def user_creation(request):
    user_create_form = UserCreateForm(data=request.POST or None)
    if request.POST and user_create_form.is_valid():
        user = user_create_form.save()

        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password1'])
        auth_login(request, user)

        # In order to create an account they've already done the
        # first 2 training Tasks
        task = Task.objects.first()
        badges.possibly_award_badge("skill_awarded", user=user, level=task.provides_qualification)
        user.profile.rating.add(score=task.points, user=None, ip_address=os.urandom(7).encode('hex'))
        UserQuestRelationship.objects.create(task=task, user=user, completed=True)

        # Redirect them back b/c of the UserProfileForm
        return redirect('/account/create/settings/')

    return TemplateResponse(request, 'account/create.jade', {'form': user_create_form})


@login_required
def user_creation_settings(request):
    user_change_form = UserNameChangeForm(instance=request.user, data=request.POST or None)
    user_profile_form = UserProfileForm(instance=request.user.profile, data=request.POST or None)

    if request.POST and user_profile_form.is_valid():
        user_change_form.save()
        user_profile_form.save()
        # They already have an account, let's get them
        # started!
        return redirect('mark2cure.common.views.dashboard')

    return TemplateResponse(request, 'account/create-settings.jade',
            {'user_change_form': user_change_form,
             'user_profile_form': user_profile_form})


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    email = request.POST.get('email', None)
    notify = request.POST.get('email_notify', False)
    if notify is not False:
      notify = True

    if email:
      u, created = User.objects.get_or_create(username=email, email=email)
      if created:
        u.set_password('')
        profile = u.profile
        profile.email_notify = notify
        profile.save()
      u.save()

      return redirect('/')
    return HttpResponse('Unauthorized', status=401)

