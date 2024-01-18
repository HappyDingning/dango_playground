from asyncio import iscoroutinefunction
from functools import wraps

from django.auth.decorators import _redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME


def user_passes_test(
    test_func, atest_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME
):
    def decorator(view_func):
        if iscoroutinefunction(view_func):
            @wraps(view_func)
            async def _wrapper_view(request, *args, **kwargs):
                if await atest_func(await request.auser()):
                    if iscoroutinefunction(view_func):
                        return await view_func(request, *args, **kwargs)
                    else:
                        return view_func(request, *args, **kwargs)
                return _redirect_to_login(request, login_url, redirect_field_name)

            return _wrapper_view
        else:
            @wraps(view_func)
            def _wrapper_view(request, *args, **kwargs):
                if test_func(request.user):
                    return view_func(request, *args, **kwargs)
                return _redirect_to_login(request, login_url, redirect_field_name)

            return _wrapper_view
    return decorator


def login_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    async def acheck_login(user):
        return user.is_authenticated

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        acheck_login,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def auser_passes_test(
    test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME
):
    """
    Async version of user_passes_test
    """

    def decorator(view_func):
        @wraps(view_func)
        async def _wrapper_view(request, *args, **kwargs):
            if await test_func(await request.auser()):
                # Note: This is the key, the `view_func` can be a coroutine
                # function and it can also be a normal function. The
                # auser_passes_test (or alogin_required) always returns
                # a coroutine function, no matter the `view_func` is a
                # coroutine function or not. So that the decorated
                # `view_func` will not run in a seprate thread.
                if iscoroutinefunction(view_func):
                    return await view_func(request, *args, **kwargs)
                else:
                    return view_func(request, *args, **kwargs)
            return _redirect_to_login(request, login_url, redirect_field_name)

        return _wrapper_view

    return decorator


def alogin_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Async version of login_required
    """

    async def check_login(user):
        return user.is_authenticated

    actual_decorator = auser_passes_test(
        check_login,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
