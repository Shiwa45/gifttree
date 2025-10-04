# Design Document

## Overview

The Advanced Navigation Menu system will transform the current basic category navigation into a comprehensive, multi-layered menu structure similar to MyFlowerTree. The system will provide intuitive product discovery through multiple filtering dimensions while maintaining excellent performance and user experience across all devices.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Desktop Mega Menu  │  Mobile Collapsible  │  Menu Cache    │
│  Component          │  Menu Component      │  Service       │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Backend Layer                            │
├─────────────────────────────────────────────────────────────┤
│  Menu Builder       │  Filter Engine       │  Cache Layer   │
│  Service            │  Service             │  (Redis)       │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
├─────────────────────────────────────────────────────────────┤
│  MenuCategory       │  ProductType         │  Collection    │
│  MenuSection        │  Recipient           │  Location      │
│  MenuBadge          │  Occasion            │  Product       │
└─────────────────────────────────────────────────────────────┘
```

### Component Structure

The system will be built using a modular approach with the following key components:

1. **Menu Data Models** - Extended database models for menu structure
2. **Menu Builder Service** - Server-side menu generation and caching
3. **Frontend Menu Components** - Responsive UI components
4. **Filter Engine** - Dynamic product filtering system
5. **Admin Interface** - Management tools for menu configuration

## Components and Interfaces

### 1. Data Models

#### MenuCategory Model
```python
class MenuCategory(BaseModel):
    name = CharField(max_length=100)
    slug = SlugField(unique=True)
    parent = ForeignKey('self', null=True, blank=True)
    icon = CharField(max_length=50, blank=True)  # Font Awesome icon class
    sort_order = PositiveIntegerField(default=0)
    is_active = BooleanField(default=True)
    show_in_mega_menu = BooleanField(default=True)
    
    # Menu display settings
    menu_columns = PositiveIntegerField(default=4)  # Columns in mega menu
    featured_products_count = PositiveIntegerField(default=3)
```

#### MenuSection Model
```python
class MenuSection(BaseModel):
    category = ForeignKey(MenuCategory, related_name='sections')
    name = CharField(max_length=100)  # "By Type", "Collection", etc.
    slug = SlugField()
    section_type = CharField(max_length=50, choices=SECTION_TYPES)
    sort_order = PositiveIntegerField(default=0)
    is_active = BooleanField(default=True)
```

#### ProductType Model
```python
class ProductType(BaseModel):
    name = CharField(max_length=100)
    slug = SlugField(unique=True)
    category = ForeignKey(Category, related_name='product_types')
    description = TextField(blank=True)
    image = ImageField(upload_to='product_types/', blank=True)
    badges = ManyToManyField('MenuBadge', blank=True)
    sort_order = PositiveIntegerField(default=0)
```

#### Collection Model
```python
class Collection(BaseModel):
    name = CharField(max_length=100)
    slug = SlugField(unique=True)
    description = TextField(blank=True)
    image = ImageField(upload_to='collections/', blank=True)
    categories = ManyToManyField(Category, related_name='collections')
    badges = ManyToManyField('MenuBadge', blank=True)
    is_featured = BooleanField(default=False)
    sort_order = PositiveIntegerField(default=0)
```

#### Recipient Model
```python
class Recipient(BaseModel):
    name = CharField(max_length=100)
    slug = SlugField(unique=True)
    category = CharField(max_length=50, choices=RECIPIENT_CATEGORIES)
    # 'personal', 'professional', 'family'
    sort_order = PositiveIntegerField(default=0)
```

#### MenuBadge Model
```python
class MenuBadge(BaseModel):
    name = CharField(max_length=50)  # "New", "Hot Selling", etc.
    color = CharField(max_length=7, default='#FF0000')  # Hex color
    background_color = CharField(max_length=7, default='#FFFFFF')
    css_class = CharField(max_length=50, blank=True)
    sort_order = PositiveIntegerField(default=0)
