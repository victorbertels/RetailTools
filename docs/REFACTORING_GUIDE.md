# Refactoring Guide: Using Shared Utilities

## Overview

I've created a shared `utils` module that consolidates all the duplicate functions across your codebase. This guide shows you how to refactor your existing code to use it.

## New Structure

```
RetailTools/
├── utils/
│   ├── __init__.py          # Exports common functions
│   └── api_helpers.py       # All shared API functions
├── closeAllStores/
├── missingInventoryHighlighter.py/
├── countItemsInMenu/
└── catImporter/
```

## Available Functions

All these are now in `utils.api_helpers`:

- `getLocationName(location: str)` - Get location name by ID
- `getAccountName(account: str)` - Get account name by ID  
- `getAllLocations(account: str, return_format="list")` - Get all locations
- `findChannelNameById(channelId: int)` - Get channel name by ID
- `getAllChannelLinks(account: str, group_by_channel=True)` - Get channel links
- `paginate_api(url, ...)` - Generic pagination helper

## How to Refactor

### Step 1: Update Imports

**Before:**
```python
def getLocationName(location: str):
    url = f"https://api.deliverect.io/locations/{location}"
    response = requests.get(url, headers=headers)
    return response.json().get("name")
```

**After:**
```python
from utils import getLocationName
# Or
from utils.api_helpers import getLocationName
```

### Step 2: Remove Duplicate Functions

Delete the duplicate function definitions from your modules.

### Step 3: Update Function Calls

Most functions work the same, but `getAllLocations` has a new parameter:

**Before:**
```python
locations = getAllLocations(account)  # Returns raw locations array
```

**After:**
```python
from utils import getAllLocations

# Get as list of dicts (default)
locations = getAllLocations(account)  # [{"name": "...", "id": "..."}, ...]

# Get just IDs (if you need that)
location_ids = getAllLocations(account, return_format="ids")

# Get raw format (for backward compatibility)
raw_locations = getAllLocations(account, return_format="raw")
```

## Example Refactoring

### Example 1: missingInventory.py

**Before:**
```python
def getLocationName(location: str):
    url = f"https://api.deliverect.io/locations/{location}"
    response = requests.get(url, headers=headers)
    return response.json().get("name")

def getAccountName(account: str):
    url = f"https://api.deliverect.io/accounts/{account}"
    response = requests.get(url, headers=headers)
    return response.json().get("name")

def getAllLocations(account : str ):
    url = f"https://api.deliverect.io/accounts/{account}"
    response = requests.get(url, headers=headers)
    return response.json().get("locations")
```

**After:**
```python
from utils import getLocationName, getAccountName, getAllLocations

# Functions are now imported, no need to define them!
# Just use them directly:
location_name = getLocationName(location_id)
account_name = getAccountName(account_id)
locations = getAllLocations(account_id, return_format="raw")  # If you need raw format
```

### Example 2: closeOpenAllStores.py

**Before:**
```python
def findChannelNameById(channelId: int):
    url = f"https://api.deliverect.io/integrations?where={{\"integrationType\":\"channel\",\"backendId\":{channelId}}}"
    response = requests.get(url, headers=headers)
    return response.json().get("_items")[0].get("name")

def getAllLocations(account: str):
    location_list = []
    url = f"https://api.deliverect.io/locations?where={{\"account\":\"{account}\"}}"
    response = requests.get(url, headers=headers)
    for location in response.json().get("_items"):
        locationName = location.get("name")
        locationId = location.get("_id")
        location_list.append({"name":locationName,"id":locationId})
    return location_list

def getAllChannelLinks(account: str):
    # ... 30 lines of code ...
```

**After:**
```python
from utils import findChannelNameById, getAllLocations, getAllChannelLinks

# All functions are now imported!
# Use them directly:
channel_name = findChannelNameById(channel_id)
locations = getAllLocations(account)  # Already returns [{"name": ..., "id": ...}]
channel_links = getAllChannelLinks(account)  # Already grouped by channel
```

### Example 3: countItems.py

**Before:**
```python
def getLocationName(location, tags = None):
    try:
        url = f"https://api.deliverect.io/locations/{location}"
        response = requests.request("GET", url, headers=headers)
        # ... error handling ...
        return location_name
    except Exception as e:
        # ... error handling ...
        return None
```

**After:**
```python
from utils import getLocationName

# Use the shared function (it already has error handling)
location_name = getLocationName(location)

# If you need tags, you can extend it or make a wrapper:
def getLocationNameWithTags(location):
    from utils import getLocationName
    name = getLocationName(location)
    # Add your tag logic here if needed
    return name
```

## Benefits

1. **Single Source of Truth** - One place to fix bugs
2. **Consistency** - All modules use the same implementation
3. **Less Code** - Remove hundreds of lines of duplicate code
4. **Easier Maintenance** - Update once, works everywhere
5. **Better Testing** - Test utilities once, not in every module

## Migration Checklist

- [ ] Update `missingInventoryHighlighter.py/missingInventory.py`
- [ ] Update `closeAllStores/closeOpenAllStores.py`
- [ ] Update `countItemsInMenu/countItems.py`
- [ ] Update `catImporter/csvToCatalog.py`
- [ ] Test each module after refactoring
- [ ] Remove old duplicate functions

## Need Help?

If a function signature is slightly different, you can:
1. Update the shared function to support both use cases
2. Create a wrapper function in your module
3. Update your code to match the new signature

The shared functions are designed to be backward-compatible where possible!

