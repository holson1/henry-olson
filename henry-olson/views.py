from django.shortcuts import redirect

def home_redirect_view(request):
    """ Temporary view to redirect the user to the /bart app when they hit my site. """

    return redirect('/bart/')