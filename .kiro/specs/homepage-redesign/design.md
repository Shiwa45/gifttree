# Design Document

## Overview

This design document outlines the implementation of a desktop-optimized homepage redesign featuring four main product category sections: "Send Cakes", "Send Flowers", "Send Plants", and "Send Gifts". The design will replace the current occasion-based circular navigation with a more product-focused approach, using circular product images and clear category labels in a 2x2 grid layout for desktop users.

## Architecture

### Frontend Architecture
- **Template Layer**: Modify existing `templates/core/home.html` to include new category sections
- **Styling Layer**: Add new CSS classes and responsive design rules for desktop category grid
- **JavaScript Layer**: Enhance existing JavaScript for interactive hover effects and navigation
- **Image Management**: Utilize Django's media handling for category images with fallback support

### Backend Integration
- **View Layer**: Extend existing `home_view` in `apps/core/views.py` to provide category-specific product data
- **Model Layer**: Leverage existing Product and Category models with potential new fields for category images
- **URL Routing**: Maintain existing URL structure while adding new category-specific navigation

## Components and Interfaces

### 1. Category Grid Component
```html
<!-- Desktop Category Grid -->
<div class="category-grid-section">
    <div class="category-grid-container">
        <div class="category-item" data-category="cakes">
            <div class="category-images">
                <div class="category-image-circle">
                    <img src="pinata-cake.jpg" alt="Pinata Cakes">
                </div>
                <div class="category-image-circle">
                    <img src="cartoon-cake.jpg" alt="Cartoon Cakes">
                </div>
                <div class="category-image-circle">
                    <img src="pullup-cake.jpg" alt="Pull-up Cakes">
                </div>
            </div>
            <div class="category-content">
                <h3 class="category-title">Send Cakes</h3>
                <div class="category-subtypes">
                    <span>Pinata Cakes</span>
                    <span>Cartoon Cakes</span>
                    <span>Pull-up Cakes</span>
                </div>
            </div>
        </div>
        <!-- Repeat for Flowers, Plants, Gifts -->
    </div>
</div>
```

### 2. CSS Grid System
```css
/* Desktop Category Grid */
@media (min-width: 1024px) {
    .category-grid-section {
        background: white;
        padding: 40px 20px;
        margin: 20px 0;
    }
    
    .category-grid-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        gap: 30px;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .category-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 30px;
        border-radius: 16px;
        background: #fafafa;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
    }
    
    .category-item:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
}
```

### 3. Image Management Interface
```python
# Enhanced view context for category images
def get_category_context(self):
    return {
        'cake_images': [
            {'url': 'cakes/pinata.jpg', 'alt': 'Pinata Cakes', 'label': 'Pinata Cakes'},
            {'url': 'cakes/cartoon.jpg', 'alt': 'Cartoon Cakes', 'label': 'Cartoon Cakes'},
            {'url': 'cakes/pullup.jpg', 'alt': 'Pull-up Cakes', 'label': 'Pull-up Cakes'},
        ],
        'flower_images': [
            {'url': 'flowers/roses.jpg', 'alt': 'Roses', 'label': 'Fresh Roses'},
            {'url': 'flowers/bouquet.jpg', 'alt': 'Bouquets', 'label': 'Bouquets'},
            {'url': 'flowers/arrangements.jpg', 'alt': 'Arrangements', 'label': 'Arrangements'},
        ],
        # Similar for plants and gifts
    }
```

## Data Models

### Enhanced Category Model (Optional Extension)
```python
# Potential model extension for category images
class CategoryImage(models.Model):
    category = models.CharField(max_length=50, choices=[
        ('cakes', 'Cakes'),
        ('flowers', 'Flowers'),
        ('plants', 'Plants'),
        ('gifts', 'Gifts'),
    ])
    image = models.ImageField(upload_to='category_images/')
    alt_text = models.CharField(max_length=100)
    label = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'order']
```

