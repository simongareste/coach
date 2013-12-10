from django.views.generic.edit import FormView
from datetime import date, timedelta, datetime
from helpers import date_to_week, date_to_day
from mixins import PlanMixin
from plan.forms import PlanApplyWeekForm
from run.models import RunReport

class PlanApply(PlanMixin, FormView):
  weeks_nb = 6
  template_name = 'plan/apply.html'
  form_class = PlanApplyWeekForm

  def form_valid(self, form):
    # Get start date
    start_date = datetime.strptime(form.cleaned_data['week'], '%Y-%m-%d').date()

    # Only whole club trainer's athletes are supported
    # TODO: support single athlete or sub group of athletes
    athletes = self.list_athletes()
    club_id = form.cleaned_data['club']
    if club_id not in athletes:
      raise Exception("Invalid club")
    self.plan.apply(start_date, [a.user for a in athletes[club_id]['members']])


    # Build applied context
    context = self.get_context_data()
    return self.render_to_response(context)

  def get_context_data(self, *args, **kwargs):
    context = super(PlanApply, self).get_context_data(*args, **kwargs)
    context['athletes'] = self.list_athletes()
    context['weeks'] = self.list_weeks()
    return context

  def list_weeks(self):
    '''
    Get next X weeks year/week couples
    '''
    weeks = []
    for i in range(0, self.weeks_nb):
      d = date.today() + timedelta(days=i*7)
      weeks.append(date_to_week(d))
    return weeks

  def list_athletes(self):
    '''
    List trainer athletes by application
    '''

    # Get time interval, from this monday
    # to sunday in 6 weeks
    date_start = date_to_day(date.today())
    date_end = date_start + timedelta(self.weeks_nb * 7 + 6)

    out = {}
    athletes = self.request.user.trainees
    for club in self.clubs:
      club_athletes = athletes.filter(club=club)

      # Look for busied run reports
      # in the time interval
      users = [ca.user for ca in club_athletes]
      reports_busy = RunReport.objects.filter(user__in=users, sessions__date__range=(date_start, date_end), plan_week__isnull=False).distinct()

      # Linearize by athlete & year/week
      # to display a table of 6 weeks availiblity
      busy_dict = {}
      for r in reports_busy:
        name = "%s_%d_%d" % (r.user.username, r.year, r.week)
        busy_dict[name] = r

      out[club.id] = {
        'members' : club_athletes.order_by('user__first_name', 'user__last_name', ),
        'busy' : busy_dict,
      }
      
    return out

