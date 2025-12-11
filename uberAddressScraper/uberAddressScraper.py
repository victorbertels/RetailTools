import sys
from pathlib import Path

# Add project root to Python path (must be before project imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import re
import requests
from authentication.tokening import getHeaders
from utils.api_helpers import getAllLocations

# Only execute when run as a script, not when imported
if __name__ == "__main__":
    account = "685956b666059602c05db528"
    
    # Get all locations - returns list of dicts with "id" and "name"
    all_locs_raw = getAllLocations(account, return_format="raw")

def getUberInfo(application, uuid):
    """Get Uber Eats store information from Deliverect API."""
    url = f"https://api.deliverect.io/ubereats/{application}/stores/{uuid}?legacy=true"
    response = requests.get(url, headers=getHeaders())
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting Uber info: {response.status_code} - {response.text}")
        return None

def findUberChannelLink(locationId, channel):
    """Find Uber Eats channel link for a location by channel ID."""
    url = f"https://api.deliverect.io/channelLinks?where={{\"location\":\"{locationId}\",\"channel\":{channel}}}"
    response = requests.get(url, headers=getHeaders())
    
    if response.status_code != 200:
        return None
    
    items = response.json().get("_items", [])
    if not items:
        return None
    
    # Return first matching channel link
    cl = items[0]
    return {
        "channelLinkId": cl.get("_id"),
        "APIKey": cl.get("APIKey"),
        "application": cl.get("channelSettings", {}).get("application"),
        "channel": channel  # Include channel ID for reference
    }

def findUberChannelLinkAny(locationId):
    """Find Uber Eats channel link for a location, trying channel 6007 first, then 7."""
    # Try channel 6007 first (standard Uber Eats channel)
    channel_link = findUberChannelLink(locationId, 6007)
    if channel_link:
        print(f"  ✓ Found Uber channel link on channel 6007")
        return channel_link
    
    # Fallback to channel 7
    channel_link = findUberChannelLink(locationId, 7)
    if channel_link:
        print(f"  ✓ Found Uber channel link on channel 7")
        return channel_link
    
    return None

def stripNumberFromStreet(street):
    """Extract house number from street address."""
    match = re.search(r'\d+', street or "")
    return match.group(0) if match else ""

def mapAddressInfo(address):
    """Map Uber address info to Deliverect location address format."""
    if not address or not address.get("location"):
        return None
    
    location = address.get("location", {})
    addressInfo = {
        "address": {
            "restaurantName": address.get("name"),
            "country": location.get("country"),
            "stateOrProvince": location.get("state"),
            "city": location.get("city"),
            "postalCode": location.get("postal_code"),
            "street": location.get("address"),
            "houseNumber": stripNumberFromStreet(location.get("address"))
        }
    }
    return addressInfo

def returnUberUrl(uberInfo):
    """Extract web URL from Uber info."""
    return uberInfo.get("web_url") if uberInfo else None

def updateChannelLink(channelLinkId, web_url):
    """Update channel link with Uber store URL."""
    if not channelLinkId or not web_url:
        print(f"Skipping channel link update - missing data")
        return False
    
    # First get the channel link to get the etag
    url = f"https://api.deliverect.io/channelLinks/{channelLinkId}"
    response = requests.get(url, headers=getHeaders())
    
    if response.status_code != 200:
        print(f"Error getting channel link for update: {response.status_code}")
        return False
    
    etag = response.json().get("_etag")
    if not etag:
        print(f"Error: No etag found for channel link {channelLinkId}")
        return False
    
    # Update with etag
    headers = getHeaders()
    headers["If-Match"] = etag
    update_url = f"https://api.deliverect.io/channelLinks/{channelLinkId}"
    payload = {"channelSettings": {"storeUrl": web_url}}
    update_response = requests.patch(update_url, headers=headers, json=payload)
    
    if update_response.status_code == 200:
        print(f"✓ Updated channel link {channelLinkId} with URL: {web_url}")
        return True
    else:
        print(f"✗ Failed to update channel link: {update_response.status_code} - {update_response.text}")
        return False

def updateLocationAddress(locationId, addressInfo):
    """Update location with address information."""
    if not locationId or not addressInfo:
        print(f"Skipping location update - missing data")
        return False
    
    # First get the location to get the etag
    url = f"https://api.deliverect.io/locations/{locationId}"
    response = requests.get(url, headers=getHeaders())
    
    if response.status_code != 200:
        print(f"Error getting location for update: {response.status_code}")
        return False
    
    etag = response.json().get("_etag")
    if not etag:
        print(f"Error: No etag found for location {locationId}")
        return False
    
    # Update with etag
    headers = getHeaders()
    headers["If-Match"] = etag
    update_url = f"https://api.deliverect.io/locations/{locationId}"
    update_response = requests.patch(update_url, headers=headers, json=addressInfo)
    
    if update_response.status_code == 200:
        print(f"✓ Updated location {locationId} with address info")
        return True
    else:
        print(f"✗ Failed to update location: {update_response.status_code} - {update_response.text}")
        return False

    # Process all locations
    print(f"Processing {len(all_locs_raw)} locations...\n")
    
    for loc in all_locs_raw:
        location_id = loc.get("_id")
        location_name = loc.get("name", "Unknown")
        tags = loc.get("tags", [])
        
        # Filter for PILOT STORES only

        
        print(f"\n📍 Processing: {location_name} ({location_id})")
        
        # Find Uber channel link (tries channel 6007 first, then 7)
        print(f"  🔍 Searching for Uber channel link (trying channels 6007 and 7)...")
        uberChannelLink = findUberChannelLinkAny(location_id)
        if not uberChannelLink:
            print(f"  ⚠ No Uber Eats channel link found for this location (checked channels 6007 and 7)")
            continue
        
        APIKey = uberChannelLink.get("APIKey")
        application = uberChannelLink.get("application")
        uberChannelLinkId = uberChannelLink.get("channelLinkId")
        
        if not APIKey or not application:
            print(f"  ⚠ Missing APIKey or application for channel link")
            continue
        
        # Get Uber info
        print(f"  🔍 Fetching Uber store info...")
        UberInfo = getUberInfo(application, APIKey)
        if not UberInfo:
            print(f"  ⚠ Failed to get Uber info")
            continue
        
        # Map address info
        addressInfo = mapAddressInfo(UberInfo)
        if not addressInfo:
            print(f"  ⚠ Failed to map address info")
            continue
        
        # Get Uber URL
        uberUrl = returnUberUrl(UberInfo)
        
        # Update channel link
        print(f"  🔄 Updating channel link...")
        updateChannelLink(uberChannelLinkId, uberUrl)
        
        # Update location address
        print(f"  🔄 Updating location address...")
        updateLocationAddress(location_id, addressInfo)
        
        # Print results
        print(f"  ✅ Completed updates for {location_name}")
        print(f"     Address: {addressInfo.get('address', {}).get('street', 'N/A')}")
        print(f"     URL: {uberUrl}")
    
    print(f"\n✅ Processing complete!")
