# Why Not Use Simple Dict `{"plu": "location"}`?

## The Problem

You're asking: Why not use `{"123": "abc"}` instead of `{("123", "abc")}`?

**Answer:** Because a dictionary can only store **ONE value per key**!

## The Issue: Multiple Locations Per PLU

In our inventory, **one PLU can exist at MULTIPLE locations**:

```python
# Real inventory data:
inventory = [
    {
        "plu": "123",
        "locations": [
            {"location": "abc"},  # PLU 123 at location abc
            {"location": "def"}   # PLU 123 at location def
        ]
    },
    {
        "plu": "456", 
        "locations": [
            {"location": "abc"}   # PLU 456 at location abc
        ]
    }
]
```

## What Happens with Simple Dict

### ❌ Simple Dict Approach (Doesn't Work)
```python
lookup = {}
lookup["123"] = "abc"  # PLU 123 → location abc
lookup["123"] = "def"  # PLU 123 → location def (OVERWRITES previous!)
# Now lookup["123"] = "def" - we LOST "abc"!

# Check:
if lookup.get("123") == "abc":  # False! We lost this
    print("Found!")
```

**Problem:** When you assign `lookup["123"] = "def"`, it **overwrites** the previous value `"abc"`. You can only store ONE location per PLU!

### ✅ Set of Tuples (What We Use - Works!)
```python
lookup = set()
lookup.add(("123", "abc"))  # PLU 123 at location abc
lookup.add(("123", "def"))   # PLU 123 at location def (BOTH stored!)
# Now lookup = {("123", "abc"), ("123", "def")}

# Check:
if ("123", "abc") in lookup:  # True! Both combinations exist
    print("Found!")
```

**Solution:** Each `(plu, location)` combination is unique, so we can store multiple locations for the same PLU!

## Visual Comparison

### Simple Dict (Broken):
```
PLU "123" → location "abc"  ✅ Stored
PLU "123" → location "def"  ❌ OVERWRITES "abc"!

Result: Only "def" remains, "abc" is lost!
```

### Set of Tuples (Works):
```
(PLU "123", location "abc")  ✅ Stored
(PLU "123", location "def")  ✅ Stored (separate entry!)

Result: Both combinations exist!
```

## Real Example

Let's say you have:
- Product "Coca Cola" (PLU: "123") at Store A (location: "abc")
- Product "Coca Cola" (PLU: "123") at Store B (location: "def")

### With Simple Dict:
```python
lookup = {}
lookup["123"] = "abc"  # Store A
lookup["123"] = "def"  # Store B (OVERWRITES Store A!)

# Check if it exists at Store A:
if lookup.get("123") == "abc":  # False! We lost this
    print("Exists at Store A")
```

**Result:** We can't check if it exists at Store A anymore because Store B overwrote it!

### With Set of Tuples:
```python
lookup = set()
lookup.add(("123", "abc"))  # Store A
lookup.add(("123", "def"))  # Store B (separate entry!)

# Check if it exists at Store A:
if ("123", "abc") in lookup:  # True!
    print("Exists at Store A")

# Check if it exists at Store B:
if ("123", "def") in lookup:  # True!
    print("Exists at Store B")
```

**Result:** We can check BOTH locations independently!

## Alternative: Dict with List Values

If you really wanted to use a dict, you'd need:

```python
lookup = {}
lookup["123"] = ["abc", "def"]  # List of locations for this PLU

# Check:
if "abc" in lookup.get("123", []):  # Works, but more complex
    print("Found!")
```

**But this is:**
- More complex to check
- Less efficient (need to search through list)
- Still O(1) for dict lookup, but O(n) for list search

## Why Tuple in Set is Best

```python
lookup = {("123", "abc"), ("123", "def")}

# Check: O(1) - direct lookup
if ("123", "abc") in lookup:  # Instant!
    print("Found!")
```

**Benefits:**
1. ✅ Stores multiple locations per PLU
2. ✅ O(1) lookup (fast!)
3. ✅ Simple to check
4. ✅ Memory efficient

## Summary

| Approach | Can Store Multiple Locations? | Lookup Speed |
|----------|------------------------------|--------------|
| `{"plu": "location"}` | ❌ No (overwrites) | O(1) |
| `{"plu": ["loc1", "loc2"]}` | ✅ Yes | O(1) dict + O(n) list search |
| `{("plu", "location")}` | ✅ Yes | O(1) |

**Winner:** Set of tuples - simple, fast, handles multiple locations!

## The Key Insight

**Dictionary keys must be unique.** If you use PLU as the key, you can only have ONE location per PLU.

**But we need:** Multiple locations per PLU!

**Solution:** Use the COMBINATION `(plu, location)` as the key (in a set), so each combination is unique!

