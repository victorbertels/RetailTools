import sys
from pathlib import Path
# Add project root to Python path (must be before project imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


from authentication.tokening import getToken, headers 
import requests
import csv

def getInventory(account: str ):
    page = 1
    inventory_url = f"https://api.deliverect.io/catalog/accounts/{account}/inventory"
    inventory_items = []
    while True:
        payload_inventory = {"sort":"-_id","max_results":50,"locations":[], "page": page}
        response = requests.post(inventory_url, headers=headers, json=payload_inventory)
        inventory = response.json()
        items = inventory.get("_items", [])
        if not items:
            break
        inventory_items.extend(items)
        page += 1
        print("Fetching inventory on page" , page)
    return inventory_items

def hasInventory(inventory: list, plu: str , location: str):
    for item in inventory:
        if item.get("plu") == plu:
            locations = item.get("locations", [])
            # Check if the location is in the list of locations
            for loc_obj in locations:
                if loc_obj.get("location") == location:
                    return True
    return False

def buildInventoryLookup(inventory: list):
    """Build a set of (plu, location) tuples for O(1) lookup"""
    lookup = set()
    for item in inventory:
        plu = item.get("plu")
        if plu:
            locations = item.get("locations", [])
            for loc_obj in locations:
                location_id = loc_obj.get("location")
                if location_id:
                    lookup.add((plu, location_id))
    return lookup



def getItems(account: str):
    items_list = []
    page = 1
    while True:
        items = f"https://api.deliverect.io/catalog/accounts/{account}/items"
        payloadItems = {"visible":True,"max_results":500,"sort":"-_id", "page": page}
        response = requests.post(items, headers=headers, json=payloadItems).json()
        items = response["_items"]
        if not items:
            break
        for item in items:
            #Can add whatever we want here.
            toAdd = {"plu": item.get("plu"), "name": item.get("name")}
            items_list.append(toAdd)
        page += 1
        print("Fetching items on page" , page)
    return items_list

def getLocationName(location: str):
    url = f"https://api.deliverect.io/locations/{location}"
    response = requests.get(url, headers=headers)
    return response.json().get("name")

def getAccountName(account: str):
    url = f"https://api.deliverect.io/accounts/{account}"
    response = requests.get(url, headers=headers)
    return response.json().get("name")


def writeToCSV(missing_inventory: list, account: str, location: str, location_name: str = None, account_name: str = None):
    # Cache names to avoid repeated API calls
    if account_name is None:
        account_name = getAccountName(account)
    if location_name is None:
        location_name = getLocationName(location)
    
    with open(f"missingInventory_{account_name}_{location_name}.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["Location", "PLU", "Name", ])
        for item in missing_inventory:
            writer.writerow([location_name, item.get("plu"), item.get("name")])

def getAllLocations(account : str ):
    url = f"https://api.deliverect.io/accounts/{account}"
    response = requests.get(url, headers=headers)
    return response.json().get("locations")

def getMissingInventory(account : str , location : str = None, inventory : list = None, items : list = None):
    # Use provided data or fetch if not provided
    if inventory is None:
        inventory = getInventory(account)
    if items is None:
        items = getItems(account)
    
    # Build lookup set once for fast O(1) checks
    inventory_lookup = buildInventoryLookup(inventory)
    
    if location is None:
        locations = getAllLocations(account)
        # Pre-fetch account name once
        account_name = getAccountName(account)
        
        # Build location name cache to avoid repeated API calls
        location_name_cache = {}
        # Fetch all location names upfront (batch if possible, or cache as we go)
        for loc in locations:
            loc_id = loc if isinstance(loc, str) else (loc.get("id") if isinstance(loc, dict) else loc)
            if isinstance(loc, dict) and loc.get("name"):
                location_name_cache[loc_id] = loc.get("name")
            else:
                # Fetch name and cache it
                location_name_cache[loc_id] = getLocationName(loc_id)
        
        missing_per_location = {}
        for loc in locations:
            # Handle both string IDs and dict objects
            loc_id = loc if isinstance(loc, str) else (loc.get("id") if isinstance(loc, dict) else loc)
            missing_inventory = []
            for item in items:
                plu = item.get("plu")
                # Fast O(1) lookup instead of O(n) search
                if plu and (plu, loc_id) not in inventory_lookup:
                    missing_inventory.append(item)
            if missing_inventory:
                location_name = location_name_cache.get(loc_id, "Unknown")
                writeToCSV(missing_inventory, account, loc_id, location_name=location_name, account_name=account_name)
                missing_per_location[loc_id] = {
                    "location_name": location_name,
                    "location_id": loc_id,
                    "missing_items": missing_inventory,
                    "count": len(missing_inventory)
                }
        return missing_per_location
    else:
        missing_inventory = []
        for item in items:
            plu = item.get("plu")
            # Fast O(1) lookup instead of O(n) search
            if plu and (plu, location) not in inventory_lookup:
                missing_inventory.append(item)
        # Pre-fetch names once to avoid repeated API calls
        location_name = getLocationName(location)
        account_name = getAccountName(account)
        writeToCSV(missing_inventory, account, location, location_name=location_name, account_name=account_name)
        return missing_inventory


# print(getInventory("689da16a194569500f454819", "6904bd808e1c9f7c711dfe45")) #SPAR 
# print(getInventory("6929b2df534c927a631cd6b1", "6929b3740fbed98992338f45")) # TEST ACCOUNT
# print(getItems("6929b2df534c927a631cd6b1")) # TEST ACCOUNT
# print(getItems("689da16a194569500f454819")) #SPAR
print(getMissingInventory("6929b2df534c927a631cd6b1")) #TEST ACCOUNT
# print(getMissingInventory("689da16a194569500f454819", "6904bd808e1c9f7c711dfe45")) #SPAR

