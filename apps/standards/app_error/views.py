from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import update_session_auth_hash
from django.conf import settings as cp

from .forms import PasswordPoliciesChangeCustomizedForm


def handler(request, status_code, h2, p):
    status = status_code
    context = {
        'context': {
            'status_code': str(status),
            'h2': h2,
            'p': p,
        },
        'embedded_lib': [
            'jquery',
            'boostrap',
            'font-awesome',
        ]
    }
    return render(request, 'error.html',
        context,
        status=status
    )


def handler400(request):
    return handler(
        request,
        400,
        'Bad request',
        'The request could not be understood by the server due to malformed syntax.'
    )

def handler401(request):
    return handler(
        request,
        401,
        'Your Account was Locked for Security Reasons',
        'Too many failed login attempts. Contact an administrator to unlock your account.'
    )

def handler403(request):
    return handler(
        request,
        403,
        'Access denied',
        'Full authentication is required to access this resource.'
    )

def handler404(request):
    return handler(
        request,
        404,
        'Sorry but we could not find this page',
        'This page you are looking for does not exist.'
    )

def handler500(request):
    return handler(
        request,
        500,
        'Internal Server Error',
        'We track these errors automatically, but if the problem persists feel free to contact us. In the meantime, try refreshing.'
    )


def password_change(request):

    if request.method == "POST":
        form = PasswordPoliciesChangeCustomizedForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update the current session information
            return redirect(cp.LOGIN_REDIRECT_URL)

    else:
        form = PasswordPoliciesChangeCustomizedForm(request.user)

    context = {
        'form': form,
        'context': {},
        'embedded_lib': [
            'jquery',
            'boostrap',
            'font-awesome',
        ]
    }
    return render(request, 'password_change.html', context)
