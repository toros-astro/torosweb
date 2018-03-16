from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.shortcuts import render
from .forms import RegistrationForm


class SignUp(generic.CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('account:pending')
    template_name = 'registration/signup.html'


def profilepage(request, username):
    UserModel = get_user_model()
    the_user = UserModel.objects.filter(username=username).first()
    # the_userprofile = UserProfile.objects.filter(user=the_user).first()
    return render(request, 'profile_detail.html',
                  {
                  # 'userprofile': the_userprofile,
                  'the_user': the_user,
                  })
