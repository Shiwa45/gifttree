# Phase 1: Immediate Fixes & Quick Updates
**Timeline:** Day 1-2  
**Priority:** 🔴 CRITICAL

---

## 📋 Overview
This phase focuses on quick wins that can be implemented immediately with minimal risk. These are content updates and simple model changes that don't require complex logic.

---

## ✅ Tasks Breakdown

### Task 1.1: Update Site Settings Model
**Requirement:** #2, #10, #11, #17, #21  
**Files to Modify:**
- `apps/core/models.py`
- `apps/core/admin.py` (if needed for display)

**Changes Required:**

1. **Update SiteSettings Model** (`apps/core/models.py`):
   ```python
   # Update these fields with new defaults:
   - site_name: "MyGiftTree" (from "GiftTree")
   - contact_phone: "+91-9351221905" (from "+91-9876543210")
   - contact_email: "support@mygifttree.com" (from "info@gifttree.com")
   - copyright_text: "© 2014-2025 MyGiftTree. All rights reserved." (NEW FIELD)
   
   # Add new fields:
   - facebook_url: URLField (blank=True)
   - instagram_url: URLField (blank=True)
   - twitter_url: URLField (blank=True)
   ```

2. **Update Admin Display** (`apps/core/admin.py`):
   - Add new fields to fieldsets
   - Group social media fields together

**Expected Output:**
- Model updated with new fields
- Default values changed
- Admin panel shows new fields for editing

---

### Task 1.2: Logo Update
**Requirement:** #2  
**Files to Create/Modify:**
- `static/images/logo.png` (upload new logo)
- `templates/base.html`
- `templates/includes/desktop_header.html`
- `templates/includes/mobile_header.html`

**Changes Required:**

1. **Create logo directory** (if not exists):
   ```
   static/images/logo.png
   ```

2. **Update logo references** in all header templates:
   ```html
   <!-- Old -->
   <h2><a href="{% url 'core:home' %}">GiftTree</a></h2>
   
   <!-- New -->
   <a href="{% url 'core:home' %}" class="logo-link">
       <img src="{% static 'images/logo.png' %}" alt="MyGiftTree" class="site-logo">
   </a>
   ```

3. **Add logo CSS** to make it responsive:
   ```css
   .site-logo {
       height: 50px;
       width: auto;
   }
   
   @media (max-width: 768px) {
       .site-logo {
           height: 40px;
       }
   }
   ```

**Expected Output:**
- Logo displays on all pages (desktop & mobile)
- Logo is properly sized and responsive
- Logo links to homepage

---

### Task 1.3: Update Contact Information in Templates
**Requirement:** #10, #11  
**Files to Modify:**
- `templates/includes/desktop_header.html`
- `templates/includes/mobile_header.html`
- `templates/base.html` (if footer is there)

**Changes Required:**

1. **Desktop Header** - Update top bar:
   ```html
   <!-- Find and replace -->
   Old: +91-9876543210
   New: +91-9351221905
   
   Old: support@gifttree.com
   New: support@mygifttree.com
   ```

2. **If contact info is hardcoded**, replace with dynamic:
   ```html
   <!-- Before -->
   <span><i class="fas fa-phone"></i> Call: +91-9876543210</span>
   
   <!-- After -->
   <span><i class="fas fa-phone"></i> Call: {{ site_settings.contact_phone }}</span>
   ```

**Expected Output:**
- New phone number displays everywhere
- New email displays everywhere
- Uses dynamic site_settings variable

---

### Task 1.4: Remove MFT Category Names
**Requirement:** #1  
**Method:** Django Admin or Management Command

**Option A - Via Django Admin:**
1. Go to: `http://localhost:8000/admin/products/category/`
2. Search for categories containing "MFT"
3. Manually edit each category name to remove "MFT"
4. Save changes

**Option B - Management Command (Recommended):**

Create: `apps/core/management/commands/remove_mft_names.py`

