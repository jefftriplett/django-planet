"""
Tests for django planet
"""
import os
from django.core.management import call_command
from django.test import TestCase

from planet.models import Post, Feed


class DjangoPlanet(TestCase):
    """
    DjangoPlanet tests
    """
    def setUp(self):
        """
        setUp function
        """
        self.iwatch = 'iwatchnews.rss'
        self.iwatch_old = 'iwatchnews_old.rss'
        self.will = 'willmcguagan.rss'
        self.will_old = 'willmcguagan_old.rss'

    def test_update_feed(self):
        """
        test add and update feed
        """
        import feedparser
        original_parse = feedparser.parse
        def monkey_parse_old(url_file_stream_or_string, etag=None, modified=None,
                             agent=None, referrer=None, handlers=None,
                             request_headers=None, response_headers=None):
            file = open(os.path.dirname(os.path.abspath(__file__)) + '/' +
                        self.iwatch_old, 'r')
            rss_content = file.read()
            file.close()
            return original_parse(rss_content, etag, modified, agent, referrer,
                                  handlers, request_headers, response_headers)
        monkey_parse_old.__name__ = 'parse'

        def monkey_parse(url_file_stream_or_string, etag=None, modified=None,
                         agent=None, referrer=None, handlers=None,
                         request_headers=None, response_headers=None):
            file = open(os.path.dirname(os.path.abspath(__file__)) + '/' +
                        self.iwatch, 'r')
            rss_content = file.read()
            file.close()
            return original_parse(rss_content, etag, modified, agent, referrer,
                                  handlers, request_headers, response_headers)
        monkey_parse.__name__ = 'parse'

        setattr(feedparser, feedparser.parse.__name__, monkey_parse_old )

        call_command('add_feed', 'http://www.iwatachnews.or/rss/')
        post_count = Post.objects.count()
        feed_count = Feed.objects.count()

        self.assertEqual(post_count, 16)
        self.assertEqual(feed_count, 1)

        setattr(feedparser, feedparser.parse.__name__, monkey_parse )
        call_command('update_all_feeds')
        post_count = Post.objects.count()
        self.assertEqual(post_count, 18)