```

#### DeliveryLocation Model
```python
class DeliveryLocation(BaseModel):
    name = CharField(max_length=100)
    slug = SlugField(unique=True)
    state = CharField(max_length=100)
    is_major_city = BooleanField(default=False)
    sort_order = PositiveIntegerField(default=0)
    is_active = BooleanField(default=True)
```

### 2. Menu Builder Service

#### MenuBuilderService Class
```python
class MenuBuilderService:
    def build_mega_menu(self, category_slug=None):
        """Build complete mega menu structure with caching"""
        
    def get_menu_sections(self, category):
        """Get all sections for a category (By Type, Collection, etc.)"""
        
    def get_section_items(self, section, category):
        """Get items for a specific section"""
        
    def get_featured_products(self, category, limit=3):
        """Get featured products for mega menu display"""
        
    def build_mobile_menu(self):
        """Build mobile-optimized menu structure"""
```

### 3. Filter Engine

#### ProductFilterService Class
```python
class ProductFilterService:
    def filter_by_type(self, queryset, product_type_slug):
        """Filter products by product type"""
        
    def filter_by_collection(self, queryset, collection_slug):
        """Filter products by collection"""
        
    def filter_by_recipient(self, queryset, recipient_slug):
        """Filter products by recipient"""
        
    def filter_by_occasion(self, queryset, occasion_slug):
        """Filter products by occasion"""
        
    def filter_by_location(self, queryset, location_slug):
        """Filter products by delivery location"""
        
    def apply_multiple_filters(self, queryset, filters_dict):
        """Apply multiple filters simultaneously"""
```

### 4. Frontend Components

#### Desktop Mega Menu Component
```html
<!-- Mega Menu Structure -->
<nav class="advanced-mega-menu">
    <ul class="main-categories">
        <li class="category-item" data-category="flowers">
            <a href="/flowers/">Flowers</a>
            <div class="mega-menu-panel">
                <div class="menu-sections">
                    <div class="menu-section by-type">
                        <h6>By Type</h6>
                        <ul class="section-items">
                            <li><a href="/flowers/roses/">Roses</a></li>
                            <li><a href="/flowers/lilies/">Lilies <span class="badge new">New</span></a></li>
                        </ul>
                    </div>
                    <div class="menu-section collections">
                        <h6>Collection</h6>
                        <ul class="section-items">
                            <li><a href="/collections/bestseller/">Bestseller</a></li>
                            <li><a href="/collections/signature/">Signature Boxes <span class="badge hot">Hot</span></a></li>
                        </ul>
                    </div>
                </div>
                <div class="featured-products">
                    <!-- Featured product thumbnails -->
                </div>
            </div>
        </li>
    </ul>
</nav>
```

#### Mobile Menu Component
```html
<!-- Mobile Collapsible Menu -->
<div class="mobile-menu-container">
    <div class="category-accordion">
        <div class="category-header" data-toggle="flowers">
            <span>Flowers</span>
            <i class="fas fa-chevron-down"></i>
        </div>
        <div class="category-content" id="flowers">
            <div class="section-tabs">
                <button class="tab-btn active" data-section="type">By Type</button>
                <button class="tab-btn" data-section="collection">Collection</button>
                <button class="tab-btn" data-section="recipient">For Whom</button>
            </div>
            <div class="section-content">
                <!-- Dynamic content based on selected tab -->
            </div>
        </div>
    </div>
</div>
```

### 5. Admin Interface Components

#### Menu Management Interface
- Category management with drag-and-drop ordering
- Section configuration with type selection
- Badge management with color picker
- Product type assignment interface
- Collection management with product selection
- Bulk operations for menu items

## Data Models

### Extended Product Model Relationships
```python
# Add to existing Product model
class Product(BaseModel):
    # ... existing fields ...
    
    # New relationships for advanced menu
    product_types = ManyToManyField(ProductType, blank=True)
    collections = ManyToManyField(Collection, blank=True)
    recipients = ManyToManyField(Recipient, blank=True)
    delivery_locations = ManyToManyField(DeliveryLocation, blank=True)
    
    # Menu-specific flags
    is_signature = BooleanField(default=False)
    is_premium = BooleanField(default=False)
    is_hot_selling = BooleanField(default=False)
    is_must_try = BooleanField(default=False)
