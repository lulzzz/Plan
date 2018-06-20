from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile


class ProfileAdminInline(admin.StackedInline):
    model = Profile
    exclude = ('is_test_user',)


class UserAdmin(admin.ModelAdmin):
    model = User

    # List view
    actions = ['make_staff', 'deactivate']

    def make_staff(self, request, queryset):
        rows_updated = queryset.update(is_staff=True)

        if rows_updated == 1:
            message = '1 user was'
        else:
            message = '{} users were'.format(rows_updated)

        message += ' successfully made staff.'
        self.message_user(request, message)
    make_staff.short_description = ('Allow user to access admin site.')

    def deactivate(self, request, queryset):
        rows_updated = queryset.update(is_active=False)

        if rows_updated == 1:
            message = '1 user was'
        else:
            message = '{} users were'.format(rows_updated)

        message += ' successfully deactivated.'
        self.message_user(request, message)
    deactivate.short_description = ('Deactivate user account.')

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return tuple()
        inline_instance = ProfileAdminInline(
            self.model, self.admin_site
        )
        return(inline_instance,)


# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
