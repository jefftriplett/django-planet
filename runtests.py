#!/usr/bin/env python

"""
runtests
~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import sys
from os.path import dirname, abspath

from django.core.management import call_command
from django.conf import settings


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                },
            },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.sessions',
            'django.contrib.sites',

            # Included to fix Disqus' test Django which solves IntegrityMessage case
            'django.contrib.contenttypes',

            'planet',
            'django_jenkins',
            'tagging',
        ],
#        ROOT_URLCONF='planet.urls',
        DEBUG=False,
        TEMPLATE_DEBUG=True,
        JENKINS_TASKS=(
            #'django_jenkins.tasks.run_pylint',
#            'django_jenkins.tasks.run_pep8',
#            'django_jenkins.tasks.with_coverage',
            'django_jenkins.tasks.django_tests',
            ),
        SITE_ID=1,
        USER_AGENT='TestBrowser',
    )

def runtests(*test_args):
    from django.test.simple import run_tests

    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:  ## setup.py test
        test_args = ['planet', '--jenkins']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    if '--jenkins' in test_args:
        call_command('jenkins', 'planet', verbosity=1, interactive=True)
        sys.exit(0)
    else:
        failures = run_tests(test_args)
        sys.exit(failures)

if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        argv = ['planet']

    runtests(*argv)
