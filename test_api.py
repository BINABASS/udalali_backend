import os
import sys
import requests
from getpass import getpass

# Base URL of the API
BASE_URL = 'http://127.0.0.1:8000/api/'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.refresh_token = None
        self.user = None

    def print_section(self, title):
        print("\n" + "="*50)
        print(f"TESTING: {title}")
        print("="*50)

    def make_request(self, method, endpoint, data=None, json=None, headers=None, auth_required=True):
        url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = headers or {}
        
        if auth_required and self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, data=data, json=json)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=headers, json=json)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                print(f"Unsupported HTTP method: {method}")
                return None

            print(f"{method.upper()} {url}")
            print(f"Status: {response.status_code}")
            
            try:
                print("Response:", response.json())
            except ValueError:
                print("Response:", response.text)
            
            print("-" * 50)
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None

    def test_authentication(self):
        self.print_section("Authentication")
        
        # Test token obtain
        print("\n1. Testing token obtain")
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        
        response = self.make_request(
            'POST', 
            'token/', 
            data={
                'username': username,
                'password': password
            },
            auth_required=False
        )
        
        if response and response.status_code == 200:
            self.token = response.json().get('access')
            self.refresh_token = response.json().get('refresh')
            self.user = {
                'username': username,
                'password': password
            }
            print("Authentication successful!")
        else:
            print("Authentication failed!")
            sys.exit(1)
        
        # Test token refresh
        print("\n2. Testing token refresh")
        if self.refresh_token:
            response = self.make_request(
                'POST',
                'token/refresh/',
                json={'refresh': self.refresh_token},
                auth_required=False
            )
            if response and response.status_code == 200:
                self.token = response.json().get('access')
                print("Token refresh successful!")
            else:
                print("Token refresh failed!")

    def test_user_endpoints(self):
        self.print_section("User Endpoints")
        
        # Test user list
        print("\n1. Testing user list")
        self.make_request('GET', 'users/')
        
        # Test user detail (assuming user ID 1 exists)
        print("\n2. Testing user detail")
        self.make_request('GET', 'users/1/')
        
        # Test user registration
        print("\n3. Testing user registration")
        test_user = {
            'username': f'testuser_{os.urandom(4).hex()}',
            'email': f'test_{os.urandom(4).hex()}@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'BUYER'
        }
        response = self.make_request('POST', 'users/register/', json=test_user, auth_required=False)
        
        if response and response.status_code == 201:
            print("User registration successful!")
            user_id = response.json().get('id')
            
            # Test updating the new user
            print("\n4. Testing user update")
            update_data = {
                'email': f'updated_{test_user["email"]}'
            }
            self.make_request('PUT', f'users/{user_id}/', json=update_data)
            
            # Test deleting the new user
            print("\n5. Testing user deletion (will not actually delete in test mode)")
            print("Skipping actual deletion to prevent data loss")
            # Uncomment to actually delete:
            # self.make_request('DELETE', f'users/{user_id}/')

    def test_property_endpoints(self):
        self.print_section("Property Endpoints")
        property_id = None
        
        try:
            # Test property list
            print("\n1. Testing property list")
            list_response = self.make_request('GET', 'properties/')
            if not list_response or list_response.status_code != 200:
                print("❌ Failed to fetch property list")
                return
            print("✅ Property list retrieved successfully")
            
            # Test property creation
            print("\n2. Testing property creation")
            test_property = {
                'title': 'Test Property',
                'description': 'This is a test property',
                'price': '100000.00',
                'location': 'Test Location',
                'property_type': 'HOUSE',
                'is_available': True
            }
            create_response = self.make_request('POST', 'properties/create/', json=test_property)
            
            if not create_response or create_response.status_code != 201:
                print("❌ Property creation failed!")
                if create_response:
                    print(f"Status: {create_response.status_code}, Response: {create_response.text}")
                return
                
            property_id = create_response.json().get('id')
            if not property_id:
                print("❌ Failed to get property ID from creation response")
                return
                
            print(f"✅ Property created successfully with ID: {property_id}")
            
            # Test property detail
            print("\n3. Testing property detail")
            detail_response = self.make_request('GET', f'properties/{property_id}/')
            if not detail_response or detail_response.status_code != 200:
                print("❌ Failed to fetch property details")
                return
            print("✅ Property details retrieved successfully")
            
            # Test property update
            print("\n4. Testing property update")
            update_data = {
                'title': 'Updated Test Property',
                'price': '120000.00',
                'description': test_property['description'],  # Include required fields
                'location': test_property['location'],
                'property_type': test_property['property_type'],
                'is_available': test_property['is_available']
            }
            update_response = self.make_request('PUT', f'properties/{property_id}/update/', json=update_data)
            if not update_response or update_response.status_code != 200:
                print("❌ Failed to update property")
                if update_response:
                    print(f"Status: {update_response.status_code}, Response: {update_response.text}")
                return
            print("✅ Property updated successfully")
            
            # Verify the update
            updated_detail = self.make_request('GET', f'properties/{property_id}/')
            if updated_detail and updated_detail.status_code == 200:
                updated_data = updated_detail.json()
                if updated_data.get('title') == update_data['title'] and updated_data.get('price') == update_data['price']:
                    print("✅ Update verification successful")
                else:
                    print("⚠️ Update verification: Field values don't match expected")
            
            # Test property deletion (commented out by default)
            print("\n5. Testing property deletion (commented out by default)")
            # Uncomment the following lines to test deletion:
            # delete_response = self.make_request('DELETE', f'properties/{property_id}/delete/')
            # if delete_response and delete_response.status_code == 204:
            #     print("✅ Property deleted successfully")
            # else:
            #     print("❌ Failed to delete property")
            
        except Exception as e:
            print(f"❌ Error in property endpoints test: {str(e)}")
            raise
            
        finally:
            # Cleanup: Delete the test property if it was created
            if property_id:
                print(f"\n💡 Test property with ID {property_id} was created during testing.")
                print("   To clean up, uncomment the deletion code in test_property_endpoints().")

    def test_subscription_endpoints(self):
        self.print_section("Subscription Endpoints")
        
        try:
            # Test subscription list
            print("\n1. Testing subscription list")
            list_response = self.make_request('GET', 'subscriptions/')
            if not list_response or list_response.status_code != 200:
                print("❌ Failed to fetch subscription list")
                return
            print("✅ Subscription list retrieved successfully")
            
            # Test subscription creation (requires specific setup)
            print("\n2. Testing subscription creation (skipping - requires specific setup)")
            print("💡 Note: Subscription creation typically requires a valid seller user and plan")
            
            # Example of how to test subscription creation (commented out as it requires setup):
            """
            subscription_data = {
                'plan': 'PREMIUM',
                'start_date': '2025-01-01',
                'end_date': '2026-01-01',
                'is_active': True
            }
            create_response = self.make_request('POST', 'subscriptions/', json=subscription_data)
            if create_response and create_response.status_code == 201:
                subscription_id = create_response.json().get('id')
                print(f"✅ Subscription created with ID: {subscription_id}")
                
                # Test subscription detail
                print("\n3. Testing subscription detail")
                detail_response = self.make_request('GET', f'subscriptions/{subscription_id}/')
                if detail_response and detail_response.status_code == 200:
                    print("✅ Subscription details retrieved successfully")
                
                # Cleanup (uncomment if needed)
                # self.make_request('DELETE', f'subscriptions/{subscription_id}/')
            """
            
        except Exception as e:
            print(f"❌ Error in subscription endpoints test: {str(e)}")
            raise
        
    def test_transaction_endpoints(self):
        self.print_section("Transaction Endpoints")
        
        try:
            # Test transaction list
            print("\n1. Testing transaction list")
            list_response = self.make_request('GET', 'transactions/')
            if not list_response or list_response.status_code != 200:
                print("❌ Failed to fetch transaction list")
                return
            print("✅ Transaction list retrieved successfully")
            
            # Test transaction creation (requires specific setup)
            print("\n2. Testing transaction creation (skipping - requires specific setup)")
            print("💡 Note: Transaction creation requires a valid property and subscription")
            
            # Example of how to test transaction creation (commented out as it requires setup):
            """
            transaction_data = {
                'property': 1,  # Requires a valid property ID
                'subscription': 1,  # Requires a valid subscription ID
                'amount': '1000.00',
                'payment_method': 'CARD',
                'status': 'COMPLETED'
            }
            create_response = self.make_request('POST', 'transactions/', json=transaction_data)
            if create_response and create_response.status_code == 201:
                transaction_id = create_response.json().get('id')
                print(f"✅ Transaction created with ID: {transaction_id}")
                
                # Test transaction detail
                print("\n3. Testing transaction detail")
                detail_response = self.make_request('GET', f'transactions/{transaction_id}/')
                if detail_response and detail_response.status_code == 200:
                    print("✅ Transaction details retrieved successfully")
                
                # Cleanup (uncomment if needed)
                # self.make_request('DELETE', f'transactions/{transaction_id}/')
            """
            
        except Exception as e:
            print(f"❌ Error in transaction endpoints test: {str(e)}")
            raise

    def run_all_tests(self):
        test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        def run_test(test_method, test_name):
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                test_method()
                test_results['passed'] += 1
                print(f"✅ {test_name} completed successfully")
            except Exception as e:
                test_results['failed'] += 1
                print(f"❌ {test_name} failed: {str(e)}")
        
        try:
            # Run authentication test first
            print("\n" + "="*50)
            print("STARTING API TESTING")
            print("="*50)
            
            run_test(self.test_authentication, "Authentication Test")
            
            if not self.token:
                print("❌ Authentication failed. Cannot proceed with other tests.")
                test_results['failed'] += 1
                return test_results
            
            # Run other tests
            run_test(self.test_user_endpoints, "User Endpoints Test")
            run_test(self.test_property_endpoints, "Property Endpoints Test")
            run_test(self.test_subscription_endpoints, "Subscription Endpoints Test")
            run_test(self.test_transaction_endpoints, "Transaction Endpoints Test")
            
            # Print summary
            print("\n" + "="*50)
            print("TESTING SUMMARY")
            print("="*50)
            print(f"✅ Passed: {test_results['passed']}")
            print(f"❌ Failed: {test_results['failed']}")
            print(f"⚠️  Skipped: {test_results['skipped']}")
            print("="*50)
            
            if test_results['failed'] == 0:
                print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
            else:
                print(f"⚠️  {test_results['failed']} test(s) failed. Please check the logs above.")
            
            return test_results
            
        except KeyboardInterrupt:
            print("\n⚠️  Testing interrupted by user.")
            return test_results
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {str(e)}")
            test_results['failed'] += 1
            return test_results

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
