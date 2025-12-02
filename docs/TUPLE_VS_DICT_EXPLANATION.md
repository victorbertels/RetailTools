# Tuple in Set vs Dictionary: Which is Better?

## The Question

In our optimization, we used:
```python
lookup = set()
lookup.add((plu, location))  # Set of tuples
# Check: (plu, loc) in lookup
```

Could we use a dictionary instead?
```python
lookup = {}
lookup[(plu, location)] = True  # Dictionary with tuple keys
# Check: (plu, loc) in lookup
```

## Short Answer

**Both work!** Both are O(1) lookup time. But for our use case (just checking existence), **set is slightly better**.

## Detailed Comparison

### Option 1: Set of Tuples (What We Used)
```python
def buildInventoryLookup(inventory: list):
    lookup = set()
    for item in inventory:
        plu = item.get("plu")
        if plu:
            locations = item.get("locations", [])
            for loc_obj in locations:
                location_id = loc_obj.get("location")
                if location_id:
                    lookup.add((plu, location_id))  # Just the tuple
    return lookup

# Usage:
if (plu, loc) in lookup:  # O(1) - checks membership
    print("Exists!")
```

**Pros:**
- ✅ Slightly less memory (no values stored)
- ✅ Semantically clear - we're checking membership
- ✅ O(1) average case lookup
- ✅ Pythonic for "does this exist?" questions

**Cons:**
- ❌ Can't store additional data (but we don't need to!)

### Option 2: Dictionary with Tuple Keys
```python
def buildInventoryLookup(inventory: list):
    lookup = {}
    for item in inventory:
        plu = item.get("plu")
        if plu:
            locations = item.get("locations", [])
            for loc_obj in locations:
                location_id = loc_obj.get("location")
                if location_id:
                    lookup[(plu, location_id)] = True  # Tuple as key, True as value
    return lookup

# Usage:
if (plu, loc) in lookup:  # O(1) - checks if key exists
    print("Exists!")
```

**Pros:**
- ✅ O(1) average case lookup (same as set!)
- ✅ Could store additional data if needed later
- ✅ Works perfectly fine

**Cons:**
- ❌ Slightly more memory (stores True values)
- ❌ Less semantically clear (we're not really storing data)

### Option 3: Nested Dictionary
```python
def buildInventoryLookup(inventory: list):
    lookup = {}
    for item in inventory:
        plu = item.get("plu")
        if plu:
            locations = item.get("locations", [])
            for loc_obj in locations:
                location_id = loc_obj.get("location")
                if location_id:
                    if plu not in lookup:
                        lookup[plu] = {}
                    lookup[plu][location_id] = True
    return lookup

# Usage:
if lookup.get(plu, {}).get(loc):  # O(1) - nested lookup
    print("Exists!")
```

**Pros:**
- ✅ Could look up all locations for a PLU easily
- ✅ O(1) average case

**Cons:**
- ❌ More complex structure
- ❌ More memory overhead
- ❌ Slightly slower (two lookups instead of one)

## Performance Comparison

### Time Complexity
All three are **O(1) average case** for lookups:
- Set: `(plu, loc) in set` → O(1)
- Dict: `(plu, loc) in dict` → O(1)  
- Nested Dict: `dict.get(plu, {}).get(loc)` → O(1)

### Memory Usage
```python
# Set of tuples (what we used)
lookup = {(plu1, loc1), (plu2, loc2), ...}  
# Memory: Just the tuples

# Dictionary
lookup = {(plu1, loc1): True, (plu2, loc2): True, ...}
# Memory: Tuples + True values (slightly more)

# Nested dictionary
lookup = {plu1: {loc1: True, loc2: True}, plu2: {loc1: True}, ...}
# Memory: More overhead with nested structure
```

**Set wins** for memory (but difference is tiny).

## Real-World Test

Let me show you a quick benchmark:

```python
import time

# Test data
items = [(f"plu{i}", f"loc{j}") for i in range(1000) for j in range(10)]
# 10,000 combinations

# Set approach
start = time.time()
lookup_set = set(items)
for item in items[:100]:
    _ = item in lookup_set
time_set = time.time() - start

# Dict approach
start = time.time()
lookup_dict = {item: True for item in items}
for item in items[:100]:
    _ = item in lookup_dict
time_dict = time.time() - start

print(f"Set: {time_set:.6f}s")
print(f"Dict: {time_dict:.6f}s")
# Result: They're basically the same! (within microseconds)
```

**Result:** Performance is essentially identical. The difference is negligible.

## When to Use Each

### Use **Set** when:
- ✅ You only need to check existence
- ✅ You don't need to store associated data
- ✅ You want the most memory-efficient option
- ✅ **This is our case!**

### Use **Dictionary** when:
- ✅ You need to store associated data
- ✅ You might want to update values later
- ✅ You want to count occurrences: `lookup[(plu, loc)] += 1`

### Use **Nested Dictionary** when:
- ✅ You need to look up all locations for a PLU
- ✅ You need hierarchical access: `lookup[plu][loc]`

## Our Use Case

We're just checking: **"Does this (plu, location) combination exist?"**

We don't need to:
- Store additional data
- Count occurrences
- Look up all locations for a PLU

So **set is perfect** for our needs!

## Could We Use a Dict? 

**Yes, absolutely!** It would work fine:

```python
# This would work just as well:
def buildInventoryLookup(inventory: list):
    lookup = {}  # Dict instead of set
    for item in inventory:
        plu = item.get("plu")
        if plu:
            locations = item.get("locations", [])
            for loc_obj in locations:
                location_id = loc_obj.get("location")
                if location_id:
                    lookup[(plu, location_id)] = True  # Store True
    return lookup

# Usage:
if (plu, loc) in lookup:  # Works the same!
    # Found it
```

**Performance:** Same O(1) lookup
**Memory:** Slightly more (stores True values), but negligible
**Clarity:** Set is clearer for "existence checking"

## Conclusion

**Both work!** For our specific use case (just checking existence), **set is slightly better** because:
1. More memory efficient (no values stored)
2. More semantically clear (membership test)
3. Same performance

But if you prefer dictionaries or need to store data later, **dictionary works perfectly fine too!**

The performance difference is so small it's not worth worrying about. Choose based on:
- **Set**: "Does this exist?" (our case)
- **Dict**: "Does this exist AND I might store data?"

