"""
Serializers for Access Control Management
"""

from rest_framework import serializers

from .models import ExternalUser


class UserAccessSerializer(serializers.ModelSerializer):
    """Serializer for managing user access control"""

    class Meta:
        model = ExternalUser
        fields = [
            "id",
            "username",
            "worker_id",
            "email",
            "first_name",
            "last_name",
            "is_ptb_admin",
            "is_superuser",
            "is_staff",
            "is_active",
            "role",
            "menu_permissions",
            "event_reminders_enabled",
            "permission_updated_at",
        ]
        read_only_fields = ["id", "email", "first_name", "last_name", "permission_updated_at"]


class UserAccessUpdateSerializer(serializers.Serializer):
    """Serializer for updating user access permissions"""

    is_ptb_admin = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    role = serializers.ChoiceField(choices=ExternalUser.Role.choices, required=False)
    menu_permissions = serializers.JSONField(required=False)
    event_reminders_enabled = serializers.BooleanField(required=False)
