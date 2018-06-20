from django.shortcuts import get_object_or_404


class SecurityModelNameMixin():

    def set_user(self, user):
        self.user = user

    def get_model_name(self, user):
        r"""
        Security query to make sure model exists and user group has permissions
        """
        #  Set user
        self.set_user(user)

        # Get parameters from URL
        model_name = self.kwargs.get('item', None)

        # Check if parameter is valid
        valid_models = self.get_authorized_model_item_list()
        if model_name not in valid_models:
            return 401

        return model_name


    def get_authorized_model_item_list(self):
        r"""
        Security query get the models user can access
        """
        if type(self.permission_type) is not list:
            self.permission_type = [self.permission_type]

        # Return all item objects if user is superuser
        if self.user.is_superuser:
            return list(self.target_model.objects.filter(permission_type__in=self.permission_type).values_list('name', flat=True))

        # Get user individual permissions
        output_list = list()
        for perm in self.user_permission_model.objects.filter(user=self.user):
            output_list += list(self.target_model.objects.filter(pk=perm.item_id, permission_type__in=self.permission_type).values_list('name', flat=True))

        # Get permissions of user groups
        for group in self.user.groups.all():
            for perm in self.group_permission_model.objects.filter(group=group):
                output_list += list(self.target_model.objects.filter(pk=perm.item_id, permission_type__in=self.permission_type).values_list('name', flat=True))

        return list(set(output_list))
