# 📦 Bulk Product Upload Guide

Complete guide to uploading products in bulk using CSV or Excel files.

---

## 🚀 Quick Start

1. **Access the Upload Page**
   - Log in to Django Admin: `https://mygiftstree.com/admin/`
   - Click on **"Import CSV"** or navigate to: `https://mygiftstree.com/admin/import-csv/`

2. **Download Template**
   - Click on **"Download GiftTree Template (CSV)"** for standard format
   - Or **"Download Shopify Template (CSV)"** if migrating from Shopify
   - Excel templates also available (.xlsx)

3. **Fill Your Data**
   - Open the template in Excel, Google Sheets, or any spreadsheet application
   - Add your product information
   - Follow the column headers and example rows

4. **Upload**
   - Save as CSV or Excel (.xlsx)
   - Drag & drop the file or click to browse
   - Click **"Upload & Import"**

5. **Review Results**
   - Check the import log for success/errors
   - Review newly created products in admin

---

## 📋 GiftTree Format Fields

### Required Fields ✅
| Field | Description | Example |
|-------|-------------|---------|
| **SKU** | Unique product identifier | `GIFT-001` |
| **Name** | Product name | `Chocolate Gift Box` |
| **Category** | Product category (will be created if doesn't exist) | `Chocolates` |
| **Base Price** | Main selling price | `999.00` |
| **Description** | Product description | `Delicious assorted chocolates...` |

### Optional Fields 📝
| Field | Description | Example |
|-------|-------------|---------|
| Sale Price | Discounted price | `899.00` |
| Discount Price | Final discounted price | `799.00` |
| MRP | Maximum Retail Price | `1099.00` |
| Stock Quantity | Available inventory | `50` |
| Weight | Product weight in kg | `0.5` |
| Size | Product size | `Medium` |
| Color | Product color | `Brown` |
| Brand | Brand name | `Sweet Delights` |
| Vendor | Vendor/Supplier name | `Gift Vendor` |
| Tags | Comma-separated tags | `chocolate,gift,premium` |
| Is Featured | Mark as featured (TRUE/FALSE) | `TRUE` |
| Is Bestseller | Mark as bestseller (TRUE/FALSE) | `TRUE` |
| Is Active | Enable/disable product (TRUE/FALSE) | `TRUE` |
| Meta Title | SEO title | `Premium Chocolate Gift Box` |
| Meta Description | SEO description | `Buy premium chocolate gift box...` |
| Image1, Image2, Image3 | Product image URLs | `https://example.com/image.jpg` |

---

## 🛍️ Shopify Format Fields

If you're migrating from Shopify, use this format:

### Main Fields
| Field | Description | Example |
|-------|-------------|---------|
| Handle | URL-friendly identifier | `chocolate-gift-box` |
| Title | Product name | `Chocolate Gift Box` |
| Body (HTML) | Product description (HTML) | `<p>Delicious chocolates</p>` |
| Vendor | Vendor name | `Sweet Delights` |
| Product Category | Category | `Gifts` |
| Type | Product type | `Chocolates` |
| Tags | Comma-separated tags | `chocolate, gift, premium` |
| Published | Visibility (TRUE/FALSE) | `TRUE` |
| Status | Product status | `active` |

### Variant Fields
| Field | Description | Example |
|-------|-------------|---------|
| Option1 Name | First variant option name | `Size` |
| Option1 Value | First variant option value | `Medium` |
| Variant SKU | Variant SKU | `CHO-001-M` |
| Variant Price | Variant price | `899.00` |
| Variant Compare At Price | Original price | `1099.00` |
| Variant Inventory Qty | Stock quantity | `50` |
| Variant Weight | Weight | `0.5` |
| Variant Weight Unit | Weight unit | `kg` |
| Variant Taxable | Tax applicable (TRUE/FALSE) | `TRUE` |

### SEO & Images
| Field | Description | Example |
|-------|-------------|---------|
| SEO Title | SEO title | `Premium Chocolate Gift Box` |
| SEO Description | SEO description | `Buy premium chocolate gift box` |
| Image Src | Image URL | `https://example.com/image.jpg` |
| Image Position | Image order | `1` |

---

## 💡 Tips & Best Practices

### 1. **SKU Management**
   - Use unique SKUs for each product
   - Format: `CATEGORY-NUMBER` (e.g., `CHOC-001`, `FLOW-002`)
   - Keep SKUs consistent and easy to track

### 2. **Pricing Strategy**
   - Always include Base Price
   - Use Sale Price for discounts
   - MRP helps calculate discount percentage
   - Format: Use decimal numbers like `999.00` (no currency symbols)

### 3. **Categories**
   - Categories are auto-created if they don't exist
   - Use consistent naming (e.g., "Chocolates" not "Chocolate" or "Chocolates Gift")
   - Parent categories can be assigned later in admin

### 4. **Images**
   - Use direct image URLs (publicly accessible)
   - Recommended size: 800x800px or larger
   - Formats: JPG, PNG, WebP
   - Multiple images: Use Image1, Image2, Image3 columns

### 5. **Boolean Fields**
   - Use `TRUE` or `FALSE` (case-insensitive)
   - Also accepts: `1`/`0`, `yes`/`no`, `y`/`n`

### 6. **Tags**
   - Separate tags with commas
   - Example: `chocolate,gift,premium,birthday`
   - Tags help with search and filtering

### 7. **Descriptions**
   - Keep descriptions clear and concise
   - Include key features and benefits
   - Use plain text for GiftTree format
   - Use HTML for Shopify format

---

## 🔧 File Format Requirements

### CSV Files
- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Max Size**: 10MB
- **Extension**: `.csv`

### Excel Files
- **Format**: Excel 2007+ (.xlsx)
- **Max Size**: 10MB
- **Sheets**: Only first sheet is processed
- **Extension**: `.xlsx` or `.xls`

---

## 📊 Example Products

### Example 1: Simple Product
```csv
SKU,Name,Description,Category,Base Price,Stock Quantity,Is Active
GIFT-001,Chocolate Gift Box,Delicious assorted chocolates,Chocolates,999.00,50,TRUE
```

### Example 2: Complete Product with All Fields
```csv
SKU,Name,Description,Category,Base Price,Sale Price,Discount Price,MRP,Stock Quantity,Weight,Size,Color,Brand,Vendor,Tags,Is Featured,Is Bestseller,Is Active,Meta Title,Meta Description,Image1
GIFT-002,Red Roses Bouquet,Beautiful bouquet of 12 fresh red roses,Flowers,599.00,549.00,499.00,699.00,100,0.3,Standard,Red,Fresh Flowers Co,Flower Vendor,"roses,flowers,romantic,gift",TRUE,FALSE,TRUE,12 Red Roses Bouquet - Express Your Love,Fresh red roses bouquet perfect for expressing love,https://example.com/roses.jpg
```

---

## 🐛 Troubleshooting

### Common Errors

**1. "SKU already exists"**
- Solution: Use unique SKUs or the system will update existing products

**2. "Invalid price format"**
- Solution: Use decimal numbers without currency symbols (e.g., `999.00` not `$999`)

**3. "Category not found"**
- Solution: Categories are auto-created, check spelling consistency

**4. "File too large"**
- Solution: Split large files into smaller batches (max 10MB per file)

**5. "Invalid file format"**
- Solution: Save as CSV or XLSX format only

**6. "Image URL not accessible"**
- Solution: Ensure image URLs are publicly accessible (not behind login)

---

## 📈 Performance Tips

### For Large Imports (1000+ products)

1. **Split into batches**
   - Upload 500-1000 products at a time
   - This prevents timeout issues

2. **Test first**
   - Upload 5-10 products as a test
   - Verify data format is correct
   - Then proceed with full import

3. **Image handling**
   - Upload images separately first (to cloud storage)
   - Then add image URLs in CSV
   - Or upload products first, add images later

4. **Monitor import logs**
   - Check recent imports section for errors
   - Fix errors in next batch

---

## 🔄 Update Existing Products

The system automatically:
- **Creates** new products if SKU doesn't exist
- **Updates** existing products if SKU matches

To update products:
1. Export existing products (optional, for backup)
2. Modify the CSV with updated data
3. Keep the same SKUs
4. Upload the file
5. System will update matching products

---

## 🎯 Next Steps After Import

1. **Review Products**
   - Go to Products in admin
   - Check prices, descriptions, images

2. **Organize Categories**
   - Set parent categories if needed
   - Add category images and descriptions

3. **Configure Variants**
   - Add product variants (size, color, etc.) in admin
   - Or include in CSV with Shopify format

4. **Add Relationships**
   - Assign to Collections
   - Tag for Recipients
   - Set Occasions

5. **Test on Frontend**
   - Visit your website
   - Check product display
   - Test add to cart

---

## 📞 Support

If you encounter issues:
1. Check import logs for detailed error messages
2. Review this guide for common solutions
3. Ensure CSV format matches template exactly
4. Try with a smaller test file first

---

## 📚 Additional Resources

- **Admin Panel**: `/admin/`
- **Bulk Upload**: `/admin/import-csv/`
- **Product Management**: `/admin/products/product/`
- **Import Logs**: `/admin/products/csvimportlog/`

---

**Version**: 1.0  
**Last Updated**: October 2025  
**System**: GiftTree E-commerce Platform

