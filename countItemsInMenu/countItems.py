import sys
from pathlib import Path

# Add project root to Python path (must be before project imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import json
from datetime import datetime
import os
import pandas as pd
from authentication.tokening import getToken, headers


# menu = "682f29eefb114f00960f1bf5" # ASDA MENU
menu = "692477e7636eb3ba51b113b7"
# account = "67e1515214f41141b66ab1ea" #ASDA
account = "68dfac95670f24842ef5b109"
locIdtoCheck = "68e7b012f1151bd7d2e373d4"
channel = -1
# channel = 6007

def getLocationName(location, tags = None):
    try:
        url = f"https://api.deliverect.io/locations/{location}"
        print(f"  [DEBUG] Fetching location name from: {url}")
        response = requests.request("GET", url, headers=headers)
        
        if response.status_code != 200:
            print(f"  [ERROR] Failed to get location: Status {response.status_code}")
            print(f"  [ERROR] Response: {response.text[:200]}")
            return None
        
        data = response.json()
        location_name = data.get("name", "Unknown")
        tags = data.get("tags", [])
        
        print(f"  [DEBUG] Location name: {location_name}, Tags: {tags}")
        
        if tags and tags in [tag.lower() for tag in tags]:
            return location_name
        else:
            return location_name  # Return name anyway for now
    except Exception as e:
        print(f"  [ERROR] Exception in getLocationName: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def isSnoozed(productId, products_dict):
    product = products_dict.get(productId)
    return product and product.get('snoozed', False)

def getPreview(url, location_name):
    try:
        print(f"  [DEBUG] Fetching menu preview from: {url}")
        response = requests.request("GET", url, headers=headers)
        
        if response.status_code != 200:
            print(f"  [ERROR] Failed to get menu preview: Status {response.status_code}")
            print(f"  [ERROR] Response: {response.text[:500]}")
            return {
                'total_items': 0,
                'snoozed_items': 0,
                'snoozed_items_list': [],
                'active_items_list': []
            }
        
        data = response.json()
        print(f"  [DEBUG] Response keys: {list(data.keys())}")
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Request exception in getPreview: {type(e).__name__}: {e}")
        return {
            'total_items': 0,
            'snoozed_items': 0,
            'snoozed_items_list': [],
            'active_items_list': []
        }
    except Exception as e:
        print(f"  [ERROR] Exception in getPreview: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'total_items': 0,
            'snoozed_items': 0,
            'snoozed_items_list': [],
            'active_items_list': []
        }

    total_categories = 0
    total_subcategories = 0
    total_items = 0
    snoozed_items = 0
    
    snoozed_items_list = []
    active_items_list = []

    # Create a dictionary of all products from the menu preview
    products_dict = {}
    if 'products' in data:
        products_dict = data['products']

    if 'categories' in data:
        categories = data['categories']
        total_categories = len(categories)
        for category in categories:
            category_name = category.get('name', 'Unnamed Category')
            category_items = 0
            category_snoozed = 0
            # Count items in subcategories
            if 'subCategories' in category:
                total_subcategories += len(category['subCategories'])
                for subcategory in category['subCategories']:
                    subcategory_name = subcategory.get('name', 'Unnamed Subcategory')
                    if 'products' in subcategory:
                        for product_id in subcategory['products']:
                            product = products_dict.get(product_id, {})
                            product_name = product.get('name', 'Unknown Product')
                            product_plu = product.get('plu', 'N/A')
                            
                            if isSnoozed(product_id, products_dict):
                                snoozed_items += 1
                                category_snoozed += 1
                                snoozed_items_list.append({
                                    'Location': location_name,
                                    'Category': category_name,
                                    'Subcategory': subcategory_name,
                                    'Product Name': product_name,
                                    'PLU': product_plu,
                                    'Product ID': product_id
                                })
                            else:
                                total_items += 1
                                category_items += 1
                                active_items_list.append({
                                    'Location': location_name,
                                    'Category': category_name,
                                    'Subcategory': subcategory_name,
                                    'Product Name': product_name,
                                    'PLU': product_plu,
                                    'Product ID': product_id
                                })
            # Count items directly in category
            if 'products' in category:
                for product_id in category['products']:
                    product = products_dict.get(product_id, {})
                    product_name = product.get('name', 'Unknown Product')
                    product_plu = product.get('plu', 'N/A')
                    
                    if isSnoozed(product_id, products_dict):
                        snoozed_items += 1
                        category_snoozed += 1
                        snoozed_items_list.append({
                            'Location': location_name,
                            'Category': category_name,
                            'Subcategory': 'N/A',
                            'Product Name': product_name,
                            'PLU': product_plu,
                            'Product ID': product_id
                        })
                    else:
                        total_items += 1
                        category_items += 1
                        active_items_list.append({
                            'Location': location_name,
                            'Category': category_name,
                            'Subcategory': 'N/A',
                            'Product Name': product_name,
                            'PLU': product_plu,
                            'Product ID': product_id
                        })

    print(f"Total Categories: {total_categories}")
    print(f"Total Items (excluding snoozed): {total_items}")
    print(f"Snoozed Items: {snoozed_items}")
    
    return {
        'total_items': total_items,
        'snoozed_items': snoozed_items,
        'snoozed_items_list': snoozed_items_list,
        'active_items_list': active_items_list
    }

def getLocationCount(accountId):
    try:
        url = f"https://api.deliverect.io/accounts/{accountId}"
        print(f"[DEBUG] Fetching locations from: {url}")
        response = requests.request("GET", url, headers=headers)
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to get account locations: Status {response.status_code}")
            print(f"[ERROR] Response: {response.text[:200]}")
            return []
        
        data = response.json()
        locationList = data.get("locations", [])
        print(f"[DEBUG] Found {len(locationList)} locations")
        return locationList[::-1]
    except Exception as e:
        print(f"[ERROR] Exception in getLocationCount: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    try:
        print(f"{'='*60}")
        print(f"Starting menu count analysis...")
        print(f"{'='*60}")
        
        # Verify authentication
        print(f"[DEBUG] Checking authentication...")
        try:
            test_response = requests.get("https://api.deliverect.io/accounts", headers=headers)
            if test_response.status_code == 200:
                print(f"[SUCCESS] Authentication OK")
            else:
                print(f"[WARNING] Authentication check returned status {test_response.status_code}")
        except Exception as e:
            print(f"[ERROR] Authentication check failed: {e}")
        
        print(f"\n[INFO] Account ID: {account}")
        print(f"[INFO] Menu ID: {menu}")
        print(f"[INFO] Channel: {channel}")
        print(f"[INFO] Location to check: {locIdtoCheck}")
        
        # Get location name for filename
        location_name_for_file = getLocationName(locIdtoCheck)
        if location_name_for_file:
            # Sanitize filename (remove invalid characters)
            safe_location_name = "".join(c for c in location_name_for_file if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_location_name = safe_location_name.replace(' ', '_')
            excel_file = os.path.join(os.path.dirname(__file__), f'{safe_location_name}_menu_analysis.xlsx')
        else:
            # Fallback to location ID if name not available
            excel_file = os.path.join(os.path.dirname(__file__), f'{locIdtoCheck}_menu_analysis.xlsx')
        
        print(f"[INFO] Excel file path: {excel_file}")
        
        print(f"\n[STEP 1] Fetching locations...")
        locations = getLocationCount(account)
        print(f"[INFO] Found {len(locations)} locations to process")
        
        if not locations:
            print(f"[ERROR] No locations found! Exiting.")
            exit(1)
        
        # Lists to collect data
        overview_data = []
        all_snoozed_items = []
        all_active_items = []
        
        for i, location in enumerate(locations, 1):
            print(f"\n{'='*60}")
            print(f"Processing location {i}/{len(locations)}: {location}")
            print(f"{'='*60}")
            
            if location != locIdtoCheck:
                print(f"  [SKIP] Location {location} doesn't match {locIdtoCheck}")
                continue
            
            # Check if location has the "pilot stores" tag
            print(f"  [STEP 1] Getting location name...")
            location_name = getLocationName(location)
            if location_name is None:
                print(f"  [WARNING] Skipping location {location} - could not get name")
                continue
            
            print(f"  [STEP 2] Fetching menu preview for: {location_name}")
            url = f"https://api.deliverect.io/menuPreview?account={account}&menu={menu}&location={location}&channel={channel}"
            print(f"  [DEBUG] URL: {url}")
            
            result = getPreview(url, location_name)
            
            if result is None:
                print(f"  [ERROR] Failed to get preview for {location_name}")
                continue
            
            print(f"  [STEP 3] Processing results...")
            print(f"  Location: {location_name} has:")
            print(f"    - Total Items (excluding snoozed): {result['total_items']}")
            print(f"    - Snoozed Items: {result['snoozed_items']}")
            
            # Add to overview
            overview_data.append({
                'Location': location_name,
                'Total Items on Menu': result['total_items'] + result['snoozed_items'],
                'Active Items': result['total_items'],
                'Snoozed Items': result['snoozed_items']
            })
            
            # Add to detailed lists
            all_snoozed_items.extend(result['snoozed_items_list'])
            all_active_items.extend(result['active_items_list'])
            print(f"  [SUCCESS] Completed processing {location_name}")
        
        # Create Excel file with multiple sheets
        print(f"\n{'='*60}")
        print(f"[STEP 4] Creating Excel file with {len(overview_data)} locations...")
        print(f"{'='*60}")
        
        try:
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Tab 1: Overview
                if overview_data:
                    df_overview = pd.DataFrame(overview_data)
                    df_overview.to_excel(writer, sheet_name='Overview', index=False)
                    print(f"  [SUCCESS] Created 'Overview' sheet with {len(overview_data)} rows")
                else:
                    print(f"  [WARNING] No overview data to write")
                
                # Tab 2: Snoozed Items
                if all_snoozed_items:
                    df_snoozed = pd.DataFrame(all_snoozed_items)
                    df_snoozed.to_excel(writer, sheet_name='Snoozed Items', index=False)
                    print(f"  [SUCCESS] Created 'Snoozed Items' sheet with {len(all_snoozed_items)} rows")
                else:
                    print(f"  [INFO] No snoozed items found")
                
                # Tab 3: Active Items
                if all_active_items:
                    df_active = pd.DataFrame(all_active_items)
                    df_active.to_excel(writer, sheet_name='Active Items', index=False)
                    print(f"  [SUCCESS] Created 'Active Items' sheet with {len(all_active_items)} rows")
                else:
                    print(f"  [INFO] No active items found")
            
            print(f"\n{'='*60}")
            print(f"✅ Analysis complete!")
            print(f"{'='*60}")
            print(f"📁 Excel file saved to: {excel_file}")
            print(f"   - Overview: {len(overview_data)} locations")
            print(f"   - Snoozed Items: {len(all_snoozed_items)} items")
            print(f"   - Active Items: {len(all_active_items)} items")
        except Exception as e:
            print(f"\n[ERROR] Failed to create Excel file: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    except KeyboardInterrupt:
        print(f"\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()