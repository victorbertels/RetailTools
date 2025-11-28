import sys
from pathlib import Path
# Add project root to Python path (must be before project imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


from authentication.tokening import getToken, headers 
import requests
import csv






def getInventory(account: str , location: str):
    page = 1
    inventory_url = f"https://api.deliverect.io/catalog/accounts/{account}/inventory"
    inventory_items = []
    while True:
        payload_inventory = {"sort":"-_id","max_results":50,"locations":[location], "page": page}
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

def writeToCSV(missing_inventory: list, account: str, location: str):
    with open(f"missingInventory_{account}_{location}.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["Location", "PLU", "Name", ])
        for item in missing_inventory:
            writer.writerow([getLocationName(location), item.get("plu"), item.get("name")])


def getMissingInventory(account : str , location : str ):
    missing_inventory = []
    inventory = getInventory(account, location)
    items = getItems(account)
    for item in items:
        if not hasInventory(inventory, item.get("plu"), location):
            missing_inventory.append(item)
    writeToCSV(missing_inventory, account, location)
    return missing_inventory


# print(getInventory("689da16a194569500f454819", "6904bd808e1c9f7c711dfe45")) #SPAR 
# print(getInventory("6929b2df534c927a631cd6b1", "6929b3740fbed98992338f45")) # TEST ACCOUNT
# print(getItems("6929b2df534c927a631cd6b1")) # TEST ACCOUNT
# print(getItems("689da16a194569500f454819")) #SPAR
print(getMissingInventory("6929b2df534c927a631cd6b1", "692a0a9459950498df806400")) #TEST ACCOUNT
# print(getMissingInventory("689da16a194569500f454819", "6904bd808e1c9f7c711dfe45")) #SPAR