### View Data Structure
```python
# Enhanced context data structure
context = {
    'category_sections': {
        'cakes': {
            'title': 'Send Cakes',
            'url': '/products/?category=cakes',
            'images': cake_images,
            'subtypes': ['Pinata Cakes', 'Cartoon Cakes', 'Pull-up Cakes']
        },
        'flowers': {
            'title': 'Send Flowers',
            'url': '/products/?category=flowers',
            'images': flower_images,
            'subtypes': ['Fresh Roses', 'Bouquets', 'Arrangements']
        },
        # Similar structure for plants and gifts
    }
}
```

## Error Handling

### Image Loading Fallbacks
```css
.category-image-circle img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}

.category-image-circle img[src=""], 
.category-image-circle img:not([src]) {
    background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
    position: relative;
}

.category-image-circle img[src=""]:after,
.category-image-circle img:not([src]):after {
    content: "🎁";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 24px;
}
```

### JavaScript Error Handling
```javascript
// Graceful degradation for category navigation
function navigateToCategory(categoryType) {
    try {
        const categoryUrls = {
            'cakes': '/products/?category=cakes',
            'flowers': '/products/?category=flowers',
            'plants': '/products/?category=plants',
            'gifts': '/products/?category=gifts'
        };
        
        if (categoryUrls[categoryType]) {
            window.location.href = categoryUrls[categoryType];
        } else {
            // Fallback to general products page
            window.location.href = '/products/';
        }
    } catch (error) {
        console.error('Navigation error:', error);
        // Fallback navigation
        window.location.href = '/products/';
    }
}
```

## Testing Strategy

### 1. Visual Regression Testing
- **Desktop Layout Testing**: Verify 2x2 grid layout renders correctly across different desktop resolutions (1024px, 1440px, 1920px)
- **Image Loading Testing**: Test with various image sizes and formats, including missing images
- **Hover Effects Testing**: Validate smooth transitions and visual feedback on category hover

### 2. Responsive Design Testing
- **Mobile Adaptation**: Ensure category sections stack vertically on mobile devices
- **Tablet Layout**: Verify appropriate layout adaptation for tablet screens (768px-1023px)
- **Cross-browser Testing**: Test on Chrome, Firefox, Safari, and Edge

### 3. Performance Testing
- **Image Optimization**: Verify images are properly compressed and optimized for web
- **Loading Speed**: Ensure category section loads within 2 seconds
- **Memory Usage**: Monitor for memory leaks in hover animations

### 4. Accessibility Testing
- **Keyboard Navigation**: Ensure category sections are accessible via keyboard
- **Screen Reader Compatibility**: Verify proper alt text and ARIA labels
- **Color Contrast**: Validate text contrast meets WCAG guidelines

### 5. Integration Testing
- **Category Navigation**: Test links to product category pages work correctly
- **Admin Interface**: Verify category images can be managed through Django admin
- **Fallback Behavior**: Test behavior when images fail to load or categories have no products

### 6. User Experience Testing
- **Click/Touch Targets**: Ensure category sections have appropriate touch targets (minimum 44px)
- **Visual Hierarchy**: Verify category titles and subtypes are clearly readable
- **Loading States**: Test loading indicators and skeleton screens during image loading

## Implementation Phases

### Phase 1: Core Structure
1. Create new CSS classes for desktop category grid
2. Modify home.html template to include category sections
3. Update home_view to provide category-specific data
4. Implement basic responsive design

### Phase 2: Visual Enhancement
1. Add hover effects and animations
2. Implement image optimization and fallbacks
3. Fine-tune spacing and typography
4. Add loading states and transitions

### Phase 3: Mobile Optimization
1. Create mobile-specific layout adaptations
2. Optimize touch interactions
3. Test across various mobile devices
4. Implement progressive enhancement

### Phase 4: Admin Integration
1. Create admin interface for category image management
2. Implement image upload and validation
3. Add category content management features
4. Create documentation for content updates