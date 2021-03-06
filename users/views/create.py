from users.models import Athlete
from django.views.generic.edit import FormView
from users.forms import SignUpForm
from django.contrib.auth import login as auth_login, authenticate
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .mixins import UserInviteMixin

class CreateUser(UserInviteMixin, FormView):
  template_name = 'users/create.html'
  form_class = SignUpForm

  def get_context_data(self, *args, **kwargs):
    context = super(CreateUser, self).get_context_data(*args, **kwargs)

    # Use invite recipient data by default
    if self.invite:
      context['form'].fields['email'].initial = self.invite.recipient
      context['form'].fields['lastname'].initial = self.invite.name

    return context

  def form_valid(self, form):
    # Create user
    user = Athlete.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
    user.first_name = form.cleaned_data['firstname']
    user.last_name = form.cleaned_data['lastname']
    user.build_avatar()
    user.save()

    # Auto login
    valid_user = authenticate(email=user.email, password=form.cleaned_data['password'])
    if valid_user is not None:
      auth_login(self.request, valid_user)

    # When an invite is used, redirect to club creation
    # Otherwise, display club list
    url_name = self.invite and 'club-create' or 'club-list'

    # Subscribe user to mailing all
    user.subscribe_mailing('all')

    return HttpResponseRedirect(reverse(url_name))
