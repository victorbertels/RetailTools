# Optimization Explanation: Lookup Set vs Nested Loops

## The Problem

We need to check if a product (identified by PLU) exists in inventory for a specific location.

**Original Data Structure:**
- `inventory`: List of inventory items, each with a `plu` and a `locations` array
- `items`: List of catalog items (products) with `plu` and `name`
- We need to check: "Does this PLU exist in inventory for this location?"

---

## ❌ OLD APPROACH: Nested Loops (SLOW)

### How It Worked

```python
def hasInventory(inventory: list, plu: str, location: str):
    # For EACH inventory item
    for item in inventory:
        if item.get("plu") == plu:
            locations = item.get("locations", [])
            # For EACH location in that item
            for loc_obj in locations:
                if loc_obj.get("location") == location:
                    return True
    return False

def getMissingInventory(account: str, location: str = None):
    inventory = getInventory(account)  # 1000 items
    items = getItems(account)          # 500 items
    locations = getAllLocations(account)  # 50 locations
    
    missing_per_location = {}
    for loc in locations:  # Loop 1: 50 iterations
        missing_inventory = []
        for item in items:  # Loop 2: 500 iterations
            # This calls hasInventory which does nested loops!
            if not hasInventory(inventory, item.get("plu"), loc):
                missing_inventory.append(item)
        # ... store results
```

### Time Complexity

**For each location:**
- Loop through all items (500 items)
- For each item, call `hasInventory()` which:
  - Loops through all inventory items (1000 items)
  - For each inventory item, loops through its locations (average 5 locations)

**Total operations:**
- Locations: 50
- Items per location check: 500
- Inventory items to search: 1000
- Locations per inventory item: ~5

**Worst case: 50 × 500 × 1000 × 5 = 125,000,000 operations!**

**Time Complexity: O(locations × items × inventory × avg_locations_per_item)**

---

## ✅ NEW APPROACH: Lookup Set (FAST)

### How It Works

```python
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
                    # Create a tuple (plu, location) and add to set
                    lookup.add((plu, location_id))
    return lookup

def getMissingInventory(account: str, location: str = None):
    inventory = getInventory(account)  # 1000 items
    items = getItems(account)          # 500 items
    
    # Build lookup set ONCE - O(inventory × avg_locations)
    inventory_lookup = buildInventoryLookup(inventory)
    # This creates a set like: {("123", "loc1"), ("123", "loc2"), ("456", "loc1"), ...}
    
    if location is None:
        locations = getAllLocations(account)  # 50 locations
        missing_per_location = {}
        for loc in locations:  # Loop 1: 50 iterations
            missing_inventory = []
            for item in items:  # Loop 2: 500 iterations
                plu = item.get("plu")
                # O(1) lookup - just check if tuple exists in set!
                if plu and (plu, loc) not in inventory_lookup:
                    missing_inventory.append(item)
            # ... store results
```

### Time Complexity

**Step 1: Build lookup set**
- Loop through inventory once: 1000 items
- For each item, loop through locations: ~5 locations
- **Total: 1000 × 5 = 5,000 operations**

**Step 2: Check for missing items**
- For each location: 50 locations
- For each item: 500 items
- Each check is O(1) set lookup (instant!)
- **Total: 50 × 500 = 25,000 operations**

**Total operations: 5,000 + 25,000 = 30,000 operations**

**Time Complexity: O(inventory × avg_locations + locations × items)**

---

## 📊 Performance Comparison

| Approach | Operations | Time Complexity |
|----------|-----------|-----------------|
| **Old (Nested Loops)** | ~125,000,000 | O(locations × items × inventory × avg_locations) |
| **New (Lookup Set)** | ~30,000 | O(inventory × avg_locations + locations × items) |
| **Speedup** | **~4,167x faster!** | |

---

## 🔑 Key Concepts

### 1. What is a Set?

A Python `set` is like a dictionary but only stores keys (no values). It's optimized for:
- **Fast membership testing**: `item in set` is O(1) average case
- **No duplicates**: Each item appears only once

```python
# Example
my_set = {("123", "loc1"), ("456", "loc2")}
print(("123", "loc1") in my_set)  # True - O(1) lookup
print(("999", "loc1") in my_set)  # False - O(1) lookup
```

### 2. Why Tuples?

We use tuples `(plu, location)` because:
- Tuples are **hashable** (can be used as set elements)
- They represent a **unique combination** of PLU and location
- Easy to check: `(plu, loc) in lookup_set`

### 3. The Magic: O(1) Lookup

**Old way:**
```python
# Had to search through entire inventory list
for item in inventory:  # O(n) - linear search
    if item.get("plu") == plu:
        # ... more searching
```

**New way:**
```python
# Direct lookup in set - instant!
if (plu, loc) in inventory_lookup:  # O(1) - constant time
    # Found it!
```

---

## 💡 Real-World Analogy

**Old Approach (Nested Loops):**
Imagine you have a phone book and want to find if "John Smith" exists:
- You read through every page (inventory items)
- On each page, check every name (locations)
- Repeat for every person you're looking for (items × locations)

**New Approach (Lookup Set):**
Imagine you create an index card system:
- Build the index once: Write down every name and where it appears
- When checking: Just look up the name in your index - instant!
- The index lookup is like a dictionary - you know exactly where to find it

---

## 🎯 Summary

**What changed:**
1. **Built a lookup structure once** (set of tuples)
2. **Replaced nested loops** with simple set membership checks
3. **Reduced complexity** from O(n³) to O(n²)

**Why it's faster:**
- Sets use hash tables internally - direct lookups are O(1)
- We only build the lookup once, not for every check
- No more searching through entire lists repeatedly

**Result:**
- **4,000+ times faster** for large datasets
- Scales much better as data grows
- Comparison step is now nearly instant!

