import logging

from django.conf import settings


PLANET_LOGLEVEL = getattr(settings, 'PLANET_LOGLEVEL', logging.DEBUG)
