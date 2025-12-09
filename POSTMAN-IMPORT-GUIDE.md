# Postman Collection Import Guide

## Quick Import

1. **Download the collection:**
   - File: `Pharmacy-Microservices.postman_collection.json`
   - Location: Root of repository

2. **Import into Postman:**
   - Open Postman
   - Click **Import** button (top left)
   - Drag and drop the JSON file OR click "Upload Files"
   - Click **Import**

3. **Collection imported!** You should see:
   - ✅ Authentication folder (3 requests)
   - ✅ Products folder (9 requests)
   - ✅ Inventory folder (7 requests)
   - ✅ Orders folder (7 requests)
   - ✅ E2E Flow folder (3 requests for testing Pub/Sub)

## What's Included

### 📋 29 Ready-to-Use API Requests

**Authentication (3 requests):**
- Register User
- Login (auto-saves JWT token)
- Get Current User

**Products (9 requests):**
- Create Product (4 examples: Paracetamol, Amoxicillin, Vitamin C, Ibuprofen)
- Get All Products
- Get Product by ID
- Search Products
- Update Product
- Delete Product

**Inventory (7 requests):**
- Add Inventory (3 examples for different products)
- Get All Inventory
- Get Inventory for Product
- Adjust Inventory
- Get Low Stock Items

**Orders (7 requests):**
- Create Order (triggers Pub/Sub event!)
- Create Order #2
- Get All Orders
- Get Order by ID
- Update Order Status (Processing, Shipped, Delivered)

**E2E Flow - Pub/Sub Testing (3 requests):**
- Check Initial Inventory
- Create Order (publishes Pub/Sub event)
- Verify Inventory Reduced (by Pub/Sub subscriber)

### ⚙️ Pre-Configured Variables

- `base_url`: http://35.223.190.243 (your live deployment)
- `token`: Auto-populated after login
- `order_id`: Auto-saved from order creation
- `product_id_1`: Auto-saved from first product creation
- `initial_quantity`: Used for E2E testing

### 🧪 Built-in Tests

All requests include automated tests:
- Status code validation
- Response structure validation
- Auto-save important values (token, IDs)
- Console logging for debugging

## How to Use

### Step 1: Run in Order (First Time)

Execute requests in this sequence:

1. **Authentication → Register User**
2. **Authentication → Login** (token auto-saved)
3. **Products → Create Product - Paracetamol**
4. **Products → Create Product - Amoxicillin**
5. **Products → Create Product - Vitamin C**
6. **Inventory → Add Inventory - Paracetamol**
7. **Inventory → Add Inventory - Amoxicillin**
8. **Inventory → Add Inventory - Vitamin C**
9. **Orders → Create Order** (Pub/Sub magic happens!)
10. **Inventory → Get Inventory for Product** (verify it reduced!)

### Step 2: Test Event-Driven Architecture

Use the **E2E Flow - Verify Pub/Sub** folder:

1. Click **E2E Flow - Verify Pub/Sub** folder
2. Right-click → **Run folder**
3. Watch the magic:
   - Initial inventory checked
   - Order created (Pub/Sub event published)
   - Inventory automatically reduced
   - Tests verify the reduction!

## For Upwork Portfolio Screenshots

### Screenshot 1: Full Collection View
- Show all folders expanded
- Displays professional organization
- Shows breadth of API coverage

### Screenshot 2: Successful Request/Response
Use: **Orders → Create Order**

**Capture:**
- Request tab showing JSON body
- Authorization tab showing Bearer token
- Response showing 201 Created
- Response body with order details

### Screenshot 3: Automated Tests Passing
Use: **E2E Flow → 3. Verify Inventory Reduced**

**Capture:**
- Tests tab showing green checkmarks
- Console output showing:
  ```
  📦 Initial: 100 → Current: 95
  📉 Reduced by: 5
  ✅ Pub/Sub event-driven architecture working!
  ```

### Screenshot 4: Environment Variables
- Click eye icon (top right)
- Show variables:
  - base_url
  - token (partially visible)
  - order_id
  - product_id_1

## Testing Scenarios

### Scenario 1: Full E2E User Journey
```
1. Register → Login
2. Browse Products (Get All)
3. Create Order
4. Update Order Status (Processing → Shipped → Delivered)
5. Check Order Details
```

### Scenario 2: Inventory Management
```
1. Login
2. Get All Inventory
3. Create Order (reduces stock via Pub/Sub)
4. Manually Adjust Inventory
5. Check Low Stock Items
```

### Scenario 3: Product Catalog Management
```
1. Login
2. Create Product
3. Update Product
4. Search Product
5. Delete Product
```

## Advanced: Collection Runner

**Run all requests automatically:**

1. Click collection name → **Run**
2. Select all folders
3. Click **Run Pharmacy Microservices**
4. Watch automated execution
5. See test results summary

**Perfect for:**
- Demo presentations
- Regression testing
- Portfolio video recording

## Troubleshooting

### Token Expired Error
- Re-run **Authentication → Login**
- Token auto-refreshes in collection

### 404 Not Found
- Ensure service is deployed: http://35.223.190.243/docs
- Check if using correct product/order IDs

### 401 Unauthorized
- Token missing or expired
- Re-run login request

### Pub/Sub Not Working
- Wait 5-10 seconds after creating order
- Check inventory again
- Verify Pub/Sub subscription in GCP Console

## Tips for Upwork Presentation

**Highlight these features in screenshots:**

1. **Professional Organization**
   - Folders grouped by service
   - Descriptive request names
   - Comprehensive coverage

2. **Automation**
   - Token auto-saved
   - Test scripts included
   - Variables auto-populated

3. **Real-World Testing**
   - E2E scenarios
   - Event-driven testing
   - Production API (live URL)

4. **Technical Depth**
   - JWT authentication
   - RESTful design
   - Microservices architecture
   - Event-driven with Pub/Sub

## Collection Features Summary

✅ **29 API requests** covering all endpoints
✅ **Pre-configured** with live URL
✅ **Auto-authentication** (token saved automatically)
✅ **Built-in tests** for validation
✅ **E2E scenarios** for demonstrating Pub/Sub
✅ **Environment variables** for easy customization
✅ **Production-ready** payloads
✅ **Documentation** for each request

---

**Collection File:** `Pharmacy-Microservices.postman_collection.json`
**Live API:** http://35.223.190.243/docs
**GitHub:** https://github.com/saifrehman100/pharmacy-microservices-gcp
