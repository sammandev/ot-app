from django.utils import timezone

from api.models import UserActivityLog


def purge_user_activity_logs_older_than(days: int):
	threshold_days = int(days)
	if threshold_days < 1:
		raise ValueError('days must be a positive integer')

	cutoff = timezone.now() - timezone.timedelta(days=threshold_days)
	deleted_count, _ = UserActivityLog.objects.filter(timestamp__lt=cutoff).delete()
	return {
		'deleted_count': deleted_count,
		'days': threshold_days,
		'cutoff': cutoff,
	}