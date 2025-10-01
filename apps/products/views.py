from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Min, Max, Prefetch
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Product, Category, Occasion, ProductImage


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        # Optimize queryset with proper prefetching
        queryset = Product.objects.filter(is_active=True).select_related(
            'category'
        ).prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.filter(is_active=True).order_by('sort_order'))
        )
        
        # Apply filters
        queryset = self.apply_filters(queryset)
        
        # Apply sorting
        queryset = self.apply_sorting(queryset)
        
        return queryset

    def apply_filters(self, queryset):
        """Apply various filters to the queryset"""
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            queryset = queryset.filter(category=category)

        # Quick filters
        filter_type = self.request.GET.get('filter')
        if filter_type == 'featured':
            queryset = queryset.filter(is_featured=True)
        elif filter_type == 'bestseller':
            queryset = queryset.filter(is_bestseller=True)
        elif filter_type == 'under_500':
            queryset = queryset.filter(base_price__lt=500)
        elif filter_type == 'same_day':
            # Assuming same day delivery is available for in-stock items
            queryset = queryset.filter(stock_quantity__gt=0)

        # Price range filters
        price_ranges = self.request.GET.getlist('price_range')
        if price_ranges:
            price_q = Q()
            for price_range in price_ranges:
                if price_range == '0-500':
                    price_q |= Q(base_price__lt=500)
                elif price_range == '500-1000':
                    price_q |= Q(base_price__gte=500, base_price__lt=1000)
                elif price_range == '1000-2000':
                    price_q |= Q(base_price__gte=1000, base_price__lt=2000)
                elif price_range == '2000+':
                    price_q |= Q(base_price__gte=2000)
            queryset = queryset.filter(price_q)

        # Category filters
        categories = self.request.GET.getlist('categories')
        if categories:
            queryset = queryset.filter(category__slug__in=categories)

        # Occasion filters
        occasions = self.request.GET.getlist('occasions')
        if occasions:
            queryset = queryset.filter(occasions__slug__in=occasions)

        return queryset

    def apply_sorting(self, queryset):
        """Apply sorting to the queryset"""
        sort_by = self.request.GET.get('sort', 'popularity')
        
        if sort_by == 'price_low':
            return queryset.order_by('base_price')
        elif sort_by == 'price_high':
            return queryset.order_by('-base_price')
        elif sort_by == 'newest':
            return queryset.order_by('-created_at')
        elif sort_by == 'rating':
            # Assuming you have a rating field or related reviews
            return queryset.order_by('-created_at')  # Fallback to newest
        else:  # popularity (default)
            return queryset.order_by('-is_featured', '-is_bestseller', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add category context if filtering by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            try:
                context['category'] = get_object_or_404(Category, slug=category_slug, is_active=True)
                context['page_title'] = context['category'].name
            except:
                context['page_title'] = 'Products'
        else:
            context['page_title'] = 'All Products'

        # Add search query context
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            context['search_query'] = search_query
            context['page_title'] = f'Search Results for "{search_query}"'

        # Add filter context with error handling
        try:
            context['available_categories'] = Category.objects.filter(
                is_active=True,
                products__is_active=True
            ).annotate(product_count_annotation=Count('products')).distinct()
        except:
            context['available_categories'] = Category.objects.none()
        
        try:
            context['available_occasions'] = Occasion.objects.filter(
                is_active=True,
                products__is_active=True
            ).annotate(product_count_annotation=Count('products')).distinct()
        except:
            context['available_occasions'] = Occasion.objects.none()

        # Add product count for better UX
        context['total_products'] = self.get_queryset().count()

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add related products
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(pk=self.object.pk).select_related('category').prefetch_related('images')[:4]
        
        return context


class CategoryDetailView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        queryset = Product.objects.filter(
            category=self.category,
            is_active=True
        ).select_related('category').prefetch_related('images')
        
        # Apply the same filtering and sorting as ProductListView
        view = ProductListView()
        view.request = self.request
        view.kwargs = self.kwargs
        queryset = view.apply_filters(queryset)
        queryset = view.apply_sorting(queryset)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['page_title'] = self.category.name
        
        # Add the same context as ProductListView
        context['available_categories'] = Category.objects.filter(
            is_active=True,
            products__is_active=True
        ).annotate(product_count_annotation=Count('products')).distinct()
        
        context['available_occasions'] = Occasion.objects.filter(
            is_active=True,
            products__is_active=True
        ).annotate(product_count_annotation=Count('products')).distinct()

        return context


def product_search(request):
    """Search products by query with filtering and sorting"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Apply the same filtering and sorting as ProductListView
    view = ProductListView()
    view.request = request
    view.kwargs = {}
    products = view.apply_filters(products)
    products = view.apply_sorting(products)

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add context
    context = {
        'products': page_obj,
        'search_query': query,
        'page_title': f'Search Results for "{query}"' if query else 'Search',
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'available_categories': Category.objects.filter(
            is_active=True,
            products__is_active=True
        ).annotate(product_count_annotation=Count('products')).distinct(),
        'available_occasions': Occasion.objects.filter(
            is_active=True,
            products__is_active=True
        ).annotate(product_count_annotation=Count('products')).distinct(),
    }

    return render(request, 'products/product_list.html', context)


# Add these to existing apps/products/views.py

from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator


def search_suggestions(request):
    """Auto-complete search suggestions via Ajax"""
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'suggestions': []
            })
        
        # Search products
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query),
            is_active=True
        ).select_related('category').prefetch_related('images')[:10]
        
        # Search categories
        categories = Category.objects.filter(
            name__icontains=query,
            is_active=True
        )[:5]
        
        suggestions = {
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'slug': p.slug,
                    'category': p.category.name,
                    'price': float(p.current_price),
                    'image': p.primary_image.image.url if p.primary_image else None
                }
                for p in products
            ],
            'categories': [
                {
                    'id': c.id,
                    'name': c.name,
                    'slug': c.slug
                }
                for c in categories
            ]
        }
        
        return JsonResponse({
            'success': True,
            'query': query,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def quick_view_product(request, product_id):
    """Get product data for quick view modal"""
    try:
        product = get_object_or_404(
            Product.objects.prefetch_related('images', 'variants'),
            id=product_id,
            is_active=True
        )
        
        data = {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'description': product.description,
            'current_price': float(product.current_price),
            'base_price': float(product.base_price),
            'discount_price': float(product.discount_price) if product.discount_price else None,
            'discount_percentage': product.discount_percentage,
            'is_in_stock': product.is_in_stock,
            'stock_quantity': product.stock_quantity,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
                'slug': product.category.slug
            },
            'images': [
                {
                    'id': img.id,
                    'url': img.image.url,
                    'alt_text': img.alt_text,
                    'is_primary': img.is_primary
                }
                for img in product.all_images
            ],
            'variants': [
                {
                    'id': var.id,
                    'name': var.name,
                    'price_adjustment': float(var.price_adjustment),
                    'final_price': float(var.final_price),
                    'stock_quantity': var.stock_quantity
                }
                for var in product.variants.filter(is_active=True)
            ]
        }
        
        return JsonResponse({
            'success': True,
            'product': data
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)