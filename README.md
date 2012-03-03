# Django as a microframework

I was inspired by [Ivan Sagalaev's micro-Django example](http://softwaremaniacs.org/blog/2011/01/07/django-micro-framework/en/) and wondered if it could be turned into something more easily reusable.  This is a first stab at doing that; the settings bootstrapping and command running is now separated out, and I've borrowed Flask's route decorator pattern to avoid having to explicitly define urlpatterns.

It's pretty hacky at the moment, but I think it could pretty easily get to the point, with the right additional hacks, that models could be used, and apps could be installed (like, for example, the admin).

Look at the example directory to see the original example refactored to use the library.  To run:

    python web.py runserver