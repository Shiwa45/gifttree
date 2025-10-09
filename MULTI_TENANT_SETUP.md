# Multi-Tenant E-commerce Platform - Setup Guide

## Overview

This Django e-commerce platform has been transformed into a **multi-tenant system** where:
- **Super users** manage product listings
- **Sellers/Vendors** maintain inventory at their locations and fulfill orders
- **Pincode-based availability** checking for products
- **Location-based inventory management**

## Key Features

### 1. Multi-Tenant Seller System
- Sellers can have multiple warehouse/store locations
- Each location can service specific pincodes
- Independent inventory management per location
- Commission-based seller model

### 2. Pincode-Based Availability
- All Indian pincodes database
- Real-time availability checking on product pages
- Automatic stock status based on serviceable locations
- Delivery time estimation per pincode

### 3. Inventory Management
- Product inventory tracked per seller location
- Reserved quantity for pending orders
- Reorder level notifications
- Seller-specific pricing (optional)

## Database Schema

### New Models

#### 1. `Seller` (apps/users/models.py)
Seller/Vendor accounts with business details, bank info, and commission settings.

#### 2. `SellerLocation` (apps/users/models.py)
Physical locations (warehouses/stores) of sellers with serviceable pincode mapping.

#### 3. `Pincode` (apps/users/models.py)
Indian pincode database with delivery settings.

#### 4. `SellerInventory` (apps/products/models.py)
Product inventory at each seller location with stock tracking.

#### 5. Updated `Order` Model
Now includes `assigned_seller` and `assigned_location` fields for order fulfillment.

## Installation & Setup

### Step 1: Run Migrations

```bash
python manage.py migrate users
python manage.py migrate products
python manage.py migrate orders
```

### Step 2: Import Sample Pincodes

To get started with sample pincodes for major Indian cities:

```bash
python manage.py import_pincodes --sample
```

This creates ~60 pincodes covering Delhi, Mumbai, Bangalore, Hyderabad, Chennai, Pune, Kolkata, Ahmedabad, Jaipur, and Chandigarh.

### Step 3: Import Full Pincode Database (Optional)

To import all Indian pincodes from a CSV file:

```bash
python manage.py import_pincodes --file path/to/pincodes.csv
```

**Expected CSV format:**
```csv
pincode,area,district,city,state,delivery_days
110001,Connaught Place,Central Delhi,Delhi,Delhi,1
400001,Fort,Mumbai City,Mumbai,Maharashtra,2
```

### Step 4: Create a Seller Account

1. Create a user account (via Django admin or registration)
2. Go to Django Admin → Users → Sellers → Add Seller
3. Fill in business details:
   - Business name
   - Contact details
   - GST/PAN numbers
   - Bank details
   - Commission percentage

### Step 5: Add Seller Locations

1. In the Seller admin, add locations using the inline form, or
2. Go to Seller Locations → Add Seller Location
3. Provide:
   - Location name (e.g., "Mumbai Warehouse")
   - Address details
   - Contact person
   - Serviceable pincodes (select multiple)

### Step 6: Add Inventory

1. Go to Products → Select a product → Edit
2. Scroll to "Seller Inventory" section (inline form)
3. Add inventory for each seller location:
   - Select seller location
   - Set stock quantity
   - Optionally set seller-specific price
   - Select variant (if applicable)

Or manage inventory separately:
- Go to Seller Inventories → Add Seller Inventory

## Usage

### For Super Users (Product Management)

1. **Create/Import Products** - Use the CSV import feature or add manually
2. **Assign to Sellers** - Create seller inventory records for each location
3. **Monitor Orders** - View which seller is assigned to each order

### For Sellers (Order Fulfillment)

1. **Manage Inventory** - Update stock quantities at your locations
2. **View Assigned Orders** - Filter orders by your seller account
3. **Update Order Status** - Mark orders as processing → ready_to_ship → shipped → delivered

### For Customers (Shopping)

1. **Check Pincode Availability**
   - On product detail pages, enter pincode
   - See if product is available and delivery time
   - View shipping location

2. **Place Orders**
   - Orders automatically assigned to nearest seller with stock
   - Track shipment from seller location

## API Endpoints

### Check Pincode Availability

```
GET /products/api/check-pincode/?pincode=110001&product_id=123&variant_id=456
```

