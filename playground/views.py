from django.http import HttpResponse

from playground.decorators import login_required, alogin_required


@login_required
def simple_view(request):
    '''
    Note: This decorated simple_view is not a coroutin function.
    If we run django in async mode, this view will be run in a thread,
    this will decrease the performance. and this is different from
    the original undecorated simple_view.
    '''
    return HttpResponse("Hello, world!")


@alogin_required
def simple_view_2(request):
    '''
    Note: This decorated simple_view is a coroutin function.
    '''
    return HttpResponse("Hello, world!")
