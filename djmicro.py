import os, types

_base_module = None

def configure(options={}, module=None, local_settings=None):
    if not module:
        # hack to figure out where we were called from
        import sys, inspect
        module = sys.modules[inspect.stack()[1][0].f_locals['__name__']]
    
    # settings
    from django.conf import settings
    if not settings.configured:
        opts = dict(
            DEBUG = True,
            ROOT_URLCONF = module.__name__,
            TEMPLATE_DIRS = [os.path.dirname(module.__file__)],
            INSTALLED_APPS = [],
            MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware',)
        )
        opts.update(options)

        if local_settings:
            ls_opts = {k: v for k, v in local_settings.__dict__.iteritems() if not k.startswith('__')}
            opts.update(ls_opts)

        settings.configure(**opts)
    
    # urls
    from django.conf.urls import patterns
    module.urlpatterns = patterns('')

    # wsgi application
    from django.core.wsgi import get_wsgi_application
    module.application = get_wsgi_application()
        
    global _base_module
    _base_module = module

def route(*args, **kwargs):
    def add_route(view):
        # if it's a class-based view, take .as_view() of it
        from django.views.generic import View
        target = view.as_view() if isinstance(view, types.TypeType) and issubclass(view, View) else view

        from django.conf.urls import patterns, url
        _base_module.urlpatterns += patterns('',
            url(args[0], target, *args[1:], **kwargs)
        )
        return view
    return add_route

def run():
    from django.core.management import execute_from_command_line
    execute_from_command_line()