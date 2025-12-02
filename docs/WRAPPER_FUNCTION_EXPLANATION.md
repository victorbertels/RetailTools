# Understanding Wrapper Functions and Function Signatures

## The Context

When refactoring, sometimes the shared function has a slightly different signature (parameters) than what your old code expects. You have 3 options:

## Option 1: Update the Shared Function

**What it means:** Modify the shared function in `utils/api_helpers.py` to support both the old way and new way.

### Example:

**Old code expects:**
```python
def getAllLocations(account):
    # Returns just location IDs: ["loc1", "loc2", ...]
    return location_ids
```

**Shared function returns:**
```python
def getAllLocations(account, return_format="list"):
    # Returns list of dicts: [{"name": "...", "id": "..."}, ...]
    return location_list
```

**Solution:** The shared function already supports this with `return_format="ids"`!

```python
# Your old code:
locations = getAllLocations(account)  # Expects IDs

# Update shared function to support both:
def getAllLocations(account, return_format="list"):
    if return_format == "ids":
        # Return just IDs (old way)
        return [loc.get("_id") for loc in items]
    else:
        # Return list of dicts (new way)
        return location_list
```

---

## Option 2: Create a Wrapper Function

**What it means:** Create a small function in YOUR module that calls the shared function and adapts it to match what your code expects.

### Example:

**Your old code:**
```python
# Old function you had:
def getLocationName(location, tags=None):
    # Your custom logic with tags
    url = f"https://api.deliverect.io/locations/{location}"
    response = requests.get(url, headers=headers)
    name = response.json().get("name")
    tags = response.json().get("tags", [])
    
    if tags and "pilot" in [t.lower() for t in tags]:
        return name
    return name
```

**Shared function:**
```python
# In utils/api_helpers.py:
def getLocationName(location: str):
    # Simple version, no tags parameter
    url = f"https://api.deliverect.io/locations/{location}"
    response = requests.get(url, headers=headers)
    return response.json().get("name")
```

**Solution: Create a wrapper:**
```python
# In your module (countItems.py):
from utils import getLocationName as _getLocationName

def getLocationName(location, tags=None):
    """
    Wrapper function that adds tags functionality.
    Calls the shared function, then adds your custom logic.
    """
    # Call the shared function
    name = _getLocationName(location)
    
    # Add your custom logic
    if tags:
        # Your custom tag checking logic here
        # ... (fetch tags if needed, etc.)
        pass
    
    return name
```

**Now your existing code works without changes:**
```python
# Your old code still works!
name = getLocationName(location, tags=["pilot"])
```

### Another Example:

**Your old code expects:**
```python
locations = getAllLocations(account)  # Returns just IDs
```

**Shared function returns:**
```python
locations = getAllLocations(account)  # Returns [{"name": "...", "id": "..."}]
```

**Create a wrapper:**
```python
# In your module:
from utils import getAllLocations as _getAllLocations

def getAllLocations(account):
    """
    Wrapper that returns just IDs (old format).
    """
    locations = _getAllLocations(account)  # Get new format
    return [loc.get("id") for loc in locations]  # Convert to old format
```

**Now your code works:**
```python
# Your old code still works!
location_ids = getAllLocations(account)  # Gets just IDs like before
```

---

## Option 3: Update Your Code

**What it means:** Change your existing code to use the new function signature directly.

### Example:

**Old code:**
```python
# Old way - get just location IDs
locations = getAllLocations(account)
for loc_id in locations:
    print(loc_id)
```

**New shared function:**
```python
# Returns list of dicts: [{"name": "...", "id": "..."}, ...]
locations = getAllLocations(account)
```

**Update your code:**
```python
# New way - adapt to new format
locations = getAllLocations(account)
for location in locations:
    loc_id = location.get("id")  # Extract ID from dict
    loc_name = location.get("name")  # Bonus: now you have name too!
    print(f"{loc_name}: {loc_id}")
```

**Or use the return_format parameter:**
```python
# Use return_format to get what you need
location_ids = getAllLocations(account, return_format="ids")
for loc_id in location_ids:
    print(loc_id)
```

---

## Which Option to Choose?

### Use Option 1 (Update Shared Function) when:
- ✅ The change benefits everyone
- ✅ It's a simple addition (like adding a parameter)
- ✅ It doesn't break existing code

### Use Option 2 (Wrapper Function) when:
- ✅ You have custom logic specific to your module
- ✅ You want to keep your existing code unchanged
- ✅ The shared function is close but not quite right

### Use Option 3 (Update Your Code) when:
- ✅ The new signature is better
- ✅ You want to use the new features
- ✅ It's a simple change

---

## Real Example from Your Codebase

### Before Refactoring:
```python
# In countItems.py:
def getLocationName(location, tags=None):
    # Custom version with tags
    url = f"https://api.deliverect.io/locations/{location}"
    response = requests.get(url, headers=headers)
    name = response.json().get("name")
    # ... tag logic ...
    return name
```

### After Refactoring - Option 2 (Wrapper):
```python
# In countItems.py:
from utils import getLocationName as _getLocationName

def getLocationName(location, tags=None):
    """Wrapper that adds tags functionality."""
    name = _getLocationName(location)  # Use shared function
    if tags:
        # Add your custom tag logic here
        # ... (you might need to fetch tags separately)
        pass
    return name

# Your existing code still works!
name = getLocationName(location, tags=["pilot"])
```

### After Refactoring - Option 3 (Update Code):
```python
# In countItems.py:
from utils import getLocationName

# Update your code - remove tags parameter since shared function doesn't support it
# Old code: name = getLocationName(location, tags=["pilot"])
# New code:
name = getLocationName(location)

# If you still need tag filtering, you'd need to:
# 1. Use Option 2 (wrapper) to keep tags functionality, OR
# 2. Fetch location data separately and filter tags yourself
```

---

## Summary

**Wrapper function** = A small function in your module that:
- Calls the shared function
- Adapts it to match what your code expects
- Lets you keep your existing code unchanged

**Update your code** = Change your existing code to:
- Use the new function signature directly
- Take advantage of new features
- Modernize your code

Both approaches work! Choose based on:
- How much code you'd need to change
- Whether you need custom logic
- Whether you want to modernize or maintain compatibility

