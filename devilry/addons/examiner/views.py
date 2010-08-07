from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.db.models import Count

from devilry.core.models import Delivery, AssignmentGroup, Assignment
from devilry.core import gradeplugin
from devilry.core.utils.GroupNodes import group_assignments


@login_required
def list_assignmentgroups(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_groups = assignment.assignment_groups_where_is_examiner(
            request.user)
    return render_to_response(
            'devilry/examiner/list_assignmentgroups.django.html', {
                'assignment_groups': assignment_groups,
                'assignment': assignment,
            }, context_instance=RequestContext(request))

@login_required
def show_assignmentgroup(request, assignmentgroup_id):
    assignment_group = get_object_or_404(AssignmentGroup, pk=assignmentgroup_id)
    if not assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    return render_to_response(
            'devilry/examiner/show_assignmentgroup.django.html', {
                'assignment_group': assignment_group,
            }, context_instance=RequestContext(request))

@login_required
def correct_delivery(request, delivery_id):
    delivery_obj = get_object_or_404(Delivery, pk=delivery_id)
    if not delivery_obj.assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    key = delivery_obj.assignment_group.parentnode.grade_plugin
    return gradeplugin.registry.getitem(key).view(request, delivery_obj)

@login_required
def choose_assignment(request):
    assignments = Assignment.active_where_is_examiner(request.user)
    subjects = group_assignments(assignments)
    return render_to_response(
            'devilry/examiner/choose_assignment.django.html', {
                'subjects': subjects,
            }, context_instance=RequestContext(request))


from django.db.models import Q
from django.utils.simplejson import JSONEncoder
from django.core.urlresolvers import reverse
from django import http

@login_required
def assignmentgroup_filtertable_json(request):
    def latestdeliverytime(g):
        d = g.get_latest_delivery()
        if d:
            return d.time_of_delivery.strftime("%Y-%m-%d %H:%M")
        else:
            return ""

    maximum = 20
    term = request.GET.get('term', '')
    showall = request.GET.get('all', 'no')

    groups = AssignmentGroup.where_is_examiner(request.user).order_by(
            'parentnode__parentnode__parentnode__short_name',
            'parentnode__parentnode__short_name',
            'parentnode__short_name',
            )
    if term != '':
        groups = groups.filter(
            Q(name__contains=term)
            | Q(examiners__username__contains=term)
            | Q(candidates__student__username__contains=term))

    if not request.GET.get('nodeliveries'):
        groups = groups.filter(Q(deliveries__isnull=False))

    groups = groups.distinct()
    allcount = groups.count()

    if showall != 'yes':
        groups = groups[:maximum]
    l = [dict(
            id = g.id,
            path = [
                g.parentnode.parentnode.parentnode.short_name,
                g.parentnode.parentnode.short_name,
                g.parentnode.short_name,
                str(g.id), g.get_candidates(), g.name,
                latestdeliverytime(g),
                g.get_status(),
            ],
            editurl = reverse('devilry-examiner-show_assignmentgroup',
                    args=[str(g.id)]))
        for g in groups]
    data = JSONEncoder().encode(dict(result=l, allcount=allcount))
    response = http.HttpResponse(data, content_type="text/plain")
    return response