```

### Menu Configuration Model
```python
class MenuConfiguration(BaseModel):
    key = CharField(max_length=100, unique=True)
    value = JSONField()
    description = TextField(blank=True)
    
    # Example configurations:
    # 'mega_menu_columns': 4
    # 'featured_products_per_category': 3
    # 'mobile_menu_animation_speed': 300
```

## Error Handling

### Menu Loading Errors
- **Graceful Degradation**: If mega menu data fails to load, fall back to basic category menu
- **Cache Fallback**: Use stale cache data if fresh data is unavailable
- **Progressive Loading**: Load menu sections incrementally to prevent blocking

### Filter Errors
- **Invalid Filter Handling**: Ignore invalid filter parameters and show all products
- **Empty Result Sets**: Display "No products found" with suggestions for alternative filters
- **Performance Timeouts**: Implement query timeouts and fallback to cached results

### Mobile Menu Errors
- **Touch Event Failures**: Provide click alternatives for all touch interactions
- **Animation Failures**: Ensure menu functionality works even if CSS animations fail
- **Viewport Issues**: Handle various screen sizes and orientations gracefully

## Testing Strategy

### Unit Tests
1. **Model Tests**
   - Menu category hierarchy validation
   - Product type and collection relationships
   - Badge assignment and display logic
   - Filter query generation

2. **Service Tests**
   - Menu builder service functionality
   - Filter engine accuracy
   - Cache invalidation logic
   - Performance benchmarks

### Integration Tests
1. **Menu Rendering Tests**
   - Desktop mega menu display
   - Mobile menu functionality
   - Cross-browser compatibility
   - Responsive behavior

2. **Filter Integration Tests**
   - Multiple filter combinations
   - URL parameter handling
   - Search result accuracy
   - Performance under load

### User Experience Tests
1. **Usability Testing**
   - Menu navigation flow
   - Filter discovery and usage
   - Mobile touch interactions
   - Accessibility compliance

2. **Performance Testing**
   - Menu loading times
   - Filter response times
   - Cache effectiveness
   - Database query optimization

### Admin Interface Tests
1. **Management Tests**
   - Menu configuration changes
   - Bulk operations
   - Data validation
   - Permission handling

## Performance Considerations

### Caching Strategy
- **Menu Structure Cache**: Cache complete menu structure for 1 hour
- **Filter Results Cache**: Cache popular filter combinations for 30 minutes
- **Featured Products Cache**: Cache featured product data for 15 minutes
- **Mobile Menu Cache**: Separate cache for mobile-optimized menu structure

### Database Optimization
- **Indexing**: Add indexes on frequently filtered fields (product_type, collection, recipient)
- **Query Optimization**: Use select_related and prefetch_related for menu queries
- **Denormalization**: Consider denormalizing frequently accessed menu data

### Frontend Optimization
- **Lazy Loading**: Load mega menu content on hover/interaction
- **Image Optimization**: Optimize featured product images for menu display
- **CSS/JS Minification**: Minimize menu-related assets
- **Progressive Enhancement**: Ensure basic functionality without JavaScript

## Security Considerations

### Input Validation
- Validate all filter parameters to prevent SQL injection
- Sanitize menu configuration inputs in admin interface
- Implement rate limiting for menu API endpoints

### Access Control
- Restrict menu management to authorized admin users
- Implement proper permissions for menu configuration changes
- Log all menu-related administrative actions

### Data Protection
- Ensure menu data doesn't expose sensitive product information
- Implement proper error messages that don't reveal system details
- Use HTTPS for all menu-related API calls