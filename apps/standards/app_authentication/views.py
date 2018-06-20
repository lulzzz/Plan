from django.contrib.auth import views as auth_views

from .forms import LoginForm

class LoginView(auth_views.LoginView):
    r"""
    Login page
    """
    template_name = 'architecture/authentication_structure.html'
    authentication_form = LoginForm
    extra_context = {
        'embedded_lib': [
            'jquery',
            'boostrap',
            'font-awesome-google',
            'font-awesome',
            'login',
        ]
    }


class LogoutView(auth_views.LogoutView):
    r'''
    Logout page, which redirects to login
    '''
    pass
