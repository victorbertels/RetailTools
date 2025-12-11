"""
Shared API helper functions for Deliverect API.
Consolidates common functions used across multiple modules.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from authentication.tokening import getHeaders
import requests


def getLocationName(location: str):
    """
    Get location name by location ID.
    
    Args:
        location: Location ID
        
    Returns:
        Location name or None if not found
    """
    try:
        url = f"https://api.deliverect.io/locations/{location}"
        response = requests.get(url, headers=getHeaders())
        if response.status_code == 200:
            return response.json().get("name")
        return None
    except Exception as e:
        print(f"Error getting location name: {e}")
        return None


def getAccountName(account: str):
    """
    Get account name by account ID.
    
    Args:
        account: Account ID
        
    Returns:
        Account name or None if not found
    """
    try:
        url = f"https://api.deliverect.io/accounts/{account}"
        response = requests.get(url, headers=getHeaders())
        if response.status_code == 200:
            return response.json().get("name")
        return None
    except Exception as e:
        print(f"Error getting account name: {e}")
        return None


def getAllLocations(account: str, return_format: str = "list"):
    """
    Get all locations for an account.
    
    Args:
        account: Account ID
        return_format: "list" returns list of dicts with name/id, 
                      "ids" returns just location IDs,
                      "raw" returns raw API response locations array
                      
    Returns:
        List of locations in requested format
    """
    try:
        url = f"https://api.deliverect.io/locations?where={{\"account\":\"{account}\"}}"
        response = requests.get(url, headers=getHeaders())
        
        if response.status_code != 200:
            return []
        
        items = response.json().get("_items", [])
        
        if return_format == "ids":
            # Return just location IDs (for backward compatibility with some code)
            return [item.get("_id") for item in items if item.get("_id")]
        elif return_format == "raw":
            # Return raw locations array (for backward compatibility)
            return items
        else:
            # Return list of dicts with name and id
            location_list = []
            for location in items:
                location_name = location.get("name")
                location_id = location.get("_id")
                if location_id:
                    location_list.append({"name": location_name, "id": location_id})
            return location_list
    except Exception as e:
        print(f"Error getting locations: {e}")
        return []


def findChannelNameById(channelId: int):
    """
    Find channel name by channel ID.
    
    Args:
        channelId: Channel ID (backendId)
        
    Returns:
        Channel name or None if not found
    """
    try:
        url = f"https://api.deliverect.io/integrations?where={{\"integrationType\":\"channel\",\"backendId\":{channelId}}}"
        response = requests.get(url, headers=getHeaders())
        
        if response.status_code == 200:
            items = response.json().get("_items", [])
            if items:
                return items[0].get("name")
        return None
    except Exception as e:
        print(f"Error getting channel name: {e}")
        return None


def getAllChannelLinks(account: str, group_by_channel: bool = True):
    """
    Get all channel links for an account, optionally grouped by channel.
    
    Args:
        account: Account ID
        group_by_channel: If True, returns list grouped by channel.
                        If False, returns flat list of all channel links.
                        
    Returns:
        If group_by_channel=True: [{"channel": channelName, "channelLinksIds": [...]}, ...]
        If group_by_channel=False: [{"name": ..., "id": ..., "channel": ...}, ...]
    """
    perChannelDict = {}
    page = 1
    
    while True:
        url = f"https://api.deliverect.io/channelLinks?where={{\"account\":\"{account}\"}}&page={page}&limit=500"
        response = requests.get(url, headers=getHeaders())
        
        if response.status_code != 200:
            break
            
        items = response.json().get("_items", [])
        if not items:
            break

        for channelLink in items:
            channelLinkId = channelLink.get("_id")
            channelLinkChannel = channelLink.get("channel")
            
            if group_by_channel:
                if channelLinkChannel not in perChannelDict:
                    perChannelDict[channelLinkChannel] = []
                perChannelDict[channelLinkChannel].append(channelLinkId)
            else:
                # For flat list, we'd need to store more info
                # This is for backward compatibility if needed
                pass

        page += 1
    
    if not group_by_channel:
        # Return flat list (implement if needed)
        return []
    
    # Convert to list of dicts grouped by channel
    result = []
    for channel_id, channel_link_ids in perChannelDict.items():
        channelName = findChannelNameById(channel_id)
        result.append({
            "channel": channelName,
            "channelId": channel_id,  # Also include ID for easier matching
            "channelLinksIds": channel_link_ids
        })
    
    return result


def paginate_api(url: str, items_key: str = "_items", max_results: int = 500, **kwargs):
    """
    Generic pagination helper for Deliverect API endpoints.
    
    Args:
        url: Base API URL (without page/limit params)
        items_key: Key in response JSON that contains the items array
        max_results: Number of results per page
        **kwargs: Additional query parameters
        
    Yields:
        Items from each page
    """
    page = 1
    while True:
        # Build URL with pagination
        params = f"&page={page}&limit={max_results}"
        if kwargs:
            param_str = "&".join([f"{k}={v}" for k, v in kwargs.items()])
            params = f"{param_str}{params}"
        
        full_url = f"{url}?{params}" if "?" not in url else f"{url}&{params}"
        
        response = requests.get(full_url, headers=getHeaders())
        if response.status_code != 200:
            break
            
        data = response.json()
        items = data.get(items_key, [])
        
        if not items:
            break
            
        yield items
        page += 1


def getAllCategoriesPerCatalog(catalogId: str) -> list:
    """
    Get all categories for a catalog.
    
    Args:
        catalogId: Catalog ID
    """
    try:
        page = 1    
        allCategories = []
        while True:
            url = f"https://api.deliverect.io/channelCategories?where={{\"menu\":\"{catalogId}\"}}&page={page}&max_results=500"
            response = requests.get(url, headers=getHeaders())
            if response.status_code != 200:
                break
            data = response.json()
            categories = data.get("_items", [])
            if not categories:
                break
            allCategories.extend(categories)
            page += 1
        print(f"Found {len(allCategories)} categories")
        return allCategories
    except Exception as e:
        print(f"Error getting categories for catalog: {e}")
        return []


def extractAllProductIdsFromCategories(categories: list) -> list:
    """
    Extract all product IDs from categories.
    getAllCategoriesPerCatalog already returns all categories (top-level and subcategories) in a flat list.
    This function simply extracts subProducts from each category and deduplicates them.
    
    Args:
        categories: List of all categories from getAllCategoriesPerCatalog (includes top-level and subcategories)
    
    Returns:
        List of unique product IDs (deduplicated)
    """
    allProductIds = set()  # Use set to automatically deduplicate
    
    for category in categories:
        subProducts = category.get("subProducts")
        if subProducts:
            # Add all product IDs to the set (automatically handles duplicates)
            allProductIds.update(subProducts)

    return list(allProductIds)  # Convert back to list


def getAccountIdfromCatalogId(catalogId: str) -> str:
    """
    Get account ID from catalog ID.
    
    Args:
        catalogId: Catalog ID
    """
    try:
        url = f"https://api.deliverect.io/channelMenus/{catalogId}"
        response = requests.get(url, headers=getHeaders())
        if response.status_code != 200:
            print(f"Error getting account ID from catalog ID: {response.status_code}")
            print(f"Error getting account ID from catalog ID: {response.text}")
            return None
        menu = response.json()
        return menu.get("account")
    except Exception as e:
        print(f"Error getting account ID from catalog ID: {e}")
        return None