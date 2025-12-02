# Complete Guide to Classes and Class Methods

## What is a Class?

A **class** is a blueprint for creating objects. Think of it as a template that defines:
- **Attributes** (data/properties)
- **Methods** (functions that work with that data)

## Why Use Classes?

Instead of having separate functions everywhere, classes group related functionality together.

**Without classes (what you have now):**
```python
# Scattered functions
def getLocationName(location_id):
    ...

def getAllLocations(account):
    ...

def getAccountName(account):
    ...
```

**With classes (organized):**
```python
class LocationManager:
    def get_location_name(self, location_id):
        ...
    
    def get_all_locations(self, account):
        ...
```

## Basic Class Structure

### Example: API Client Class

```python
class DeliverectAPI:
    """Class to handle Deliverect API operations."""
    
    def __init__(self, account_id):
        """
        Constructor - runs when you create an instance.
        'self' refers to the instance being created.
        """
        self.account_id = account_id
        self.base_url = "https://api.deliverect.io"
        from authentication.tokening import headers
        self.headers = headers
    
    def get_location_name(self, location_id):
        """Instance method - works with this specific account."""
        url = f"{self.base_url}/locations/{location_id}"
        response = requests.get(url, headers=self.headers)
        return response.json().get("name")
    
    def get_account_name(self):
        """Instance method - uses self.account_id."""
        url = f"{self.base_url}/accounts/{self.account_id}"
        response = requests.get(url, headers=self.headers)
        return response.json().get("name")

# Usage:
api = DeliverectAPI("6929b2df534c927a631cd6b1")  # Create instance
name = api.get_location_name("692a0a9459950498df806400")  # Use it
account_name = api.get_account_name()  # Uses the account_id we set
```

## Types of Methods

### 1. Instance Methods (Most Common)

**What:** Methods that work with a specific instance (object) of the class.

**Syntax:** First parameter is always `self`

```python
class InventoryManager:
    def __init__(self, account_id):
        self.account_id = account_id
        self.inventory = []
    
    def fetch_inventory(self):
        """Instance method - fetches inventory for THIS account."""
        # Uses self.account_id
        url = f"https://api.deliverect.io/catalog/accounts/{self.account_id}/inventory"
        response = requests.get(url, headers=headers)
        self.inventory = response.json().get("_items", [])
        return self.inventory
    
    def has_item(self, plu, location):
        """Instance method - checks THIS inventory."""
        for item in self.inventory:
            if item.get("plu") == plu:
                locations = item.get("locations", [])
                for loc_obj in locations:
                    if loc_obj.get("location") == location:
                        return True
        return False

# Usage:
manager = InventoryManager("6929b2df534c927a631cd6b1")
manager.fetch_inventory()  # Fetches for this account
exists = manager.has_item("123", "abc")  # Checks this inventory
```

### 2. Class Methods

**What:** Methods that work with the class itself, not a specific instance. Useful for:
- Creating alternative constructors
- Working with class-level data
- Factory methods

**Syntax:** Use `@classmethod` decorator, first parameter is `cls` (the class)

```python
class ChannelLinkManager:
    # Class variable (shared by all instances)
    base_url = "https://api.deliverect.io"
    
    def __init__(self, account_id):
        self.account_id = account_id
    
    @classmethod
    def from_account_name(cls, account_name):
        """
        Alternative constructor - create instance from account name.
        This is a class method because we're creating an instance.
        """
        # First, find account ID from name
        url = f"{cls.base_url}/accounts"
        response = requests.get(url, headers=headers)
        accounts = response.json().get("_items", [])
        
        for account in accounts:
            if account.get("name") == account_name:
                account_id = account.get("_id")
                return cls(account_id)  # Create and return instance
        return None
    
    @classmethod
    def get_all_channels(cls):
        """
        Class method - doesn't need an instance.
        Returns all available channels.
        """
        url = f"{cls.base_url}/channels"
        response = requests.get(url, headers=headers)
        return response.json().get("_items", [])

# Usage:
# Create instance normally:
manager1 = ChannelLinkManager("6929b2df534c927a631cd6b1")

# Create instance using class method (alternative constructor):
manager2 = ChannelLinkManager.from_account_name("SPAR Nederland")

# Use class method without creating instance:
all_channels = ChannelLinkManager.get_all_channels()
```

