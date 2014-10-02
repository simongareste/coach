from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from messages.forms import MessageTextForm
from sport.models import SportSession
from coach.mixins import JsonResponseMixin, JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML

class MessageSessionAdd(JsonResponseMixin, CreateView):
  template_name = 'messages/add/session.html'
  form_class = MessageTextForm

  def get_session(self):
    # Load sport session
    self.session = get_object_or_404(SportSession, pk=self.kwargs['session_id'])
    return self.session

  def get_context_data(self, *args, **kwargs):
    context = super(MessageSessionAdd, self).get_context_data(*args, **kwargs)
    context['session'] = self.get_session()
    return context

  def form_valid(self, form):
    self.get_session()

    # Save a new message
    message = form.save(commit=False)
    message.session = self.session
    message.sender = self.request.user
    message.recipient = self.session.day.week.user
    message.save()

    # Reload boxes & close modal
    self.json_options = [JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, ]
    date = self.session.day.date
    self.json_boxes = {
      'session-%s-%d' % (date, self.session.pk) : reverse('sport-session-edit', args=(date.year, date.month, date.day, self.session.pk,)),
    }
    return self.render_to_response({})
