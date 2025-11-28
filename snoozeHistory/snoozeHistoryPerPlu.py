import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import requests
from authentication.tokening import getToken, headers 


def get_snooze_history_for_plu(
    location: str,
    account: str,
    plu: str,
    weeks_back: int = 1,
    operation_types: List[int] = None,
    max_results: int = 500
) -> Optional[List[Dict]]:
    """
    Fetch snooze history for a specific PLU (Product Lookup Unit).
    
    Args:
        location: Deliverect location ID
        account: Deliverect account ID
        plu: Product Lookup Unit identifier
        weeks_back: Number of weeks to look back from now (default: 1)
        operation_types: List of operation types to filter (default: [15, 2, 3])
        max_results: Maximum number of results to return (default: 500)
    
    Returns:
        List of snooze event dictionaries, or None if an error occurred
    
    Raises:
        Exception: If API request fails
    """
    if operation_types is None:
        operation_types = [15, 2, 3]
    
    # Get authentication token
    token = getToken()

    
    # Calculate date range
    stop_dt = datetime.now(timezone.utc)
    stop = stop_dt.isoformat(timespec='microseconds').replace('+00:00', 'Z')
    start_dt = stop_dt - timedelta(weeks=weeks_back)
    start = start_dt.isoformat(timespec='microseconds').replace('+00:00', 'Z')
    
    # Build API request
    url = f"https://api.deliverect.io/evefind/operationReports?sort=-_created&max_results={max_results}"
    
    # Build the where clause - use dot notation for nested snooze field
    snooze_key = f"snooze.{plu}"
    
    where_clause = {
        "operationType": {"$in": operation_types},
        "account": {"$in": [account]},
        "location": {"$in": [location]},
        "_created": {
            "$gt": start,
            "$lt": stop
        }
    }
    
    # Add the snooze field query using bracket notation to set the dynamic key
    where_clause[snooze_key] = {"$exists": True}
    
    payload = {"where": where_clause}
    
    # Make API request
    response = requests.post(url, json=payload, headers=headers)
    
    # Check for errors
    if response.status_code != 200:
        raise Exception(f"API Error: Status code {response.status_code}, Response: {response.text}")
    
    opsreports = response.json()
    ops_items = opsreports.get('_items', [])
    
    # Parse snooze history from operation reports
    history = []
    for ops in ops_items:
        ops_id = ops.get("_id", "")
        snooze = ops.get("snooze", {})
        
        if plu in snooze:
            snooze_info = snooze[plu]
            user_info = ops.get("user", {})
            snooze_end = snooze_info.get("snoozeEnd")
            action = snooze_info.get("action")
            user_name = user_info.get("name", "DELIVERECT")
            user_id = user_info.get("id", "")
            
            # Detect QUEST automated snoozes
            if action == 1 and snooze_end and "00:00" in snooze_end:
                user_name = "QUEST"
                user_id = ""
                
            event = {
                "id": ops_id,
                "snoozeStart": snooze_info.get("snoozeStart"),
                "snoozeEnd": snooze_end,
                "action": action,  # 2 = UNSNOOZE, 1 = SNOOZE
                "snoozeId": snooze_info.get("snoozeId"),
                "channels": snooze_info.get("channelLinks", {}),
                "name": snooze_info.get("name", ""),
                "plu": snooze_info.get("plu", plu),
                "report_id": ops_id,
                "user_id": user_id,
                "user_name": user_name,
                "created": ops.get("_created")
            }
            history.append(event)
    
    # Sort by creation date
    history.sort(key=lambda x: x["created"] or "")
    
    return history


def format_snooze_history(history: List[Dict], plu: str, start_date: str = None) -> str:
    """
    Format snooze history into a human-readable string.
    
    Args:
        history: List of snooze event dictionaries
        plu: Product Lookup Unit identifier
        start_date: Start date for the search range (optional)
    
    Returns:
        Formatted string representation of the history
    """
    if not history:
        return f"\n======= No Snooze History Found for PLU: {plu} =======\n"
    
    output = []
    output.append(f"\n======= Snooze History for PLU: {plu} =======\n")
    if start_date:
        output.append(f"Search range from: {start_date}\n")
    
    for idx, event in enumerate(history, 1):
        action_str = "SNOOZE" if event['action'] == 1 else ("UNSNOOZE" if event['action'] == 2 else str(event['action']))
        
        output.append(f"Event #{idx}")
        output.append(f"  Created:     {event['created']}")
        output.append(f"  PLU:         {event['plu']}")
        output.append(f"  Name:        {event['name']}")
        output.append(f"  Action:      {action_str}")
        
        if event['action'] == 2:
            output.append("----------------------------------------")
            output.append(f"  UNSNOOZED the item at: {event['created']}")
            output.append("----------------------------------------")
        
        output.append(f"  Start:       {event['snoozeStart']}")
        output.append(f"  End:         {event['snoozeEnd']}")
        output.append(f"  SnoozeId:    {event['snoozeId']}")
        output.append(f"  User:        {event['user_name']} ({event['user_id']})")
        output.append(f"  Report Link: https://retail.deliverect.com/operationreports/{event['id']}")
        output.append("----------------------------------------\n")
    
    return "\n".join(output)


# For command-line usage or testing
if __name__ == "__main__":
    # Example usage - remove hardcoded values for production
    location = "68e50b01ca69f3b78146dc59"
    account = "67e1515214f41141b66ab1ea"
    plu = "40090042"
    
    try:
        history = get_snooze_history_for_plu(location, account, plu, weeks_back=1)
        if history:
            print(format_snooze_history(history, plu))
            print(f"\nTotal events found: {len(history)}")
        else:
            print(f"No snooze history found for PLU: {plu}")
    except Exception as e:
        print(f"Error: {e}")
