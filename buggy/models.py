from operator import attrgetter

from fn.iters import map, filter, head

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.conf import settings


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class Project(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    name = models.CharField(_('name'), max_length=255)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return self.name


# These are all properties of Bug that live on Comment.
INHERITED_PROPERTIES = [
    'title',
    'assigned_to',
]


@python_2_unicode_compatible
class Bug(models.Model):
    class Meta:
        verbose_name = _('bug')
        verbose_name_plural = _('bugs')

    def __str__(self):
        return _('Bug #{number}: {title}').format(
            number=self.number,
            title=self.title,
        )

    @property
    def number(self):
        return self.pk


# Assign getters for the inherited properties.
def get_from_comment(attr):
    fn = attrgetter(attr)

    def inner(self):
        return head(filter(bool, map(fn, self.comments.all())))
    return inner

for attr in INHERITED_PROPERTIES:
    setattr(Bug, attr, cached_property(get_from_comment(attr)))


@python_2_unicode_compatible
class Comment(models.Model):
    bug = models.ForeignKey('buggy.Bug', verbose_name=_('bug'),
                            related_name='comments')
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('created by'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    # Bug properties
    title = models.CharField(_('title'), max_length=255, null=True, blank=True)
    assigned_to = models.ForeignKey(AUTH_USER_MODEL, null=True, blank=True,
                                    verbose_name=_('assigned to'),
                                    related_name='+')

    class Meta:
        unique_together = [
            ('bug', 'created_at'),
        ]
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return 'Comment by {user} on {created_at}'.format(
            user=self.user,
            created_at=self.created_at,
        )

    @property
    def changelist(self):
        for attr in INHERITED_PROPERTIES:
            value = getattr(self, attr, None)
            if value:
                yield (attr, value)
