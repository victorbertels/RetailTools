import sys
from pathlib import Path

# Add project root to Python path (must be before project imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from authentication.tokening import getHeaders
import requests
from utils import getAllLocations, getAllChannelLinks


def returnChannelLinksPerChannel(channelLinks: list, channel: int):
    """
    Get channel link IDs for a specific channel.
    
    Args:
        channelLinks: List of channel link dicts from getAllChannelLinks()
        channel: Channel ID (backendId) to filter by
        
    Returns:
        List of channel link IDs for the specified channel, or None if not found
    """
    # Search by channel ID (more efficient than converting to name first)
    for channelLink in channelLinks:
        if channelLink.get("channelId") == channel:
            return channelLink.get("channelLinksIds")
    return None
  
def closeStore(locationId: str, preparationTimeDelay: int):
    url = f"https://api.deliverect.io/location/{locationId}/busymode"
    payload = {"locationId":locationId,"preparationTimeDelay":preparationTimeDelay}
    response = requests.post(url, headers=getHeaders(), json=payload)
    print(response.json())
    if response.status_code == 200:
        print(f"Location {locationId} closed successfully")
        return True
    else:
        print(f"Location {locationId} failed to close")
        return False

def closeChannelLink(channelLinkId: str, preparationTimeDelay: int):
    url = f"https://api.deliverect.io/channellink/{channelLinkId}/busymode"
    payload = {"channelLinkId":channelLinkId,"preparationTimeDelay":preparationTimeDelay}
    response = requests.post(url, headers=getHeaders(), json=payload)
    print(response.json())
    if response.status_code == 200:
        print(f"Channel Link {channelLinkId}  successfully")
        return True
    else:
        print(f"Channel Link {channelLinkId} failed")
        return False

def closeOpenAllStores(account: str, type: int , channel: int = None):
    if type == 1:
        preparationTimeDelay = 999
    elif type == 0:
        preparationTimeDelay = 0
  
    if not channel:
        for location in getAllLocations(account):
            if closeStore(location.get("id"), preparationTimeDelay):
                return True
        return False
    else:
        channelLinks = getAllChannelLinks(account)
        channelLinksIds = returnChannelLinksPerChannel(channelLinks, channel)
        if channelLinksIds:
            for channelLinkId in channelLinksIds:
                closeChannelLink(channelLinkId, preparationTimeDelay)
        return True
    return False





print(closeOpenAllStores("6929b2df534c927a631cd6b1", 0, 1))