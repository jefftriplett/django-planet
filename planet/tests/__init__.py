"""
Tests for django planet
"""
import os
from django.core.management import call_command
from django.test import TestCase

from planet.models import Post, Feed

import feedparser
original_parse = feedparser.parse


class DjangoPlanetBaseTest(TestCase):
    """
    DjangoPlanetBaseTest base class
    """
    iwatch = 'iwatchnews.rss'
    iwatch_old = 'iwatchnews_old.rss'
    will = 'willmcguagan.rss'
    will_old = 'willmcguagan_old.rss'

    def patch_feedparser(self, rss_name):
        """
        monkey patch feedparser with an rss data file
        """
        def monkey_parse(url_file_stream_or_string, etag=None, modified=None,
                             agent=None, referrer=None, handlers=None,
                             request_headers=None, response_headers=None):
            file = open(os.path.dirname(os.path.abspath(__file__)) + '/data/' +
                        rss_name, 'r')
            rss_content = file.read()
            file.close()
            return original_parse(rss_content, etag, modified, agent, referrer,
                                  handlers, request_headers, response_headers)
        monkey_parse.__name__ = 'parse'

        setattr(feedparser, feedparser.parse.__name__, monkey_parse)


class TestCommands(DjangoPlanetBaseTest):
    def test_update_all_feed(self):
        """
        Test update_all_feeds
        """
        self.patch_feedparser(self.iwatch_old)
        call_command('add_feed', 'http://www.iwatachnews.or/rss/')
        post_count = Post.objects.count()
        feed_count = Feed.objects.count()

        self.assertEqual(post_count, 16)
        self.assertEqual(feed_count, 1)

        self.patch_feedparser(self.iwatch)
        call_command('update_all_feeds')
        post_count = Post.objects.count()
        self.assertEqual(post_count, 18)

    def test_add_feed(self):
        """
        Test add_feed
        """
        self.patch_feedparser(self.iwatch_old)
        call_command('add_feed', 'http://www.iwatachnews.or/rss/')
        post_count = Post.objects.count()
        feed_count = Feed.objects.count()

        self.assertEqual(post_count, 16)
        self.assertEqual(feed_count, 1)
