from django import forms
from django.conf import settings as cp
from password_policies.forms import PasswordPoliciesChangeForm


class PasswordPoliciesChangeCustomizedForm(PasswordPoliciesChangeForm):
    r"""
    Form for customizing the PasswordPoliciesChangeForm
    """

    #: This forms error messages.
    error_messages = dict(PasswordPoliciesChangeForm.error_messages, **{
        'password_lower_upper': 'New password must contain at least {} capital letter and {} lower case letter.'.format(cp.PASSWORD_MIN_LETTERS_UPPER, cp.PASSWORD_MIN_LETTERS_LOWER),
        'password_username': 'New password cannot contain the username.',
    })

    def clean(self):
        cleaned_data = super(PasswordPoliciesChangeForm, self).clean()

        new_password1 = cleaned_data.get("new_password1")
        if new_password1 is None:
            return cleaned_data

        if not (
            sum(1 for c in new_password1 if c.isupper()) >= cp.PASSWORD_MIN_LETTERS_UPPER and
            sum(1 for c in new_password1 if c.islower()) >= cp.PASSWORD_MIN_LETTERS_LOWER
        ):
            raise forms.ValidationError(self.error_messages['password_lower_upper'])

        if (self.user.username.lower() in new_password1.lower()):
            raise forms.ValidationError(self.error_messages['password_username'])

        return cleaned_data
