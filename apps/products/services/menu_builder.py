"""
Menu Builder Service for Advanced Navigation System
Handles server-side menu generation, caching, and optimization
"""

from django.core.cache import cache
from django.db.models import Prefetch, Count, Q
from django.conf import settings
from typing import Dict, List, Optional, Any
import logging

from apps.products.models import (
    MenuCategory, MenuSection, ProductType, Collection, 
    Recipient, DeliveryLocation, Occasion, Product, Category
)

logger = logging.getLogger(__name__)


class MenuBuilderService:
    """
    Service class for building and managing navigation menus
    """
    
    # Cache timeouts (in seconds)
    CACHE_TIMEOUT_MENU = 3600  # 1 hour
    CACHE_TIMEOUT_MOBILE = 1800  # 30 minutes
    CACHE_TIMEOUT_FEATURED = 900  # 15 minutes
    
    # Cache keys
    CACHE_KEY_DESKTOP_MENU = 'menu_builder_desktop_full'
    CACHE_KEY_MOBILE_MENU = 'menu_builder_mobile_full'
    CACHE_KEY_CATEGORY_FEATURED = 'menu_builder_featured_{}'
    
    def __init__(self):
        self.logger = logger
    
    def build_mega_menu(self, force_refresh: bool = False) -> List[Dict]:
        """
        Build complete mega menu structure with caching
        
        Args:
            force_refresh: If True, bypass cache and rebuild menu
            
        Returns:
            List of menu categories with complete structure
        """
        cache_key = self.CACHE_KEY_DESKTOP_MENU
        
        if not force_refresh:
            cached_menu = cache.get(cache_key)
            if cached_menu is not None:
                self.logger.debug("Returning cached desktop menu")
                return cached_menu
        
        try:
            self.logger.info("Building desktop mega menu from database")
            
            # Get main menu categories with optimized queries
            menu_categories = MenuCategory.objects.filter(
                is_active=True,
                show_in_mega_menu=True
            ).prefetch_related(
                'sections',
                'children'
            ).order_by('sort_order')[:10]
            
            menu_data = []
            
            for category in menu_categories:
                category_data = {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'icon': category.icon,
                    'sort_order': category.sort_order,
                    'sections': self.get_menu_sections(category),
                    'featured_products': self.get_featured_products(category, category.featured_products_count)
                }
                menu_data.append(category_data)
            
            # Cache the result
            cache.set(cache_key, menu_data, self.CACHE_TIMEOUT_MENU)
            self.logger.info(f"Cached desktop menu with {len(menu_data)} categories")
            
            return menu_data
            
        except Exception as e:
            self.logger.error(f"Error building mega menu: {str(e)}")
            return []
    
    def build_mobile_menu(self, force_refresh: bool = False) -> List[Dict]:
        """
        Build mobile-optimized menu structure
        
        Args:
            force_refresh: If True, bypass cache and rebuild menu
            
        Returns:
            List of menu categories optimized for mobile
        """
        cache_key = self.CACHE_KEY_MOBILE_MENU
        
        if not force_refresh:
            cached_menu = cache.get(cache_key)
            if cached_menu is not None:
                self.logger.debug("Returning cached mobile menu")
                return cached_menu
        
        try:
            self.logger.info("Building mobile menu from database")
            
            # Get menu categories for mobile
            menu_categories = MenuCategory.objects.filter(
                is_active=True,
                show_in_mobile_menu=True
            ).prefetch_related('sections').order_by('sort_order')[:10]
            
            menu_data = []
            
            for category in menu_categories:
                # Limit items for mobile to improve performance
                sections = self.get_menu_sections(category, mobile_limit=8)
                
                category_data = {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'icon': category.icon,
                    'sort_order': category.sort_order,
                    'sections': sections,
                    'featured_products': self.get_featured_products(category, 3)  # Limit to 3 for mobile
                }
                menu_data.append(category_data)
            
            # Cache the result
            cache.set(cache_key, menu_data, self.CACHE_TIMEOUT_MOBILE)
            self.logger.info(f"Cached mobile menu with {len(menu_data)} categories")
            
            return menu_data
            
        except Exception as e:
            self.logger.error(f"Error building mobile menu: {str(e)}")
            return []
    
    def get_menu_sections(self, category: MenuCategory, mobile_limit: Optional[int] = None) -> List[Dict]:
        """
        Get all sections for a menu category with their items
        
        Args:
            category: MenuCategory instance
            mobile_limit: Limit items per section for mobile (optional)
            
        Returns:
            List of sections with their items
        """
        sections_data = []
        
        try:
            sections = category.sections.filter(is_active=True).order_by('sort_order')
            
            for section in sections:
                section_items = self.get_section_items(section, category, mobile_limit)
                
                if section_items:  # Only include sections with items
                    section_data = {
                        'id': section.id,
                        'name': section.name,
                        'slug': section.slug,
                        'section_type': section.section_type,
                        'sort_order': section.sort_order,
                        'items': section_items
                    }
                    sections_data.append(section_data)
            
            return sections_data
            
        except Exception as e:
            self.logger.error(f"Error getting menu sections for {category.name}: {str(e)}")
            return []
    
    def get_section_items(self, section: MenuSection, category: MenuCategory, limit: Optional[int] = None) -> List[Dict]:
        """
        Get items for a specific menu section
        
        Args:
            section: MenuSection instance
            category: MenuCategory instance
            limit: Maximum number of items to return
            
        Returns:
            List of section items with badges
        """
        items = []
        
        try:
            if section.section_type == 'by_type':
                items = self._get_product_types(category, limit)
            elif section.section_type == 'collection':
                items = self._get_collections(category, limit)
            elif section.section_type == 'for_whom':
                items = self._get_recipients(category, limit)
            elif section.section_type == 'by_occasion':
                items = self._get_occasions(category, limit)
            elif section.section_type == 'deliver_to':
                items = self._get_delivery_locations(category, limit)
            
            return items
            
        except Exception as e:
            self.logger.error(f"Error getting items for section {section.name}: {str(e)}")
            return []
    
    def _get_product_types(self, category: MenuCategory, limit: Optional[int] = None) -> List[Dict]:
        """Get product types for a category"""
        queryset = ProductType.objects.filter(
            slug__startswith=f'{category.slug}-',
            is_active=True
        ).prefetch_related('badges').order_by('sort_order')
        
        if limit:
            queryset = queryset[:limit]
        
        return [
            {
                'id': item.id,
                'name': item.name,
                'slug': item.slug,
                'badges': [
                    {
                        'name': badge.name,
                        'color': badge.color,
                        'background_color': badge.background_color,
                        'css_class': badge.css_class
                    } for badge in item.badges.all()
                ]
            } for item in queryset
        ]
    
    def _get_collections(self, category: MenuCategory, limit: Optional[int] = None) -> List[Dict]:
        """Get collections for a category"""
        queryset = Collection.objects.filter(
            slug__startswith=f'{category.slug}-',
            is_active=True
        ).prefetch_related('badges').order_by('sort_order')
        
        if limit:
            queryset = queryset[:limit]
        
        return [
            {
                'id': item.id,
                'name': item.name,
                'slug': item.slug,
                'is_featured': item.is_featured,
                'badges': [
                    {
                        'name': badge.name,
                        'color': badge.color,
                        'background_color': badge.background_color,
                        'css_class': badge.css_class
                    } for badge in item.badges.all()
                ]
            } for item in queryset
        ]
    
    def _get_recipients(self, category: MenuCategory, limit: Optional[int] = None) -> List[Dict]:
        """Get recipients for a category"""
        queryset = Recipient.objects.filter(
            slug__startswith=f'{category.slug}-',
            is_active=True
        ).order_by('sort_order')
        
        if limit:
            queryset = queryset[:limit]
        
        return [
            {
                'id': item.id,
                'name': item.name,
                'slug': item.slug,
                'category': item.category
            } for item in queryset
        ]
    
    def _get_occasions(self, category: MenuCategory, limit: Optional[int] = None) -> List[Dict]:
        """Get occasions for a category"""
        # Define category-specific occasions
        category_occasions = {
            'flowers': ['Birthday', 'Anniversary', 'Condolence', 'Congratulations', 
                       'Love & Romance', 'Get Well Soon', 'I Am Sorry', 'Thank You', 'New Born'],
            'cakes': ['Anniversary', 'Birthday', 'Appreciation', 'Congratulations',
                     'Get Well Soon', 'I Am Sorry', 'Love & Affection', 'Thank You', 'New Born'],
            'occasions': None  # All occasions for the occasions menu
        }
        
        occasion_names = category_occasions.get(category.slug)
        
        if occasion_names:
            queryset = Occasion.objects.filter(
                name__in=occasion_names,
                is_active=True
            ).order_by('sort_order')
        else:
            queryset = Occasion.objects.filter(
                is_active=True
            ).order_by('sort_order')
        
        if limit:
            queryset = queryset[:limit]
        
        return [
            {
                'id': item.id,
                'name': item.name,
                'slug': item.slug,
                'is_featured': item.is_featured
            } for item in queryset
        ]
    
    def _get_delivery_locations(self, category: MenuCategory, limit: Optional[int] = None) -> List[Dict]:
        """Get delivery locations for a category"""
        queryset = DeliveryLocation.objects.filter(
            slug__startswith=f'{category.slug}-',
            is_active=True
        ).order_by('sort_order')
        
        if limit:
            queryset = queryset[:limit]
        
        return [
            {
                'id': item.id,
                'name': item.name,
                'slug': item.slug,
                'state': item.state,
                'country': item.country,
                'is_major_city': item.is_major_city
            } for item in queryset
        ]
    
    def get_featured_products(self, category: MenuCategory, limit: int = 3) -> List[Dict]:
        """
        Get featured products for a menu category
        
        Args:
            category: MenuCategory instance
            limit: Number of products to return
            
        Returns:
            List of featured products with basic info
        """
        cache_key = self.CACHE_KEY_CATEGORY_FEATURED.format(category.slug)
        
        cached_products = cache.get(cache_key)
        if cached_products is not None:
            return cached_products[:limit]
        
        try:
            # Try to find corresponding old category for products
            old_category = Category.objects.filter(
                slug=category.slug,
                is_active=True
            ).first()
            
            if old_category:
                products = Product.objects.filter(
                    category=old_category,
                    is_featured=True,
                    is_active=True,
                    published=True
                ).select_related('category').prefetch_related(
                    Prefetch('images', queryset=Product.objects.none())  # We'll get primary image separately
                ).order_by('-created_at')[:limit * 2]  # Get more to cache
                
                products_data = []
                for product in products:
                    primary_image = product.primary_image
                    
                    product_data = {
                        'id': product.id,
                        'name': product.name,
                        'slug': product.slug,
                        'current_price': float(product.current_price),
                        'discount_percentage': product.discount_percentage,
                        'image_url': primary_image.get_image_url if primary_image else None,
                        'absolute_url': product.get_absolute_url()
                    }
                    products_data.append(product_data)
                
                # Cache the result
                cache.set(cache_key, products_data, self.CACHE_TIMEOUT_FEATURED)
                return products_data[:limit]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting featured products for {category.name}: {str(e)}")
            return []
    
    def invalidate_cache(self, category_slug: Optional[str] = None):
        """
        Invalidate menu caches
        
        Args:
            category_slug: If provided, only invalidate caches for this category
        """
        if category_slug:
            # Invalidate specific category caches
            cache_key = self.CACHE_KEY_CATEGORY_FEATURED.format(category_slug)
            cache.delete(cache_key)
            self.logger.info(f"Invalidated cache for category: {category_slug}")
        else:
            # Invalidate all menu caches
            cache.delete(self.CACHE_KEY_DESKTOP_MENU)
            cache.delete(self.CACHE_KEY_MOBILE_MENU)
            
            # Invalidate all category featured product caches
            categories = MenuCategory.objects.filter(is_active=True).values_list('slug', flat=True)
            for slug in categories:
                cache_key = self.CACHE_KEY_CATEGORY_FEATURED.format(slug)
                cache.delete(cache_key)
            
            self.logger.info("Invalidated all menu caches")
    
    def get_menu_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the menu system
        
        Returns:
            Dictionary with menu statistics
        """
        try:
            stats = {
                'total_categories': MenuCategory.objects.filter(is_active=True).count(),
                'total_sections': MenuSection.objects.filter(is_active=True).count(),
                'total_product_types': ProductType.objects.filter(is_active=True).count(),
                'total_collections': Collection.objects.filter(is_active=True).count(),
                'total_recipients': Recipient.objects.filter(is_active=True).count(),
                'total_locations': DeliveryLocation.objects.filter(is_active=True).count(),
                'cache_status': {
                    'desktop_menu_cached': cache.get(self.CACHE_KEY_DESKTOP_MENU) is not None,
                    'mobile_menu_cached': cache.get(self.CACHE_KEY_MOBILE_MENU) is not None,
                }
            }
            
            # Add per-category stats
            categories = MenuCategory.objects.filter(is_active=True)
            category_stats = {}
            
            for category in categories:
                category_stats[category.slug] = {
                    'sections_count': category.sections.filter(is_active=True).count(),
                    'featured_products_cached': cache.get(
                        self.CACHE_KEY_CATEGORY_FEATURED.format(category.slug)
                    ) is not None
                }
            
            stats['categories'] = category_stats
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting menu statistics: {str(e)}")
            return {}


# Global instance
menu_builder = MenuBuilderService()