### 3. Static Methods

**What:** Methods that don't need `self` or `cls`. They're just regular functions but organized within the class.

**Syntax:** Use `@staticmethod` decorator, no `self` or `cls`

```python
class InventoryHelper:
    @staticmethod
    def build_lookup_set(inventory):
        """
        Static method - doesn't need instance or class.
        Just a utility function organized in the class.
        """
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
    
    @staticmethod
    def format_location_name(name):
        """Another utility function."""
        return name.strip().title()

# Usage:
# Can call without creating instance:
lookup = InventoryHelper.build_lookup_set(inventory)
formatted = InventoryHelper.format_location_name("  spar store  ")

# Or create instance and call:
helper = InventoryHelper()
lookup = helper.build_lookup_set(inventory)
```

## Complete Example: Refactored Inventory Manager

```python
import requests
from authentication.tokening import headers

class InventoryManager:
    """Manages inventory operations for an account."""
    
    # Class variable (shared by all instances)
    base_url = "https://api.deliverect.io"
    
    def __init__(self, account_id):
        """Constructor - initialize instance."""
        self.account_id = account_id
        self.inventory = []
        self.items = []
        self.lookup_set = None
    
    # Instance Methods
    def fetch_inventory(self):
        """Fetch all inventory for this account."""
        page = 1
        self.inventory = []
        while True:
            url = f"{self.base_url}/catalog/accounts/{self.account_id}/inventory"
            payload = {"sort": "-_id", "max_results": 50, "locations": [], "page": page}
            response = requests.post(url, headers=headers, json=payload)
            items = response.json().get("_items", [])
            if not items:
                break
            self.inventory.extend(items)
            page += 1
        return self.inventory
    
    def fetch_items(self):
        """Fetch all catalog items for this account."""
        page = 1
        self.items = []
        while True:
            url = f"{self.base_url}/catalog/accounts/{self.account_id}/items"
            payload = {"visible": True, "max_results": 500, "sort": "-_id", "page": page}
            response = requests.post(url, headers=headers, json=payload)
            items = response.json().get("_items", [])
            if not items:
                break
            for item in items:
                self.items.append({"plu": item.get("plu"), "name": item.get("name")})
            page += 1
        return self.items
    
    def build_lookup(self):
        """Build lookup set for fast checking."""
        self.lookup_set = self._build_lookup_set(self.inventory)
        return self.lookup_set
    
    def has_item(self, plu, location):
        """Check if item exists in inventory."""
        if not self.lookup_set:
            self.build_lookup()
        return (plu, location) in self.lookup_set if plu else False
    
    def get_missing_items(self, location_id):
        """Get items missing from inventory for a location."""
        if not self.inventory:
            self.fetch_inventory()
        if not self.items:
            self.fetch_items()
        if not self.lookup_set:
            self.build_lookup()
        
        missing = []
        for item in self.items:
            plu = item.get("plu")
            if plu and not self.has_item(plu, location_id):
                missing.append(item)
        return missing
    
    # Private method (convention: starts with _)
    def _build_lookup_set(self, inventory):
        """Internal helper method."""
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
    
    # Class Method
    @classmethod
    def from_account_name(cls, account_name):
        """Alternative constructor - create from account name."""
        url = f"{cls.base_url}/accounts"
        response = requests.get(url, headers=headers)
        accounts = response.json().get("_items", [])
        for account in accounts:
            if account.get("name") == account_name:
                return cls(account.get("_id"))
        raise ValueError(f"Account '{account_name}' not found")
    
    # Static Method
    @staticmethod
    def format_csv_filename(account_name, location_name):
        """Utility function to format CSV filename."""
        safe_account = "".join(c for c in account_name if c.isalnum() or c in (' ', '-', '_'))
        safe_location = "".join(c for c in location_name if c.isalnum() or c in (' ', '-', '_'))
        return f"missingInventory_{safe_account}_{safe_location}.csv"

# Usage Examples:

# Create instance normally:
manager = InventoryManager("6929b2df534c927a631cd6b1")

# Or use class method:
manager = InventoryManager.from_account_name("SPAR Nederland")

# Use instance methods:
manager.fetch_inventory()
manager.fetch_items()
missing = manager.get_missing_items("692a0a9459950498df806400")

# Use static method (doesn't need instance):
filename = InventoryManager.format_csv_filename("SPAR", "Store A")
```