```python
from django.core.management.base import BaseCommand
from apps.products.models import Category

class Command(BaseCommand):
    help = 'Remove MFT prefix from category names'

    def handle(self, *args, **options):
        categories = Category.objects.filter(name__icontains='MFT')
        
        count = 0
        for category in categories:
            old_name = category.name
            new_name = category.name.replace('MFT', '').replace('mft', '').strip()
            
            if old_name != new_name:
                category.name = new_name
                category.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated: "{old_name}" → "{new_name}"')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {count} categories')
        )
```

Run command:
```bash
python manage.py remove_mft_names
```

**Expected Output:**
- All category names cleaned (no "MFT" prefix)
- Navigation displays clean category names
- No data loss

---

### Task 1.5: Add Social Media Links to Footer
**Requirement:** #21  
**Files to Modify/Create:**
- `templates/base.html` (if footer is here)
- OR create `templates/includes/footer.html` (NEW)

**Changes Required:**

1. **Create/Update Footer Template**:

If footer doesn't exist, create `templates/includes/footer.html`:

```html
<footer class="site-footer">
    <div class="container">
        <div class="footer-content">
            <!-- Company Info -->
            <div class="footer-section">
                <h4>{{ site_settings.site_name }}</h4>
                <p>Send beautiful flowers, delicious cakes and amazing gifts online.</p>
                
                <!-- Social Media Links -->
                <div class="social-links">
                    {% if site_settings.facebook_url %}
                    <a href="{{ site_settings.facebook_url }}" target="_blank" rel="noopener" aria-label="Facebook">
                        <i class="fab fa-facebook"></i>
                    </a>
                    {% endif %}
                    
                    {% if site_settings.instagram_url %}
                    <a href="{{ site_settings.instagram_url }}" target="_blank" rel="noopener" aria-label="Instagram">
                        <i class="fab fa-instagram"></i>
                    </a>
                    {% endif %}
                    
                    {% if site_settings.twitter_url %}
                    <a href="{{ site_settings.twitter_url }}" target="_blank" rel="noopener" aria-label="Twitter">
                        <i class="fab fa-twitter"></i>
                    </a>
                    {% endif %}
                </div>
            </div>
            
            <!-- Contact Info -->
            <div class="footer-section">
                <h4>Contact Us</h4>
                <ul class="contact-info">
                    <li>
                        <i class="fas fa-phone"></i>
                        <a href="tel:{{ site_settings.contact_phone }}">{{ site_settings.contact_phone }}</a>
                    </li>
                    <li>
                        <i class="fas fa-envelope"></i>
                        <a href="mailto:{{ site_settings.contact_email }}">{{ site_settings.contact_email }}</a>
                    </li>
                </ul>
            </div>
        </div>
        
        <!-- Copyright -->
        <div class="footer-bottom">
            <p>{{ site_settings.copyright_text }}</p>
        </div>
    </div>
</footer>

<style>
.site-footer {
    background: #2c3e50;
    color: #ecf0f1;
    padding: 40px 0 20px;
    margin-top: 60px;
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
    margin-bottom: 30px;
}

.footer-section h4 {
    color: #fff;
    margin-bottom: 15px;
}

.social-links {
    display: flex;
    gap: 15px;
    margin-top: 15px;
}

.social-links a {
    width: 40px;
    height: 40px;
    background: rgba(255,255,255,0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    transition: all 0.3s;
}

.social-links a:hover {
    background: #E91E63;
    transform: translateY(-3px);
}

.footer-bottom {
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.1);
}

@media (max-width: 768px) {
    .footer-content {
        grid-template-columns: 1fr;
    }
}
</style>
```

2. **Include Footer in Base Template** (`templates/base.html`):
```html
<!-- Before closing </body> tag -->
{% include 'includes/footer.html' %}
```

**Expected Output:**
- Footer displays on all pages
- Social media icons are clickable
- Links open in new tab
- Contact info is dynamic
- Copyright shows correct year range

---

### Task 1.6: Update Context Processor
**Requirement:** All dynamic data  
**File to Verify:**
- `apps/core/context_processors.py`

