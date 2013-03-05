# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import DetailView, ListView
from tagging.models import Tag, TaggedItem

from .forms import SearchForm
from .models import Blog, Feed, Author, Post


class AuthorDetail(ListView):
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'planet/authors/detail.html'

    def get_context_data(self, **kwargs):
        context = super(AuthorDetail, self).get_context_data(**kwargs)
        author_pk = self.kwargs['pk']
        context['author'] = get_object_or_404(Author, pk=author_pk)
        tag = self.kwargs.get('tag', None)
        if tag:
            context['tag'] = get_object_or_404(Tag, name=tag)
        return context

    def get_queryset(self):
        author_pk = self.kwargs['pk']
        tag = self.kwargs.get('tag', None)
        if tag:
            tag = get_object_or_404(Tag, name=tag)
            return TaggedItem.objects.get_by_model(Post.site_objects, tag).filter(
                authors__pk=author_pk).order_by("-date_modified")

        else:
            return Post.site_objects.filter(authors__pk=author_pk).order_by('-date_modified')

author_detail = AuthorDetail.as_view()


class AuthorList(ListView):
    model = Author
    context_object_name = 'authors_list'
    paginate_by = 20
    template_name = 'planet/authors/list.html'

    def get_queryset(self):
        return Author.site_objects.all()

authors_list = AuthorList.as_view()


class BlogDetail(ListView):
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'planet/blogs/detail.html'

    def get_context_data(self, **kwargs):
        context = super(BlogDetail, self).get_context_data(**kwargs)
        context['blog'] = get_object_or_404(Blog, pk=self.kwargs['pk'])
        return context

    def get_queryset(self):
        blog_pk = self.kwargs['pk']
        return Post.site_objects.filter(feed__blog__pk=blog_pk).order_by('-date_modified')

blog_detail = BlogDetail.as_view()


class BlogList(ListView):
    model = Blog
    context_object_name = 'blogs_list'
    paginate_by = 10
    template_name = 'planet/blogs/list.html'

    def get_queryset(self):
        return Blog.site_objects.all()

blogs_list = BlogList.as_view()


class FeedDetail(ListView):
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'planet/feeds/detail.html'

    def get_context_data(self, **kwargs):
        context = super(FeedDetail, self).get_context_data(**kwargs)
        feed_pk = self.kwargs['pk']
        context['feed'] = get_object_or_404(Feed, pk=feed_pk)
        tag = self.kwargs.get('tag', None)
        if tag:
            context['tag'] = get_object_or_404(Tag, name=tag)
        return context

    def get_queryset(self):
        feed_pk = self.kwargs['pk']
        tag = self.kwargs.get('tag', None)
        if tag:
            tag = get_object_or_404(Tag, name=tag)
            return TaggedItem.objects.get_by_model(Post.site_objects, tag).filter(
                feed__pk=feed_pk).order_by("-date_modified")

        else:
            return Post.site_objects.filter(feed__pk=feed_pk).order_by('-date_modified')

feed_detail = FeedDetail.as_view()


class FeedList(ListView):
    model = Feed
    context_object_name = 'feeds_list'
    paginate_by = 10
    template_name = 'planet/feeds/list.html'

    def get_queryset(self):
        return Feed.site_objects.all()

feeds_list = FeedList.as_view()


class PostDetail(DetailView):
    model = Post
    template_name = 'planet/posts/detail.html'

post_detail = PostDetail.as_view()


class PostList(ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'planet/posts/list.html'

    def get_queryset(self):
        return Post.site_objects.all().select_related("feed").order_by("-date_modified")

index = PostList.as_view()
posts_list = PostList.as_view()


def tag_detail(request, tag):
    tag = get_object_or_404(Tag, name=tag)

    posts = TaggedItem.objects.get_by_model(
        Post.site_objects, tag).order_by("-date_modified")

    return render_to_response("planet/tags/detail.html", {"posts": posts,
        "tag": tag}, context_instance=RequestContext(request))


def tag_authors_list(request, tag):
    tag = get_object_or_404(Tag, name=tag)

    posts_list = TaggedItem.objects.get_by_model(Post.site_objects, tag)

    authors = set()
    for post in posts_list:
        for author in post.authors.all():
            authors.add(author)

    return render_to_response("planet/authors/list_for_tag.html",
        {"authors": list(authors), "tag": tag},
        context_instance=RequestContext(request))


def tag_feeds_list(request, tag):
    tag = get_object_or_404(Tag, name=tag)

    post_ids = TaggedItem.objects.get_by_model(Post.site_objects, tag
        ).values_list("id", flat=True)

    feeds_list = Feed.site_objects.filter(post__in=post_ids).distinct()

    return render_to_response("planet/feeds/list_for_tag.html",
        {"feeds_list": feeds_list, "tag": tag},
        context_instance=RequestContext(request))


def tags_cloud(request, min_posts_count=1):

    tags_cloud = Tag.objects.cloud_for_model(Post)

    return render_to_response("planet/tags/cloud.html",
        {"tags_cloud": tags_cloud}, context_instance=RequestContext(request))


def foaf(request):
    # TODO: use http://code.google.com/p/django-foaf/ instead of this
    feeds = Feed.site_objects.all().select_related("blog")

    return render_to_response("planet/microformats/foaf.xml", {"feeds": feeds},
        context_instance=RequestContext(request), mimetype="text/xml")


def opml(request):
    feeds = Feed.site_objects.all().select_related("blog")

    return render_to_response("planet/microformats/opml.xml", {"feeds": feeds},
        context_instance=RequestContext(request), mimetype="text/xml")


def search(request):
    if request.method == "GET" and request.GET.get("search") == "go":
        search_form = SearchForm(request.GET)

        if search_form.is_valid():
            query = search_form.cleaned_data["q"]

            if search_form.cleaned_data["w"] == "posts":
                params_dict = {"title__icontains": query}

                posts = Post.site_objects.filter(**params_dict
                    ).distinct().order_by("-date_modified")

                return render_to_response("planet/posts/list.html",
                    {"posts": posts}, context_instance=RequestContext(request))

            elif search_form.cleaned_data["w"] == "tags":
                params_dict = {"name__icontains": query}

                tags_list = Tag.objects.filter(**params_dict
                    ).distinct().order_by("name")

                return render_to_response("planet/tags/list.html",
                    {"tags_list": tags_list},
                    context_instance=RequestContext(request))

            elif search_form.cleaned_data["w"] == "blogs":
                params_dict = {"title__icontains": query}

                blogs_list = Blog.site_objects.filter(**params_dict
                    ).order_by("title")

                return render_to_response("planet/blogs/list.html",
                    {"blogs_list": blogs_list},
                    context_instance=RequestContext(request))

            elif search_form.cleaned_data["w"] == "feeds":
                params_dict = {"title__icontains": query}

                feeds_list = Feed.site_objects.filter(**params_dict
                    ).order_by("title")

                return render_to_response("planet/feeds/list.html",
                    {"feeds_list": feeds_list},
                    context_instance=RequestContext(request))

            elif search_form.cleaned_data["w"] == "authors":
                params_dict = {"name__icontains": query}

                authors_list = Author.site_objects.filter(**params_dict
                    ).order_by("name")

                return render_to_response("planet/authors/list.html",
                    {"authors_list": authors_list},
                    context_instance=RequestContext(request))

            else:
                return HttpResponseRedirect(reverse("planet_post_list"))

        else:
            return HttpResponseRedirect(reverse("planet_post_list"))

    else:
        return HttpResponseRedirect(reverse("planet_post_list"))
