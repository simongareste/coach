from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from club.models import Club, ClubMembership
from coach.mixins import JsonResponseMixin, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD

class ClubList(ListView):
  model = Club
  template_name = 'club/join.html'
  context_object_name = 'clubs'

  def get_queryset(self):
    # List normal clubs
    club_ids = [c['pk'] for c in Club.objects.exclude(demo=True).exclude(private=True).values('pk')]

    # Add user's clubs
    if self.request.user.is_authenticated():
      club_ids += [c['club__pk'] for c in self.request.user.memberships.values('club__pk')]

    # Load club queryset
    clubs = Club.objects.filter(pk__in=club_ids)
    clubs = clubs.prefetch_related('clubmembership_set')
    clubs = clubs.order_by('name')

    return clubs

class ClubJoin(JsonResponseMixin, TemplateView, ):
  template_name = 'club/joined.html'

  def get_context_data(self, *args, **kwargs):
    context = {}

    # Check there is no existing relation
    club = get_object_or_404(Club, slug=kwargs['slug'])
    context['club'] = club
    if club.has_user(self.request.user):
      context['error'] = 'member'
      return context

    # Create new membership
    member = ClubMembership.objects.create(club=club, user=self.request.user, role='prospect')

    # Send notification to manager
    try:
      member.mail_club()
    except Exception, e:
      print 'Notification failed : %s' % (str(e), )
      # Don't keep membership when no mail is sent
      member.delete()
      context['error'] = 'mail'

    return context
