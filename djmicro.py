import os, sys, types

_base_module = None
_app_name = None

def _extend_opts(initial, to_add):
    if type(to_add) is dict:
        initial.update(to_add)
    elif type(to_add) is types.ModuleType:
        module_opts = {k: v for k, v in to_add.__dict__.iteritems() if not k.startswith('__')}
        initial.update(module_opts)
    elif type(to_add) in (tuple, list):
        for opt_set in to_add:
            _extend_opts(initial, opt_set)
    elif to_add is None:
        pass
    else:
        raise ValueError("Options must be a dict, module, list, tuple, or None.")

def configure(options={}, module=None, app_name=None):
    if not module:
        # hack to figure out where we were called from
        import sys, inspect
        module = sys.modules[inspect.stack()[1][0].f_locals['__name__']]

    # djmicro makes an implicit app that you can install models into, add modules from, etc.
    if not app_name:
        app_name = "djmicro"
    global _app_name
    _app_name = app_name

    if app_name != __name__:
        sys.modules[app_name] = sys.modules[__name__]

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
        _extend_opts(opts, options)

        if 'djmicro' not in opts['INSTALLED_APPS']:
            opts['INSTALLED_APPS'] += (app_name,)

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

def add_module_to_app(module, name=None):
    if name is None:
        name = module.__name__

    # make it available as a module
    sys.modules["%s.%s" % (_app_name, name)] = module
    if _app_name != __name__:
        sys.modules["%s.%s" % (__name__, name)] = module

    # make it available with a from import
    globals()[name] = module

    # if it's a models module, special-case handle it because model detection has already occurred
    if name == "models":
        from django.apps import apps
        new_config = apps.get_app_config(_app_name)
        new_config.import_models(apps.all_models[_app_name])
        apps.app_configs[_app_name] = new_config


def run():
    from django.core.management import execute_from_command_line
    execute_from_command_line()