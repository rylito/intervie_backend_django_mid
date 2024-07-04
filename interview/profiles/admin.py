from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from interview.profiles.models import UserProfile


class UserProfileAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets

    # add the avatar field to the default fieldsets
    fieldsets[1][1]['fields'] += ('avatar',)

    # add is_admin to the default fieldsets
    fieldsets[2][1]['fields'] = (
        'is_active',
        'is_staff',
        'is_superuser',
        'is_admin',
        'groups', 'user_permissions'
    )


admin.site.register(UserProfile, UserProfileAdmin)