**Response:**
```json
{
  "success": true,
  "available": true,
  "message": "Available! Delivery in 2 days",
  "delivery_days": 2,
  "seller_location": {
    "name": "Delhi Warehouse",
    "city": "Delhi",
    "state": "Delhi"
  },
  "pincode_info": {
    "pincode": "110001",
    "is_serviceable": true
  }
}
```

### Validate Pincode

```
GET /products/api/validate-pincode/?pincode=110001
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "serviceable": true,
  "pincode_data": {
    "pincode": "110001",
    "area": "Connaught Place",
    "city": "Delhi",
    "district": "Central Delhi",
    "state": "Delhi",
    "delivery_days": 1
  },
  "message": "Delhi, Delhi"
}
```

## Admin Panel Features

### Seller Management
- **Sellers Admin** - Manage seller accounts, verification, commission
- **Seller Locations Admin** - Manage warehouses/stores
- **Filter by location** - serviceable pincodes selection

### Inventory Management
- **Seller Inventories Admin** - View all inventory across locations
- **Filter by seller/location** - Quick inventory overview
- **Reorder alerts** - Visual indicators for low stock
- **Bulk edit** - Update stock quantities easily

### Pincode Management
- **Pincodes Admin** - Manage serviceable pincodes
- **Bulk edit** - Update delivery days, serviceable status
- **Filter by state/city** - Easy pincode management

### Order Management
- **Assigned Seller** - See which seller fulfills each order
- **Assigned Location** - Track shipping location
- **Order Status** - Extended statuses (ready_to_ship, out_for_delivery)

## Order Flow

### Traditional Flow
1. Customer places order
2. Admin processes order
3. Ships from central warehouse

### New Multi-Tenant Flow
1. Customer places order with delivery pincode
2. System finds seller location that:
   - Services the pincode
   - Has stock available
3. Order auto-assigned to seller & location
4. Seller receives notification
5. Seller ships from their location
6. Customer tracks from seller location

## Customization

### Adding Custom Delivery Rules

Edit `Product.check_availability_by_pincode()` in `apps/products/models.py`:

```python
def check_availability_by_pincode(self, pincode, variant=None):
    # Add custom logic here
    # Example: Prioritize nearest location, check delivery slots, etc.
    pass
```

### Custom Seller Assignment Logic

Create a service in `apps/orders/services.py`:

```python
def assign_order_to_seller(order, customer_pincode):
    # Find best seller based on:
    # - Stock availability
    # - Distance
    # - Seller rating
    # - Delivery speed
    pass
```

## Best Practices

### 1. Inventory Management
- Set realistic reorder levels
- Update stock regularly
- Use reserved_quantity for pending orders

### 2. Pincode Coverage
- Map all serviceable pincodes to locations
- Update delivery_days based on actual performance
- Mark unserviceable pincodes appropriately

### 3. Seller Onboarding
- Verify business documents
- Test with small inventory first
- Monitor initial orders closely

### 4. Performance
- Use select_related/prefetch_related for queries
- Cache pincode lookups
- Index frequently queried fields

## Troubleshooting

### Product shows "Out of Stock" but has stock
- Check if any seller location has inventory
- Verify seller location services the customer's pincode
- Check `is_active` status on inventory and location

### Pincode check fails
- Ensure pincode exists in database
- Verify pincode is marked as serviceable
- Check seller location has pincode in serviceable_pincodes

### Order not assigned to seller
- Check if pincode is serviceable
- Verify inventory exists for the location
- Check stock_quantity > reserved_quantity

## Data Import

### Bulk Pincode Import

Prepare a CSV with format:
```csv
pincode,area,district,city,state,delivery_days,is_serviceable
110001,Connaught Place,Central Delhi,Delhi,Delhi,1,true
```

Then import:
```bash
python manage.py import_pincodes --file pincodes.csv
```

### Bulk Inventory Upload

Create a management command or use Django admin's CSV import feature with:
- Product SKU
- Seller Location ID
- Stock Quantity
- Variant (optional)

## Next Steps

1. **Seller Dashboard** - Create a frontend for sellers to manage orders
2. **Analytics** - Track seller performance, sales by location
3. **Notifications** - Email/SMS alerts for low stock, new orders
4. **Payment Split** - Auto-calculate seller payments minus commission
5. **Rating System** - Allow customers to rate sellers
6. **Advanced Routing** - AI-based seller assignment for optimal delivery

## Support

For issues or questions:
1. Check Django admin logs
2. Review migration files
3. Check model definitions
4. Verify API endpoints

## License

This multi-tenant system is part of the GiftTree e-commerce platform.
