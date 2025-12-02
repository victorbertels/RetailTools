# Understanding `yield` in Python

## What is `yield`?

`yield` creates a **generator function** - a function that can produce multiple values one at a time, instead of returning everything at once.

## `return` vs `yield`

### Using `return` (normal function):
```python
def get_all_items():
    all_items = []
    for page in range(1, 4):
        items = fetch_page(page)  # [item1, item2, item3]
        all_items.extend(items)
    return all_items  # Returns everything at once: [item1, item2, item3, item4, item5, item6, ...]

# Usage:
items = get_all_items()  # Waits for ALL pages, then returns everything
```

**Problem:** You have to wait for ALL pages before getting any results. Uses more memory.

### Using `yield` (generator function):
```python
def get_all_items():
    for page in range(1, 4):
        items = fetch_page(page)  # [item1, item2, item3]
        yield items  # Give you this page's items NOW, then pause

# Usage:
for page_items in get_all_items():  # Gets items page by page
    print(page_items)  # Process each page as it arrives
```

**Benefit:** You get results page by page, immediately. Uses less memory.

## How `yield` Works in `paginate_api`

```python
def paginate_api(url: str, items_key: str = "_items", max_results: int = 500, **kwargs):
    page = 1
    while True:
        # ... fetch page ...
        items = data.get(items_key, [])
        if not items:
            break
            
        yield items  # ← Give you THIS page's items, then pause
        page += 1    # ← Resume here when you ask for next page
```

### What happens:

1. **First call:** Function starts, fetches page 1, `yield items` → gives you page 1 items, **pauses**
2. **Second call:** Function **resumes** from `page += 1`, fetches page 2, `yield items` → gives you page 2 items, **pauses**
3. **Continues** until no more items

## Usage Examples

### Example 1: Process pages one at a time
```python
from utils import paginate_api

# Get items page by page
for page_items in paginate_api("https://api.deliverect.io/locations", where={"account": "123"}):
    print(f"Got {len(page_items)} items on this page")
    # Process this page immediately, don't wait for all pages
    for item in page_items:
        process_item(item)
```

### Example 2: Collect all items (if needed)
```python
from utils import paginate_api

# Collect all pages into one list
all_items = []
for page_items in paginate_api("https://api.deliverect.io/locations"):
    all_items.extend(page_items)

print(f"Total: {len(all_items)} items")
```

### Example 3: Stop early (memory efficient!)
```python
from utils import paginate_api

# Stop after finding what you need
for page_items in paginate_api("https://api.deliverect.io/locations"):
    for item in page_items:
        if item.get("name") == "Target Location":
            print("Found it!")
            break  # Stops fetching more pages - saves time and memory!
```

## Memory Comparison

### With `return` (collects everything):
```
Page 1: [100 items] → stored in memory
Page 2: [100 items] → stored in memory  
Page 3: [100 items] → stored in memory
Total: 300 items in memory at once
```

### With `yield` (one page at a time):
```
Page 1: [100 items] → process → free memory
Page 2: [100 items] → process → free memory
Page 3: [100 items] → process → free memory
Total: Only 100 items in memory at any time
```

## Real-World Analogy

**`return`** = A restaurant that makes ALL dishes, then brings everything to your table at once
- You wait a long time
- Table is crowded with all dishes

**`yield`** = A restaurant that brings dishes one at a time as they're ready
- You start eating immediately
- Table stays clean, one dish at a time

## Key Takeaways

1. **`yield` creates a generator** - produces values one at a time
2. **Function pauses** after each `yield`, resumes when you ask for next value
3. **Memory efficient** - only holds one page/result in memory at a time
4. **Lazy evaluation** - only fetches what you need, when you need it
5. **Use with `for` loops** - iterate over the generator to get values

## When to Use `yield`

✅ **Use `yield` when:**
- Processing large datasets
- Paginating through API results
- Reading large files line by line
- You want to process items as they arrive
- Memory is a concern

❌ **Use `return` when:**
- You need all results at once
- Small datasets
- Simple functions that return one value