**Changes Required:**

Ensure `site_settings` is available globally:

```python
from apps.core.models import SiteSettings

def global_context(request):
    """
    Global context processor to provide common data to all templates
    """
    # ... existing code ...
    
    return {
        'main_categories': main_categories,
        'cart_count': cart_count,
        'site_settings': SiteSettings.get_settings(),  # ADD THIS
    }
```

**Expected Output:**
- `{{ site_settings }}` available in all templates
- No need to pass site_settings in every view

---

## 🔄 Migration Steps

After making all model changes:

```bash
# 1. Create migrations
python manage.py makemigrations core

# 2. Check migration file (review it)
# Should see: add fields facebook_url, instagram_url, twitter_url, copyright_text

# 3. Apply migrations
python manage.py migrate

# 4. Run management command (if created)
python manage.py remove_mft_names

# 5. Update site settings via admin
# Go to: http://localhost:8000/admin/core/sitesettings/1/change/
# Update:
#   - Phone: +91-9351221905
#   - Email: support@mygifttree.com
#   - Copyright: © 2014-2025 MyGiftTree. All rights reserved.
#   - Facebook: https://facebook.com/mygifttree
#   - Instagram: https://instagram.com/mygifttree

# 6. Collect static files (for logo)
python manage.py collectstatic --noinput
```

---

## ✅ Testing Checklist

### Desktop Testing:
- [ ] New logo displays in header
- [ ] Logo is properly sized (50px height)
- [ ] Logo links to homepage
- [ ] Phone number shows: +91-9351221905 in header
- [ ] Email shows: support@mygifttree.com in header
- [ ] Social media icons appear in footer
- [ ] Facebook link opens in new tab
- [ ] Instagram link opens in new tab
- [ ] Copyright shows: © 2014-2025 MyGiftTree
- [ ] All category names are clean (no MFT)

### Mobile Testing:
- [ ] Logo displays at 40px height
- [ ] Logo doesn't overflow
- [ ] Contact info is readable
- [ ] Social icons are tappable
- [ ] Footer is responsive

### Admin Testing:
- [ ] Can edit site settings
- [ ] New fields show in admin
- [ ] Changes reflect immediately on frontend

---

## 📊 Success Criteria

Phase 1 is complete when:
1. ✅ Logo displays on all pages (desktop & mobile)
2. ✅ Phone number is +91-9351221905 everywhere
3. ✅ Email is support@mygifttree.com everywhere
4. ✅ Copyright shows © 2014-2025 MyGiftTree
5. ✅ Social media links work in footer
6. ✅ No category names contain "MFT"
7. ✅ No errors in console or terminal
8. ✅ All migrations applied successfully

---

## 🎯 Files Modified Summary

### Python Files:
1. `apps/core/models.py` - SiteSettings model updates
2. `apps/core/context_processors.py` - Add site_settings
3. `apps/core/management/commands/remove_mft_names.py` - NEW

### Template Files:
1. `templates/base.html` - Logo reference, footer include
2. `templates/includes/desktop_header.html` - Logo, contact info
3. `templates/includes/mobile_header.html` - Logo, contact info
4. `templates/includes/footer.html` - NEW (social media, copyright)

### Static Files:
1. `static/images/logo.png` - NEW (upload client's logo)

---

## ⚠️ Important Notes

1. **Backup Database First**: Run `python manage.py dumpdata > backup.json`
2. **Test Logo**: Make sure logo.png is optimized (< 100KB)
3. **Check Migrations**: Review migration file before applying
4. **Clear Cache**: If using cache, clear it after changes
5. **Browser Refresh**: Hard refresh (Ctrl+Shift+R) to see logo changes

---

## 🚀 Next Steps

After Phase 1 completion:
- Commit all changes to git
- Tag release as `v1.1-phase1-complete`
- Move to Phase 2: Bug Fixes

---

**Estimated Time: 4-6 hours**
**Risk Level: LOW** ✅
**Can be done without downtime** ✅