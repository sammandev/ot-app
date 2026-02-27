"""
Soft delete manager for models.
Provides custom queryset that excludes deleted records by default.
"""

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """Custom QuerySet that excludes soft-deleted objects."""

    def delete(self):
        """Soft delete all objects in the queryset.

        Uses bulk update() for performance. Individual model save()
        methods and post_save signals will NOT fire. Use model-level
        delete() for single-object soft deletes that need signals.
        """
        count = self.update(is_deleted=True, deleted_at=timezone.now())
        return (count, {self.model._meta.label: count})

    def hard_delete(self):
        """Permanently delete all objects in the queryset."""
        return super().delete()

    def alive(self):
        """Return only non-deleted objects."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Return only deleted objects."""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""

    def get_queryset(self):
        """Return queryset excluding soft-deleted objects."""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        """Return all objects including soft-deleted ones."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Return only soft-deleted objects."""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)


class SoftDeleteMixin(models.Model):
    """
    Mixin that adds soft delete functionality to a model.

    Usage:
        class MyModel(SoftDeleteMixin, models.Model):
            name = models.CharField(max_length=100)

            objects = SoftDeleteManager()
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete the object.

        Calls save(), which emits post_save (not post_delete) signals.
        Signal handlers that need to react to soft deletes should
        listen for post_save and check the is_deleted field.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["is_deleted", "deleted_at"])
        return (1, {self._meta.label: 1})

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object."""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
