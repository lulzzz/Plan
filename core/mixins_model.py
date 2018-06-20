from django.db.models.fields import FieldDoesNotExist

class ModelFormFieldNames():
    r"""
    Provide the selected form fields and verbose names
    """

    def get_form_field_names_tuple(self):
        return tuple(self.form_field_list)

    def get_form_field_names_list(self):
        return self.form_field_list

    def get_form_field_names_verbose_list(self):
        verbose_list = list()
        for field in self.form_field_list:
            try:
                verbose_list.append(self._meta.get_field(field).verbose_name)
            except FieldDoesNotExist:
                verbose_list.append(field)
        return verbose_list
