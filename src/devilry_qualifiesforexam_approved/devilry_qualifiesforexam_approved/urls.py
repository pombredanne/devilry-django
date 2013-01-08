from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required


from .views import AllApprovedView


urlpatterns = patterns('devilry_qualifiesforexam_approved',
    url('^all/$', login_required(AllApprovedView.as_view()), name='devilry_qualifiesforexam_approved_all')
)
