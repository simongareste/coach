from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from club.views import *

club_patterns = patterns('', 
  # Manager
  url(r'^manage/?$', ClubManage.as_view(), name="club-manage"),
  url(r'^link/add/?$', ClubLinkAdd.as_view(), name="club-link-add"),
  url(r'^link/delete/(?P<id>\d+)?$', ClubLinkDelete.as_view(), name="club-link-delete"),

  # Join
  url(r'join/?$', login_required(ClubJoin.as_view()), name="club-join"),

  # Members
  url(r'^/?$', ClubMembers.as_view(), name="club-current"),
  url(r'^(?P<type>[\w]+)-by-(?P<sort>[\w-]+)/?$', ClubMembers.as_view(), name="club-current-name"),
  url(r'^by-(?P<sort>[\w-]+)/?$', ClubMembers.as_view(), name="club-current-sort"),

  # Member
  url(r'^(?P<username>[\w\_]+)/week/(?P<year>[\d]{4})/(?P<week>[\d]{1,2})/?', ClubMemberWeek.as_view(), name="club-member-week"),
  url(r'^(?P<username>[\w\_]+)/month/(?P<year>[\d]{4})/(?P<month>[\d]{1,2})/?', ClubMemberMonth.as_view(), name="club-member-month"),
  url(r'^(?P<username>[\w\_]+)/day/(?P<year>[\d]{4})/(?P<month>[\d]{1,2})/(?P<day>[\d]{1,2})/?', ClubMemberDay.as_view(), name="club-member-day"),
  url(r'^(?P<username>[\w\_]+)/role/?', ClubMemberRole.as_view(), name="club-member-role"),
  url(r'^(?P<username>[\w\_]+)/?', ClubMember.as_view(), name="club-member"),
)

urlpatterns = patterns('',
  # Create
  url(r'^create/?$', ClubCreate.as_view(), name="club-create"),

  # With an existing club
  url(r'^(?P<slug>[\w\_\-]+)/', include(club_patterns)),

  # List to Join
  url(r'join/?$', login_required(ClubList.as_view()), name="club-list"),
)
