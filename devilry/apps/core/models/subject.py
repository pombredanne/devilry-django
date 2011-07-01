from datetime import datetime

from django.utils.translation import ugettext as _
from django.db.models import Q
from django.contrib.auth.models import User
from django.db import models

from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from custom_db_fields import ShortNameField, LongNameField
from basenode import BaseNode
from node import Node

class Subject(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate):
    """

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Node`_.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        `Node`_.

    .. attribute:: short_name

        A django.db.models.SlugField_ with max 20 characters. Only numbers,
        letters, '_' and '-'. Unlike all other children of
        :class:`BaseNode`, Subject.short_name is **unique**. This is mainly
        to avoid the overhead of having to recurse all the way to the top of
        the node hierarchy for every unique path.


    .. attribute:: periods

        A set of periods for this subject 
    """

    class Meta:
        app_label = 'core'
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ['short_name']

    short_name = ShortNameField(unique=True)
    long_name = LongNameField()
    parentnode = models.ForeignKey(Node, related_name='subjects')
    admins = models.ManyToManyField(User, blank=True)

    @classmethod
    def q_is_admin(cls, user_obj):
            return Q(admins__pk=user_obj.pk) \
                | Q(parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def get_by_path(self, path):
        """ Get a Subject by path.

        Only matches on :attr:`short_name` for subjects because it is
        guaranteed to be unique.

        Raises :exc:`Subject.DoesNotExist` if the query does not match.
        
        :param path: The :attr:`short_name` of a subject.
        :return: A Subject-object.
        """
        return Subject.objects.get(short_name=path)

    def get_path(self):
        """ Only returns :attr:`short_name` for subject since it is
        guaranteed to be unique. """
        return self.short_name

    #TODO delete this?
    #def clean(self, *args, **kwargs):
        #super(Subject, self).clean(*args, **kwargs)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(periods__assignments__publishing_time__lt=now)
        if not active:
            q &= ~Q(periods__end_time__gte=now)
        if not old:
            q &= ~Q(periods__end_time__lt=now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(periods__assignments__assignmentgroups__examiners=user_obj)

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(periods__assignments__assignmentgroups__candidates=user_obj)
