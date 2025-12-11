import sys
from pathlib import Path
# Add project root to Python path (must be before project imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.api_helpers import extractAllProductIdsFromCategories, getAllCategoriesPerCatalog, getAccountIdfromCatalogId
from catImporter.csvToCatalog import getAllProducts

catalogId = "TESTCAT"


product_ids = extractAllProductIdsFromCategories(getAllCategoriesPerCatalog(catalogId))

accountId = getAccountIdfromCatalogId(catalogId)
allProducts = getAllProducts(accountId)
print(f"Found {len(product_ids)} products across all categories")
print(f"Found {len(allProducts)} products in the account")
productsNotInMenu = []
for product in allProducts:
    if product.get("_id") not in product_ids:
        productsNotInMenu.append(product)
print(f"Found {len(productsNotInMenu)} products not in the menu")
# for product in productsNotInMenu:
#     print(product.get("name"), product.get("plu"))