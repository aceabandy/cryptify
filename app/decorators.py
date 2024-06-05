from django.shortcuts import redirect

def user_not_authenticated(function=None, redirect_to=None):
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_to or 'profile')  # Change 'home' to your desired redirect URL
            return view_func(request, *args, **kwargs)
        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)

