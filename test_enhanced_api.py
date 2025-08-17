#!/usr/bin/env python3
"""
Test script for the enhanced DigiDalali API endpoints.

This script helps test the new seller and buyer functionality in the enhanced API.
It uses the requests library to make HTTP requests to the API.

Usage:
    python test_enhanced_api.py --base-url BASE_URL [--username USERNAME] [--password PASSWORD]
"""

import argparse
import json
import os
import sys
from typing import Dict, Optional, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Default API base URL
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

class APIClient:
    """Client for interacting with the DigiDalali API."""
    
    def __init__(self, base_url: str):
        """Initialize the API client with the base URL."""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Authentication token
        self.token = None
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate and get JWT token."""
        url = f"{self.base_url}/token/"
        data = {"username": username, "password": password}
        
        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            self.token = response.json().get("access")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return True
        except requests.exceptions.RequestException as e:
            print(f"Login failed: {e}")
            return False
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Send a GET request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GET {url} failed: {e}")
            return {}
    
    def post(self, endpoint: str, data: Dict) -> Dict:
        """Send a POST request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"POST {url} failed: {e}")
            return {}
    
    def put(self, endpoint: str, data: Dict) -> Dict:
        """Send a PUT request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"PUT {url} failed: {e}")
            return {}
    
    def delete(self, endpoint: str) -> bool:
        """Send a DELETE request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"DELETE {url} failed: {e}")
            return False

def test_seller_flow(api: APIClient):
    """Test the seller flow (list, create, update, delete properties)."""
    print("\n=== Testing Seller Flow ===")
    
    # 1. List seller's properties
    print("\n1. Listing seller's properties...")
    properties = api.get("properties/my_properties/")
    print(f"Found {len(properties.get('results', []))} properties")
    
    # 2. Create a new property
    print("\n2. Creating a new property...")
    new_property = {
        "title": "Luxury Villa with Ocean View",
        "description": "Beautiful villa with stunning ocean views and modern amenities.",
        "property_type": "HOUSE",
        "price": 350.00,
        "location": "Beach Road, Malindi",
        "bedrooms": 4,
        "bathrooms": 3,
        "is_available": True
    }
    created_property = api.post("properties/", data=new_property)
    if created_property:
        property_id = created_property.get('id')
        print(f"Created property with ID: {property_id}")
        
        # 3. Update the property
        print("\n3. Updating the property...")
        update_data = {"price": 375.00, "description": "Updated description with more details."}
        updated_property = api.put(f"properties/{property_id}/", data=update_data)
        if updated_property:
            print(f"Updated property price to: {updated_property.get('price')}")
        
        # 4. Upload images (placeholder - actual file upload would be handled differently)
        print("\n4. Uploading images (simulated)...")
        # In a real scenario, you would use files parameter with actual image files
        print("Image upload would happen here with actual files")
        
        # 5. Check property availability
        print("\n5. Checking property availability...")
        availability = api.get(f"properties/{property_id}/availability/", 
                             params={"start_date": "2025-09-01", "end_date": "2025-09-07"})
        print(f"Property availability: {availability.get('available', False)}")
        
        # 6. Delete the property (cleanup)
        print("\n6. Cleaning up - deleting the property...")
        if api.delete(f"properties/{property_id}/"):
            print("Property deleted successfully")
    else:
        print("Failed to create property")

def test_buyer_flow(api: APIClient):
    """Test the buyer flow (browse properties, make bookings, send messages)."""
    print("\n=== Testing Buyer Flow ===")
    
    # 1. Browse available properties
    print("\n1. Browsing available properties...")
    properties = api.get("properties/")
    print(f"Found {properties.get('count', 0)} properties")
    
    if properties.get('results'):
        # Get the first property
        property = properties['results'][0]
        property_id = property['id']
        print(f"Viewing property: {property['title']} (ID: {property_id})")
        
        # 2. Check availability
        print("\n2. Checking property availability...")
        availability = api.get(f"properties/{property_id}/availability/", 
                             params={"start_date": "2025-09-15", "end_date": "2025-09-22"})
        print(f"Available: {availability.get('available', False)}")
        
        if availability.get('available'):
            # 3. Create a booking
            print("\n3. Creating a booking...")
            booking_data = {
                "property": property_id,
                "start_date": "2025-09-15",
                "end_date": "2025-09-22",
                "notes": "Interested in booking this property for a family vacation."
            }
            booking = api.post("bookings/", data=booking_data)
            if booking:
                print(f"Booking created with ID: {booking.get('id')}")
                
                # 4. Send a message to the seller
                print("\n4. Sending a message to the seller...")
                message_data = {
                    "recipient": property['seller']['id'],
                    "property": property_id,
                    "subject": f"Question about {property['title']}",
                    "content": "Hello, I have a few questions about this property...",
                    "message_type": "INQUIRY"
                }
                message = api.post("messages/", data=message_data)
                if message:
                    print(f"Message sent with ID: {message.get('id')}")
            else:
                print("Failed to create booking")

def main():
    """Main function to run the API tests."""
    parser = argparse.ArgumentParser(description="Test DigiDalali API endpoints")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, 
                       help=f"Base URL of the API (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--username", help="Username for authentication")
    parser.add_argument("--password", help="Password for authentication")
    args = parser.parse_args()
    
    # Create API client
    api = APIClient(args.base_url)
    
    # Login if credentials provided
    if args.username and args.password:
        print(f"Logging in as {args.username}...")
        if not api.login(args.username, args.password):
            print("Login failed. Exiting.")
            sys.exit(1)
    else:
        print("No credentials provided. Testing public endpoints only.")
    
    # Run tests
    if api.token:
        test_seller_flow(api)
        test_buyer_flow(api)
    else:
        # Test public endpoints only
        print("\nTesting public endpoints...")
        properties = api.get("properties/")
        print(f"Found {properties.get('count', 0)} properties")
        
        if properties.get('results'):
            property_id = properties['results'][0]['id']
            availability = api.get(f"properties/{property_id}/availability/", 
                                 params={"start_date": "2025-09-01", "end_date": "2025-09-07"})
            print(f"Property availability: {availability.get('available', False)}")
    
    print("\nTesting complete!")

if __name__ == "__main__":
    main()
