from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import BlogPost, BlogCategory, BlogTag


class BlogListView(ListView):
    """List all published blog posts"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')

        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(meta_keywords__icontains=search_query)
            )

        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Tag filter
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        return queryset.order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        context['popular_tags'] = BlogTag.objects.all()[:10]
        context['featured_posts'] = BlogPost.objects.filter(status='published', is_featured=True)[:3]
        return context


class BlogDetailView(DetailView):
    """Display a single blog post"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags', 'related_products')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Related posts (same category or tags)
        related_posts = BlogPost.objects.filter(
            status='published'
        ).exclude(id=self.object.id).select_related('category')

        if self.object.category:
            related_posts = related_posts.filter(category=self.object.category)
        elif self.object.tags.exists():
            related_posts = related_posts.filter(tags__in=self.object.tags.all()).distinct()

        context['related_posts'] = related_posts[:3]
        context['recent_posts'] = BlogPost.objects.filter(status='published').exclude(id=self.object.id)[:5]

        return context


class BlogCategoryView(ListView):
    """List posts by category"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, slug=self.kwargs['slug'], is_active=True)
        return BlogPost.objects.filter(
            status='published',
            category=self.category
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        context['popular_tags'] = BlogTag.objects.all()[:10]
        return context


class BlogTagView(ListView):
    """List posts by tag"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.tag = get_object_or_404(BlogTag, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            status='published',
            tags=self.tag
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        context['popular_tags'] = BlogTag.objects.all()[:10]
        return context
