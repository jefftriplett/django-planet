from django.conf import settings
import logging

PLANET_LOGLEVEL = getattr(settings, 'PLANET_LOGLEVEL', logging.DEBUG)


