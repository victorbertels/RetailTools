"""
Example demonstrating the optimization: Lookup Set vs Nested Loops

This file shows both approaches side-by-side with example data.
"""

# Example data structure (simplified)
inventory = [
    {
        "plu": "123",
        "locations": [
            {"location": "loc1", "product": "prod1"},
            {"location": "loc2", "product": "prod2"}
        ]
    },
    {
        "plu": "456",
        "locations": [
            {"location": "loc1", "product": "prod3"}
        ]
    },
    {
        "plu": "789",
        "locations": [
            {"location": "loc2", "product": "prod4"}
        ]
    }
]

items = [
    {"plu": "123", "name": "Product A"},
    {"plu": "456", "name": "Product B"},
    {"plu": "999", "name": "Product C"},  # Missing from inventory
    {"plu": "888", "name": "Product D"}   # Missing from inventory
]

locations = ["loc1", "loc2"]


# ============================================================================
# ❌ OLD APPROACH: Nested Loops (SLOW)
# ============================================================================

def hasInventory_OLD(inventory: list, plu: str, location: str):
    """
    OLD: Check if PLU exists in inventory for location using nested loops.
    
    Time Complexity: O(inventory_items × avg_locations_per_item)
    For each check, we loop through ALL inventory items!
    """
    for item in inventory:
        if item.get("plu") == plu:
            locations_list = item.get("locations", [])
            for loc_obj in locations_list:
                if loc_obj.get("location") == location:
                    return True
    return False


def findMissing_OLD(inventory: list, items: list, locations: list):
    """
    OLD: Find missing inventory using nested loops.
    
    Time Complexity: O(locations × items × inventory × avg_locations)
    This is VERY slow for large datasets!
    """
    missing_per_location = {}
    
    for loc in locations:
        missing_items = []
        for item in items:
            plu = item.get("plu")
            # This calls hasInventory_OLD which does nested loops!
            # For 50 locations × 500 items × 1000 inventory = 25,000,000 operations!
            if not hasInventory_OLD(inventory, plu, loc):
                missing_items.append(item)
        
        if missing_items:
            missing_per_location[loc] = missing_items
    
    return missing_per_location


# ============================================================================
# ✅ NEW APPROACH: Lookup Set (FAST)
# ============================================================================

def buildInventoryLookup(inventory: list):
    """
    NEW: Build a lookup set once for O(1) checks.
    
    Creates a set of (plu, location) tuples.
    Time Complexity: O(inventory_items × avg_locations_per_item)
    But we only do this ONCE!
    """
    lookup = set()
    for item in inventory:
        plu = item.get("plu")
        if plu:
            locations_list = item.get("locations", [])
            for loc_obj in locations_list:
                location_id = loc_obj.get("location")
                if location_id:
                    # Add tuple to set for fast lookup
                    lookup.add((plu, location_id))
    return lookup


def findMissing_NEW(inventory: list, items: list, locations: list):
    """
    NEW: Find missing inventory using lookup set.
    
    Time Complexity: O(inventory × avg_locations + locations × items)
    Much faster! The lookup is O(1) instead of O(n)
    """
    # Build lookup set ONCE
    inventory_lookup = buildInventoryLookup(inventory)
    # Result: {("123", "loc1"), ("123", "loc2"), ("456", "loc1"), ("789", "loc2")}
    
    missing_per_location = {}
    
    for loc in locations:
        missing_items = []
        for item in items:
            plu = item.get("plu")
            # O(1) lookup - just check if tuple exists in set!
            # This is INSTANT compared to nested loops
            if plu and (plu, loc) not in inventory_lookup:
                missing_items.append(item)
        
        if missing_items:
            missing_per_location[loc] = missing_items
    
    return missing_per_location


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OPTIMIZATION DEMONSTRATION")
    print("=" * 70)
    
    print("\n📦 Example Inventory:")
    print(f"  - {len(inventory)} inventory items")
    print(f"  - {len(items)} catalog items")
    print(f"  - {len(locations)} locations")
    
    print("\n" + "=" * 70)
    print("❌ OLD APPROACH: Nested Loops")
    print("=" * 70)
    
    import time
    
    # Time the OLD approach
    start = time.time()
    missing_old = findMissing_OLD(inventory, items, locations)
    time_old = time.time() - start
    
    print(f"\n⏱️  Time taken: {time_old:.6f} seconds")
    print(f"\n📋 Missing items per location:")
    for loc, missing in missing_old.items():
        print(f"  {loc}: {[item['name'] for item in missing]}")
    
    print("\n" + "=" * 70)
    print("✅ NEW APPROACH: Lookup Set")
    print("=" * 70)
    
    # Time the NEW approach
    start = time.time()
    missing_new = findMissing_NEW(inventory, items, locations)
    time_new = time.time() - start
    
    print(f"\n⏱️  Time taken: {time_new:.6f} seconds")
    print(f"\n📋 Missing items per location:")
    for loc, missing in missing_new.items():
        print(f"  {loc}: {[item['name'] for item in missing]}")
    
    print("\n" + "=" * 70)
    print("📊 COMPARISON")
    print("=" * 70)
    
    print(f"\n✅ Results match: {missing_old == missing_new}")
    
    if time_old > 0:
        speedup = time_old / time_new if time_new > 0 else float('inf')
        print(f"\n🚀 Speedup: {speedup:.2f}x faster")
        print(f"   (Note: For small datasets, the difference is minimal.")
        print(f"    For large datasets with 1000s of items, the speedup is HUGE!)")
    
    print("\n" + "=" * 70)
    print("💡 KEY INSIGHT")
    print("=" * 70)
    print("""
    The lookup set approach:
    1. Builds the lookup structure ONCE (O(n))
    2. Uses O(1) set lookups instead of O(n) linear searches
    3. Reduces total complexity from O(n³) to O(n²)
    
    For 50 locations × 500 items × 1000 inventory:
    - OLD: ~125,000,000 operations
    - NEW: ~30,000 operations
    - Speedup: ~4,000x faster!
    """)

