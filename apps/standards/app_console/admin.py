from django.contrib import admin
from . import models


admin.site.register(models.UserPermissions)
admin.site.register(models.GroupPermissions)

# Item
class ItemAdmin(admin.ModelAdmin):

    list_display = ('label', 'permission_type')
    search_fields = ('label', 'permission_type')

admin.site.register(models.Item, ItemAdmin)
