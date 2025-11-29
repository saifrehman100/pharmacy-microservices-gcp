"""
Seed script to populate the databases with sample data.

This script creates sample products and inventory records for testing and demo purposes.
"""
import requests
import json
from typing import Dict, Any

# API Gateway URL (change based on your environment)
API_GATEWAY_URL = "http://localhost:8000"
PRODUCT_SERVICE_URL = "http://localhost:8001"
INVENTORY_SERVICE_URL = "http://localhost:8003"


def register_user() -> Dict[str, Any]:
    """Register a test user and get JWT token."""
    print("Registering test user...")

    # Register user
    response = requests.post(
        f"{API_GATEWAY_URL}/auth/register",
        json={
            "email": "admin@pharmacy.com",
            "username": "admin",
            "password": "admin123456",
            "full_name": "Admin User"
        }
    )

    if response.status_code == 201:
        print("  User registered successfully")
    elif response.status_code == 400:
        print("  User already exists, attempting login...")
    else:
        print(f"  Error: {response.status_code} - {response.text}")
        return None

    # Login to get token
    response = requests.post(
        f"{API_GATEWAY_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123456"
        }
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        print("  Login successful")
        return {"Authorization": f"Bearer {token}"}
    else:
        print(f"  Login failed: {response.status_code}")
        return None


def create_products(headers: Dict[str, str]) -> list:
    """Create sample pharmacy products."""
    print("\nCreating sample products...")

    products = [
        {
            "name": "Aspirin 100mg",
            "description": "Pain reliever and fever reducer",
            "price": 9.99,
            "category": "Pain Relief",
            "requires_prescription": False,
            "manufacturer": "Bayer",
            "stock_keeping_unit": "ASP-100-BTL-100"
        },
        {
            "name": "Ibuprofen 200mg",
            "description": "Anti-inflammatory pain reliever",
            "price": 12.99,
            "category": "Pain Relief",
            "requires_prescription": False,
            "manufacturer": "Advil",
            "stock_keeping_unit": "IBU-200-BTL-100"
        },
        {
            "name": "Amoxicillin 500mg",
            "description": "Antibiotic for bacterial infections",
            "price": 24.99,
            "category": "Antibiotics",
            "requires_prescription": True,
            "manufacturer": "GSK",
            "stock_keeping_unit": "AMX-500-CAP-30"
        },
        {
            "name": "Lisinopril 10mg",
            "description": "Blood pressure medication",
            "price": 15.99,
            "category": "Cardiovascular",
            "requires_prescription": True,
            "manufacturer": "Merck",
            "stock_keeping_unit": "LIS-10-TAB-30"
        },
        {
            "name": "Metformin 500mg",
            "description": "Diabetes medication",
            "price": 19.99,
            "category": "Diabetes",
            "requires_prescription": True,
            "manufacturer": "Teva",
            "stock_keeping_unit": "MET-500-TAB-60"
        },
        {
            "name": "Vitamin D3 1000IU",
            "description": "Vitamin D supplement",
            "price": 14.99,
            "category": "Vitamins",
            "requires_prescription": False,
            "manufacturer": "Nature Made",
            "stock_keeping_unit": "VIT-D3-1000-100"
        },
        {
            "name": "Omeprazole 20mg",
            "description": "Acid reflux medication",
            "price": 18.99,
            "category": "Gastrointestinal",
            "requires_prescription": False,
            "manufacturer": "Prilosec",
            "stock_keeping_unit": "OMP-20-CAP-42"
        },
        {
            "name": "Atorvastatin 20mg",
            "description": "Cholesterol medication",
            "price": 29.99,
            "category": "Cardiovascular",
            "requires_prescription": True,
            "manufacturer": "Lipitor",
            "stock_keeping_unit": "ATO-20-TAB-30"
        },
        {
            "name": "Cetirizine 10mg",
            "description": "Antihistamine for allergies",
            "price": 11.99,
            "category": "Allergy",
            "requires_prescription": False,
            "manufacturer": "Zyrtec",
            "stock_keeping_unit": "CET-10-TAB-70"
        },
        {
            "name": "Insulin Glargine 100U/mL",
            "description": "Long-acting insulin",
            "price": 89.99,
            "category": "Diabetes",
            "requires_prescription": True,
            "manufacturer": "Lantus",
            "stock_keeping_unit": "INS-GLR-100-VL-10"
        }
    ]

    created_products = []

    for product in products:
        # Try via gateway first
        response = requests.post(
            f"{API_GATEWAY_URL}/products",
            json=product,
            headers=headers
        )

        # If gateway fails, try direct product service
        if response.status_code != 201:
            response = requests.post(
                f"{PRODUCT_SERVICE_URL}/products",
                json=product
            )

        if response.status_code == 201:
            created = response.json()
            created_products.append(created)
            print(f"  Created: {product['name']} (ID: {created['id']})")
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"  Skipped: {product['name']} (already exists)")
        else:
            print(f"  Error creating {product['name']}: {response.status_code} - {response.text}")

    return created_products


def create_inventory(products: list):
    """Create inventory records for products."""
    print("\nCreating inventory records...")

    for product in products:
        product_id = product['id']

        # Set different stock levels for variety
        import random
        quantity = random.randint(5, 100)

        inventory_data = {
            "product_id": product_id,
            "quantity": quantity,
            "reorder_level": 10
        }

        response = requests.post(
            f"{INVENTORY_SERVICE_URL}/inventory",
            json=inventory_data
        )

        if response.status_code == 201:
            print(f"  Created inventory for product {product_id}: {quantity} units")
        elif response.status_code == 400:
            print(f"  Inventory already exists for product {product_id}")
        else:
            print(f"  Error creating inventory for product {product_id}: {response.status_code}")


def main():
    """Main seeding function."""
    print("=" * 60)
    print("Pharmacy Microservices - Database Seeding Script")
    print("=" * 60)

    # Register user and get token
    headers = register_user()

    # Create products (with or without authentication)
    if headers:
        products = create_products(headers)
    else:
        print("\nAttempting to create products without authentication...")
        products = create_products({})

    # Create inventory
    if products:
        create_inventory(products)
    else:
        print("\nNo products were created, skipping inventory creation")

    print("\n" + "=" * 60)
    print("Seeding completed!")
    print("=" * 60)
    print("\nTest User Credentials:")
    print("  Username: admin")
    print("  Password: admin123456")
    print("\nYou can now test the API at:")
    print(f"  API Gateway: {API_GATEWAY_URL}")
    print(f"  API Docs: {API_GATEWAY_URL}/docs")


if __name__ == "__main__":
    main()