## Properties (Advanced)

Properties let you access methods like attributes:

```python
class LocationManager:
    def __init__(self, location_id):
        self._location_id = location_id
        self._name = None  # Cache
    
    @property
    def name(self):
        """Access like: location.name (not location.name())"""
        if self._name is None:
            url = f"https://api.deliverect.io/locations/{self._location_id}"
            response = requests.get(url, headers=headers)
            self._name = response.json().get("name")
        return self._name
    
    @property
    def account_id(self):
        """Get account ID from location."""
        url = f"https://api.deliverect.io/locations/{self._location_id}"
        response = requests.get(url, headers=headers)
        return response.json().get("account")

# Usage:
location = LocationManager("692a0a9459950498df806400")
print(location.name)  # No parentheses! Like an attribute
print(location.account_id)  # Also like an attribute
```

## Inheritance (Advanced)

Create a base class and extend it:

```python
class BaseAPIManager:
    """Base class with common functionality."""
    
    def __init__(self, account_id):
        self.account_id = account_id
        self.base_url = "https://api.deliverect.io"
        from authentication.tokening import headers
        self.headers = headers
    
    def make_request(self, endpoint, method="GET", **kwargs):
        """Common request method."""
        url = f"{self.base_url}/{endpoint}"
        if method == "GET":
            return requests.get(url, headers=self.headers, **kwargs)
        elif method == "POST":
            return requests.post(url, headers=self.headers, **kwargs)

class InventoryManager(BaseAPIManager):
    """Extends BaseAPIManager."""
    
    def __init__(self, account_id):
        super().__init__(account_id)  # Call parent constructor
        self.inventory = []
    
    def fetch_inventory(self):
        """Uses parent's make_request method."""
        response = self.make_request(
            f"catalog/accounts/{self.account_id}/inventory",
            method="POST",
            json={"sort": "-_id", "max_results": 50}
        )
        self.inventory = response.json().get("_items", [])
        return self.inventory

# Usage:
manager = InventoryManager("6929b2df534c927a631cd6b1")
manager.fetch_inventory()  # Uses both parent and child methods
```

## When to Use Classes

### ✅ Use Classes When:
- You have related data and functions that work together
- You want to organize code better
- You need to maintain state (like cached data)
- You have multiple instances with different data

### ❌ Don't Use Classes When:
- You just have a few standalone functions
- No shared state needed
- Simple utility functions

## Quick Reference

```python
class MyClass:
    class_var = "shared"  # Class variable
    
    def __init__(self, param):
        self.instance_var = param  # Instance variable
    
    def instance_method(self):
        """Works with self - most common."""
        return self.instance_var
    
    @classmethod
    def class_method(cls):
        """Works with class - for factories."""
        return cls.class_var
    
    @staticmethod
    def static_method():
        """Just a function in the class."""
        return "utility"
    
    @property
    def property_method(self):
        """Access like attribute."""
        return self.instance_var

# Usage:
obj = MyClass("value")
obj.instance_method()      # Instance method
MyClass.class_method()      # Class method
MyClass.static_method()     # Static method
obj.property_method         # Property (no parentheses!)
```

## Summary

1. **Class** = Blueprint for objects
2. **Instance Method** = Works with specific object (`self`)
3. **Class Method** = Works with class (`cls`), for factories
4. **Static Method** = Just a function in the class (no `self` or `cls`)
5. **Property** = Method accessed like attribute
6. **Inheritance** = Extend base classes

**Most common:** Instance methods with `self`!

