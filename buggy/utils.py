from django.db import models
from django.db.models import query

if hasattr(models.Manager, 'from_queryset'):
    Manager = models.Manager
else:
    # Minimal and lazy backport of https://github.com/django/django/pull/1328
    class Manager(models.Manager):
        @classmethod
        def from_queryset(cls, queryset_class, class_name=None):
            if class_name is None:
                class_name = '%sFrom%s' % (cls.__name__,
                                           queryset_class.__name__)
            return type(class_name, (cls, ), {'_queryset_class': queryset_class})

        def get_queryset(self):
            return self._queryset_class(self.model, using=self.db)

        get_query_set = get_queryset # BBB

        def __getattr__(self, name):
            try:
                return super(Manager, self).__getattr__(name)
            except AttributeError:
                # Don't copy dunder methods
                if not name.startswith('_') and name not in ('delete', 'as_manager'):
                    attribute = getattr(self.get_queryset(), name, None)
                    if callable(attribute):
                        return attribute
                raise

if hasattr(query.QuerySet, 'as_manager'):
    QuerySet = query.QuerySet
else:
    # Minimal and lazy backport of https://github.com/django/django/pull/1328
    class QuerySet(query.QuerySet):
        @classmethod
        def as_manager(cls):
            return Manager.from_queryset(cls)()
