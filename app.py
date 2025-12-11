import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

st.set_page_config(
    page_title="Retail Tools Dashboard",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main navigation
st.sidebar.title("🛠️ Retail Tools")
st.sidebar.markdown("---")

# Navigation options
page = st.sidebar.radio(
    "Select a tool:",
    [
        "📦 Catalog Importer",
        "📊 Count Items in Menu",
        "😴 Snooze History",
        "🔍 Missing Inventory",
        "🔎 Find Items Not in Menu",
        "🚗 Uber Address Scraper"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Make sure the account is linked to the developer account ID: `690ca201b9c6f85ca05b6eb1`"
)

# Route to the selected page
if page == "📦 Catalog Importer":
    # Import catalog importer functions from catImporter
    sys.path.insert(0, str(project_root / "catImporter"))
    import os
    import tempfile
    import time
    import requests
    from authentication.tokening import getToken, getHeaders
    
    # Import functions from catImporter
    import importlib
    csvToCatalog = importlib.import_module("csvToCatalog")
    readCsv = csvToCatalog.readCsv
    createStructure = csvToCatalog.createStructure
    createCatalog = csvToCatalog.createCatalog
    getAccountName = csvToCatalog.getAccountName
    createCategories = csvToCatalog.createCategories
    createSubCategories = csvToCatalog.createSubCategories
    getAllProducts = csvToCatalog.getAllProducts
    findProductIdbyPlu = csvToCatalog.findProductIdbyPlu
    getEtag = csvToCatalog.getEtag
    patchSubCategory = csvToCatalog.patchSubCategory
    
    # Developer account ID
    DEVELOPER_ACCOUNT_ID = "690ca201b9c6f85ca05b6eb1"
    
    def checkAccountAccess(accountId):
        """Check if we can access the account"""
        try:
            account_name = getAccountName(accountId)
            return True, account_name
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                return False, None
            raise
        except Exception as e:
            return False, None
    
    st.title("📦 Catalog Importer")
    st.markdown("Upload a csv and I will create a catalog structure for you.")
    st.markdown("This assumes the products you want to add in there already exist in the account, this will not create new items.")
    st.markdown("This only makes nested category menu structures, so we expect values on Category 2.")
    st.markdown("Expected headers in the CSV file: **Category 1, Category 2, Plu**")
    
    # Download template CSV
    template_path = project_root / "catImporter" / "template.csv"
    try:
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as template_file:
                template_data = template_file.read()
                st.download_button(
                    label="📥 Download CSV Template",
                    data=template_data,
                    file_name="catalog_template.csv",
                    mime="text/csv",
                    help="Download a template CSV file to see the expected structure with example data"
                )
        else:
            st.warning("Template CSV file not found")
    except Exception as e:
        st.error(f"Error loading template: {str(e)}")
    
    st.markdown("---")
    
    # Input fields
    account_id = st.text_input(
        "Account ID",
        placeholder="Enter your Deliverect account ID",
        help="Your Deliverect account ID"
    )
    
    menu_name = st.text_input(
        "Catalog Name",
        placeholder="Enter catalog/menu name",
        help="Name for the new catalog/menu"
    )
    
    csv_file = st.file_uploader(
        "Upload CSV File",
        type=['csv'],
        help="Upload your catalog structure CSV file with Category 1, Category 2, and Plu columns"
    )
    
    # Check account access when account ID is provided
    if account_id:
        with st.spinner("Checking account access..."):
            has_access, account_name = checkAccountAccess(account_id)
        
        if not has_access:
            st.error("❌ Cannot access this account")
            st.warning(
                f"""
                **Account Access Required**
                
                This account is not linked to the developer account. Please link your account 
                to the developer account ID: `{DEVELOPER_ACCOUNT_ID}`
                """
            )
        else:
            st.success(f"✅ Importing for account: **{account_name}**")
    
    st.markdown("---")
    
    # Check if all fields are ready
    all_ready = account_id and menu_name and csv_file
    
    # Show status messages
    if not all_ready:
        if account_id and menu_name and not csv_file:
            st.info("👆 Please upload a CSV file to start the import")
        elif account_id and not menu_name:
            st.info("👆 Please enter a catalog name")
        elif not account_id:
            st.info("👆 Please enter your account ID")
    
    # Start import button - always visible, enabled only when ready
    if st.button("🚀 Start Import", type="primary", disabled=not all_ready):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(csv_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Create log area for detailed feedback
            st.markdown("### 📋 Import Log")
            log_placeholder = st.empty()
            log_messages = []
            
            def add_log(message):
                timestamp = time.strftime('%H:%M:%S')
                log_messages.append(f"[{timestamp}] {message}")
                # Display last 50 messages in a code block for better readability
                with log_placeholder.container():
                    st.code("\n".join(log_messages[-50:]), language=None)
            
            # Step 1: Read CSV
            status_text.text("📄 Reading CSV file...")
            add_log("📄 Reading CSV file...")
            rows = readCsv(tmp_path)
            progress_bar.progress(10)
            add_log(f"✓ Loaded {len(rows)} rows from CSV")
            st.success(f"✓ Loaded {len(rows)} rows from CSV")
            
            # Step 2: Create structure
            status_text.text("🔧 Building category structure...")
            add_log("🔧 Building category structure...")
            structure = createStructure(rows)
            progress_bar.progress(20)
            add_log(f"✓ Created structure with {len(structure)} main categories")
            st.success(f"✓ Created structure with {len(structure)} main categories")
            
            # Step 3: Create catalog
            status_text.text("📋 Creating catalog...")
            add_log(f"📋 Creating catalog: '{menu_name}'...")
            new_menu_id = createCatalog(account_id, menu_name)
            progress_bar.progress(30)
            add_log(f"✓ Created catalog: '{menu_name}'")
            st.success(f"✓ Created catalog: '{menu_name}'")
            
            # Step 4: Fetch products
            status_text.text("🛒 Fetching all products...")
            add_log("🛒 Fetching all products...")
            
            # Custom getAllProducts with logging
            all_products = []
            page = 1
            page_size = 500
            
            while True:
                payload = {
                    "page": page,
                    "visible": True,
                    "max_results": page_size,
                    "sort": "-_id"
                }
                resp = requests.post(f"https://api.deliverect.io/catalog/accounts/{account_id}/items", json=payload, headers=getHeaders()).json()
                
                items = resp.get("_items") if isinstance(resp, dict) else []
                if not items:
                    break
                
                all_products.extend(items)
                meta = resp.get("_meta", {}) if isinstance(resp, dict) else {}
                total_pages = meta.get("total_pages")
                current_page = meta.get("page")
                total = meta.get("total")
                
                # Show pagination progress
                log_msg = f"📦 Page {current_page}/{total_pages if total_pages else '?'} - {len(items)} items (Total so far: {len(all_products)})"
                add_log(log_msg)
                status_text.text(log_msg)
                
                if (total_pages and current_page and current_page >= total_pages) or len(items) < page_size:
                    break
                
                page += 1
            
            progress_bar.progress(50)
            add_log(f"✓ Loaded {len(all_products)} products total")
            st.success(f"✓ Loaded {len(all_products)} products")
            
            # Step 5: Process categories
            status_text.text("📂 Processing categories and subcategories...")
            add_log("📂 Processing categories and subcategories...")
            total_operations = sum(1 + len(cat2) for cat2 in structure.values())
            progress_increment = 40 / max(total_operations, 1)
            current_progress = 50
            
            results = {
                "categories_created": 0,
                "subcategories_created": 0,
                "products_added": 0,
                "errors": []
            }
            
            category_count = 0
            total_categories = len(structure)
            
            for category1_name, category2_dict in structure.items():
                category_count += 1
                try:
                    add_log(f"📁 [{category_count}/{total_categories}] Processing category: {category1_name}")
                    status_text.text(f"Processing category {category_count}/{total_categories}: {category1_name}")
                    new_category_id = createCategories(account_id, new_menu_id, category1_name)
                    results["categories_created"] += 1
                    add_log(f"  ✓ Created category: '{category1_name}'")
                    current_progress += progress_increment
                    progress_bar.progress(min(int(current_progress), 90))
                    
                    subcategory_count = 0
                    total_subcategories = len(category2_dict)
                    
                    for category2_name, plu_list in category2_dict.items():
                        subcategory_count += 1
                        try:
                            add_log(f"    [{subcategory_count}/{total_subcategories}] Processing subcategory: {category2_name}")
                            new_sub_category_id = createSubCategories(account_id, new_menu_id, new_category_id, category2_name)
                            results["subcategories_created"] += 1
                            add_log(f"    ✓ Created subcategory: '{category2_name}'")
                            
                            # Get etag for the subcategory
                            try:
                                etag = getEtag(new_sub_category_id)
                                add_log(f"      ✓ Retrieved etag for subcategory")
                            except Exception as etag_error:
                                error_msg = f"Failed to get etag for subcategory '{category2_name}': {str(etag_error)}"
                                add_log(f"      ❌ {error_msg}")
                                results["errors"].append(error_msg)
                                # Skip adding products if we can't get etag
                                current_progress += progress_increment
                                progress_bar.progress(min(int(current_progress), 90))
                                continue
                            
                            subProducts = []
                            added_product_ids = set()  # Track added product IDs to avoid duplicates
                            
                            add_log(f"      🔍 Looking up {len(plu_list)} PLUs...")
                            found_count = 0
                            for plu in plu_list:
                                product_id = findProductIdbyPlu(all_products, plu)
                                if product_id and product_id not in added_product_ids:
                                    subProducts.append(product_id)
                                    added_product_ids.add(product_id)
                                    found_count += 1
                            
                            # Remove duplicates as a safety measure (preserve order)
                            unique_subProducts = list(dict.fromkeys(subProducts))
                            
                            if unique_subProducts:
                                add_log(f"      ✓ Found {len(unique_subProducts)} unique products from {len(plu_list)} PLUs")
                                patchSubCategory(new_sub_category_id, unique_subProducts, etag)
                                results["products_added"] += len(unique_subProducts)
                                add_log(f"      ✓ Added {len(unique_subProducts)} unique products to subcategory")
                            else:
                                add_log(f"      ⚠ No products found for {len(plu_list)} PLUs")
                            
                            current_progress += progress_increment
                            progress_bar.progress(min(int(current_progress), 90))
                        except Exception as e:
                            error_msg = f"Error in subcategory '{category2_name}': {str(e)}"
                            add_log(f"      ❌ {error_msg}")
                            results["errors"].append(error_msg)
                except Exception as e:
                    error_msg = f"Error in category '{category1_name}': {str(e)}"
                    add_log(f"  ❌ {error_msg}")
                    results["errors"].append(error_msg)
            
            progress_bar.progress(100)
            status_text.text("✅ Import completed!")
            add_log("✅ Catalog import completed!")
            
            # Show results
            st.balloons()
            st.success("🎉 Catalog import completed successfully!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Categories Created", results["categories_created"])
            with col2:
                st.metric("Subcategories Created", results["subcategories_created"])
            with col3:
                st.metric("Products Added", results["products_added"])
            
            if results["errors"]:
                st.warning(f"⚠️ {len(results['errors'])} error(s) occurred:")
                for error in results["errors"]:
                    st.text(f"• {error}")
        
        except Exception as e:
            st.error(f"❌ Error during import: {str(e)}")
            st.exception(e)
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
elif page == "📊 Count Items in Menu":
    # Import count items functions
    sys.path.insert(0, str(project_root / "countItemsInMenu"))
    import streamlit as st
    import requests
    import pandas as pd
    import os
    from authentication.tokening import getToken, getHeaders
    
    # Import countItems functions (suppress linter warning - works at runtime)
    import importlib
    countItems = importlib.import_module("countItems")
    getLocationName = countItems.getLocationName
    getPreview = countItems.getPreview
    getLocationCount = countItems.getLocationCount
    isSnoozed = countItems.isSnoozed
    
    st.title("📊 Count Items in Menu")
    st.markdown("Analyze catalog items and their snooze status for a location.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account = st.text_input("Account ID", placeholder="Enter account ID")
        menu = st.text_input("Catalog ID", placeholder="Enter catalog ID")
    
    with col2:
        location_id = st.text_input("Location ID", placeholder="Enter location ID")
        channel = -1  # Default to all channels
    
    if st.button("🚀 Analyze catalog", type="primary"):
        if not all([account, menu]):
            st.error("Please fill in Account ID, Menu ID, and Location ID")
        else:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.container()
            
            try:
                # Step 1: Get location name
                status_text.text("🔍 Step 1/4: Getting location information...")
                progress_bar.progress(10)
                location_name = getLocationName(location_id)
                if not location_name:
                    location_name = "Unknown Location"
                status_text.text(f"✓ Location found: {location_name}")
                
                # Step 2: Fetching menu preview
                status_text.text("⏳ Step 2/4: Fetching menu preview from API (this may take a while)...")
                progress_bar.progress(25)
                
                # Build preview URL
                url = f"https://api.deliverect.io/menuPreview?account={account}&menu={menu}&location={location_id}&channel={channel}"
                
                # Get preview data with progress updates
                status_text.text("⏳ Fetching catalog data... have patience, large catalogs can take 30-60 seconds...")
                
                import time
                start_time = time.time()
                
                # Show a spinner with periodic updates
                result = None
                with log_container:
                    with st.spinner("⏳ Rendering catalog..."):
                        result = getPreview(url, location_name)
                
                elapsed_time = time.time() - start_time
                status_text.text(f"✓ Catalog data fetched in {elapsed_time:.1f} seconds")
                progress_bar.progress(50)
                
                if result:
                    # Step 3: Processing menu data
                    status_text.text("🔍 Step 3/4: Processing catalog structure...")
                    progress_bar.progress(60)
                    
                    total_items_count = result.get('total_items', 0)
                    snoozed_count = result.get('snoozed_items', 0)
                    total_all = total_items_count + snoozed_count
                    
                    status_text.text(f"✓ Found {total_all} total items ({total_items_count} active, {snoozed_count} snoozed)")
                    progress_bar.progress(80)
                    
                    # Step 4: Finalizing
                    status_text.text("✨ Step 4/4: Finalizing results...")
                    progress_bar.progress(90)
                    time.sleep(0.5)  # Brief pause to show completion
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    time.sleep(0.5)
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success(f"Analysis complete for: {location_name}")
                    
                    # Display summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Active Items", result['total_items'])
                    with col2:
                        st.metric("Snoozed Items", result['snoozed_items'])
                    with col3:
                        total = result['total_items'] + result['snoozed_items']
                        st.metric("Total Items", total)
                    with col4:
                        if total > 0:
                            percentage = (result['snoozed_items'] / total) * 100
                            st.metric("Snoozed %", f"{percentage:.1f}%")
                    
                    # Download complete Excel file with all tabs
                    st.markdown("---")
                    st.subheader("📊 Complete Report Download")
                    
                    # Create summary dataframe
                    total = result['total_items'] + result['snoozed_items']
                    percentage = (result['snoozed_items'] / total * 100) if total > 0 else 0
                    
                    summary_data = {
                        'Metric': ['Location', 'Total Items', 'Active Items', 'Snoozed Items', 'Snoozed Percentage'],
                        'Value': [
                            location_name,
                            total,
                            result['total_items'],
                            result['snoozed_items'],
                            f"{percentage:.1f}%"
                        ]
                    }
                    df_summary = pd.DataFrame(summary_data)
                    
                    # Create Excel file in memory
                    from io import BytesIO
                    excel_buffer = BytesIO()
                    
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        # Tab 1: Summary
                        df_summary.to_excel(writer, sheet_name='Summary', index=False)
                        
                        # Tab 2: Active Items
                        if result['active_items_list']:
                            df_active = pd.DataFrame(result['active_items_list'])
                            df_active.to_excel(writer, sheet_name='Active Items', index=False)
                        else:
                            # Create empty dataframe with same columns
                            df_empty_active = pd.DataFrame(columns=['Location', 'Category', 'Subcategory', 'Product Name', 'PLU', 'Product ID'])
                            df_empty_active.to_excel(writer, sheet_name='Active Items', index=False)
                        
                        # Tab 3: Inactive (Snoozed) Items
                        if result['snoozed_items_list']:
                            df_snoozed = pd.DataFrame(result['snoozed_items_list'])
                            df_snoozed.to_excel(writer, sheet_name='Inactive Items', index=False)
                        else:
                            # Create empty dataframe with same columns
                            df_empty_snoozed = pd.DataFrame(columns=['Location', 'Category', 'Subcategory', 'Product Name', 'PLU', 'Product ID'])
                            df_empty_snoozed.to_excel(writer, sheet_name='Inactive Items', index=False)
                    
                    excel_buffer.seek(0)
                    
                    # Sanitize filename
                    safe_location_name = "".join(c for c in location_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_location_name = safe_location_name.replace(' ', '_')
                    
                    st.download_button(
                        label="📥 Download Complete Excel Report",
                        data=excel_buffer,
                        file_name=f"{safe_location_name}_menu_analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Download a complete Excel file with Summary, Active Items, and Inactive Items tabs"
                    )
                    
                    st.markdown("---")
                    
                    # Display tables
                    if result['snoozed_items_list']:
                        st.subheader("😴 Snoozed Items")
                        df_snoozed = pd.DataFrame(result['snoozed_items_list'])
                        st.dataframe(df_snoozed, use_container_width=True, hide_index=True)
                        
                        # Download button for snoozed items
                        csv_snoozed = df_snoozed.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Snoozed Items CSV",
                            data=csv_snoozed,
                            file_name=f"{location_name}_snoozed_items.csv",
                            mime="text/csv"
                        )
                    
                    if result['active_items_list']:
                        st.subheader("✅ Active Items")
                        df_active = pd.DataFrame(result['active_items_list'])
                        st.dataframe(df_active, use_container_width=True, hide_index=True)
                        
                        # Download button for active items
                        csv_active = df_active.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Active Items CSV",
                            data=csv_active,
                            file_name=f"{location_name}_active_items.csv",
                            mime="text/csv"
                        )
                else:
                    st.error("Failed to retrieve menu data. Please check your IDs and try again.")
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                with st.expander("Show error details"):
                    st.code(traceback.format_exc())

elif page == "😴 Snooze History":
    # Import snooze history functions
    sys.path.insert(0, str(project_root / "snoozeHistory"))
    # Import snoozeHistoryPerPlu functions (suppress linter warning - works at runtime)
    import importlib
    import pandas as pd
    snoozeHistory = importlib.import_module("snoozeHistoryPerPlu")
    get_snooze_history_for_plu = snoozeHistory.get_snooze_history_for_plu
    format_snooze_history = snoozeHistory.format_snooze_history
    
    st.title("😴 Snooze History by PLU")
    st.markdown("View the snooze history for a specific product (PLU) at a location.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account = st.text_input("Account ID", placeholder="Enter account ID")
        location = st.text_input("Location ID", placeholder="Enter location ID")
    
    with col2:
        weeks_back = st.number_input("Weeks Back", min_value=1, max_value=52, value=2)
        plu = st.text_input("PLU", placeholder="Enter Product Lookup Unit (PLU)")
    
    if st.button("🔍 Search Snooze History", type="primary"):
        if not all([account, location, plu]):
            st.error("Please fill in Account ID, Location ID, and PLU")
        else:
            with st.spinner("Fetching snooze history..."):
                try:
                    history = get_snooze_history_for_plu(
                        location=location,
                        account=account,
                        plu=plu,
                        weeks_back=weeks_back
                    )
                    
                    if history:
                        st.success(f"Found {len(history)} snooze events for PLU: {plu}")
                        
                        # Display summary
                        snooze_count = sum(1 for event in history if event['action'] == 1)
                        unsnooze_count = sum(1 for event in history if event['action'] == 2)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Events", len(history))
                        with col2:
                            st.metric("😴 Snooze Events", snooze_count)
                        with col3:
                            st.metric("✅ Unsnooze Events", unsnooze_count)
                        
                        st.markdown("---")
                        st.subheader("📋 Complete Event History")
                        
                        # Helper function to format timestamps
                        def format_timestamp(ts):
                            if not ts or ts == 'N/A':
                                return ts
                            # Remove microseconds and 'Z' suffix, keep hours:minutes:seconds
                            # Format: 2025-11-27T09:11:43.700000Z -> 2025-11-27T09:11:43
                            ts_str = str(ts)
                            # Remove microseconds (everything after .)
                            if '.' in ts_str:
                                ts_str = ts_str.split('.')[0]
                            # Remove Z or timezone offset
                            ts_str = ts_str.rstrip('Z')
                            if '+' in ts_str:
                                ts_str = ts_str.split('+')[0]
                            return ts_str
                        
                        # Helper function to calculate duration
                        def calculate_duration(start, end):
                            if not start or not end or start == 'N/A' or end == 'N/A':
                                return 'N/A'
                            try:
                                from datetime import datetime
                                # Parse timestamps (handle with or without microseconds)
                                start_str = str(start).split('.')[0].rstrip('Z').split('+')[0]
                                end_str = str(end).split('.')[0].rstrip('Z').split('+')[0]
                                
                                start_dt = datetime.fromisoformat(start_str.replace('T', ' '))
                                end_dt = datetime.fromisoformat(end_str.replace('T', ' '))
                                
                                duration = end_dt - start_dt
                                total_seconds = int(duration.total_seconds())
                                
                                # Format duration nicely
                                if total_seconds < 0:
                                    return 'Invalid'
                                
                                days = total_seconds // 86400
                                hours = (total_seconds % 86400) // 3600
                                minutes = (total_seconds % 3600) // 60
                                
                                parts = []
                                if days > 0:
                                    parts.append(f"{days}d")
                                if hours > 0:
                                    parts.append(f"{hours}h")
                                if minutes > 0 or len(parts) == 0:
                                    parts.append(f"{minutes}m")
                                
                                return ' '.join(parts) if parts else '0m'
                            except Exception:
                                return 'N/A'
                        
                        # Prepare data for better visualization
                        display_data = []
                        for idx, event in enumerate(history, 1):
                            action_str = "😴 SNOOZE" if event['action'] == 1 else ("✅ UNSNOOZE" if event['action'] == 2 else f"❓ {event['action']}")
                            
                            # Format dates
                            created = format_timestamp(event.get('created', 'N/A'))
                            start = format_timestamp(event.get('snoozeStart', 'N/A'))
                            end = format_timestamp(event.get('snoozeEnd', 'N/A'))
                            
                            # Calculate duration
                            duration = calculate_duration(event.get('snoozeStart'), event.get('snoozeEnd'))
                            
                            # Create report URL (plain text for dataframe)
                            report_url = f"https://retail.deliverect.com/operationreports/{event['id']}" if event.get('id') else "N/A"
                            
                            display_data.append({
                                '#': idx,
                                'Action': action_str,
                                'Created': created,
                                'Product Name': event.get('name', 'N/A'),
                                'PLU': event.get('plu', plu),
                                'Snooze Start': start,
                                'Snooze End': end,
                                'User': f"{event.get('user_name', 'N/A')} ({event.get('user_id', '')})",
                                'Report Link': report_url
                            })
                        
                        # Create DataFrame for display
                        df_history = pd.DataFrame(display_data)
                        
                        # Display as a styled table with clickable links
                        st.dataframe(
                            df_history,
                            use_container_width=True,
                            hide_index=True,
                            height=400,
                            column_config={
                                "Report Link": st.column_config.LinkColumn(
                                    "Report",
                                    display_text="View Report",
                                    help="Click to view the operation report"
                                )
                            }
                        )
                        
                        # Also display in a more visual card format
                        st.markdown("---")
                        st.subheader("📊 Detailed Event View")
                        
                        for idx, event in enumerate(history, 1):
                            action_str = "😴 SNOOZE" if event['action'] == 1 else ("✅ UNSNOOZE" if event['action'] == 2 else f"❓ {event['action']}")
                            action_color = "🔴" if event['action'] == 1 else "🟢"
                            
                            # Create a card-like container
                            with st.container():
                                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                                
                                with col1:
                                    st.markdown(f"### {action_color}")
                                    st.markdown(f"**Event #{idx}**")
                                    st.markdown(f"**{action_str}**")
                                
                                with col2:
                                    st.markdown("**Timeline**")
                                    st.text(f"Created: {format_timestamp(event.get('created', 'N/A'))}")
                                    st.text(f"Start: {format_timestamp(event.get('snoozeStart', 'N/A'))}")
                                    st.text(f"End: {format_timestamp(event.get('snoozeEnd', 'N/A'))}")
                                    duration = calculate_duration(event.get('snoozeStart'), event.get('snoozeEnd'))
                                    st.text(f"Duration: {duration}")
                                
                                with col3:
                                    st.markdown("**Details**")
                                    st.text(f"Product: {event.get('name', 'N/A')}")
                                    st.text(f"PLU: {event.get('plu', plu)}")
                                    st.text(f"User: {event.get('user_name', 'N/A')}")
                                    if event.get('snoozeId'):
                                        st.text(f"Snooze ID: {event.get('snoozeId')}")
                                
                                with col4:
                                    if event.get('id'):
                                        st.markdown("**Links**")
                                        st.markdown(f"[🔗 Report](https://retail.deliverect.com/operationreports/{event['id']})")
                                
                                st.markdown("---")
                        
                        # Download as formatted text
                        formatted_text = format_snooze_history(history, plu)
                        st.download_button(
                            label="📥 Download History Report",
                            data=formatted_text,
                            file_name=f"snooze_history_{plu}_{location}.txt",
                            mime="text/plain"
                        )
                        
                        # Download as CSV
                        df_history_csv = pd.DataFrame(history)
                        csv_data = df_history.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv_data,
                            file_name=f"snooze_history_{plu}_{location}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info(f"No snooze history found for PLU: {plu}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    import traceback
                    with st.expander("Show error details"):
                        st.code(traceback.format_exc())

elif page == "🔍 Missing Inventory":
    # Import missing inventory functions
    sys.path.insert(0, str(project_root / "missingInventoryHighlighter.py"))
    import importlib
    import pandas as pd
    import time
    missingInventory = importlib.import_module("missingInventory")
    getInventory = missingInventory.getInventory
    getItems = missingInventory.getItems
    hasInventory = missingInventory.hasInventory
    getLocationName = missingInventory.getLocationName
    getAccountName = missingInventory.getAccountName
    getMissingInventory = missingInventory.getMissingInventory
    getAllLocations = missingInventory.getAllLocations
    
    st.title("🔍 Missing Inventory")
    st.markdown("Find items that exist in the catalog but are missing from inventory.")
    
    # Add option to view all locations or single location
    view_mode = st.radio(
        "View Mode:",
        ["📍 Single Location", "🌍 All Locations Overview"],
        horizontal=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        account = st.text_input("Account ID", placeholder="Enter account ID", key="missing_inv_account")
    
    with col2:
        if view_mode == "📍 Single Location":
            location = st.text_input("Location ID", placeholder="Enter location ID", key="missing_inv_location")
        else:
            location = None
            st.info("Will analyze all locations for this account")
    
    button_label = "🚀 Find Missing Inventory" if view_mode == "📍 Single Location" else "🚀 Analyze All Locations"
    
    if st.button(button_label, type="primary"):
        if not account:
            st.error("Please fill in Account ID")
        elif view_mode == "📍 Single Location" and not location:
            st.error("Please fill in Location ID")
        else:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.container()
            
            try:
                if view_mode == "📍 Single Location":
                    # Step 1: Get location name
                    status_text.text("🔍 Step 1/3: Getting location information...")
                    progress_bar.progress(15)
                    location_name = getLocationName(location)
                    if not location_name:
                        location_name = "Unknown Location"
                    status_text.text(f"✓ Location found: {location_name}")
                    
                    # Step 2: Fetch data and find missing inventory
                    status_text.text("📦 Step 2/3: Fetching data and analyzing...")
                    progress_bar.progress(40)
                    
                    with log_container:
                        with st.spinner("⏳ Fetching inventory and catalog items..."):
                            # Fetch once and reuse
                            inventory = getInventory(account)
                            items = getItems(account)
                            missing_inventory = getMissingInventory(account, location, inventory=inventory, items=items)
                    
                    progress_bar.progress(90)
                    status_text.text("🔍 Step 3/3: Finalizing...")
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    time.sleep(0.5)
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success(f"Analysis complete for: {location_name}")
                    if missing_inventory:
                        st.info("💾 CSV file has been generated automatically.")
                    
                    # Display summary metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Catalog Items", len(items))
                    with col2:
                        st.metric("Items in Inventory", len(inventory))
                    with col3:
                        st.metric("Missing Items", len(missing_inventory))
                    
                    if missing_inventory:
                        st.markdown("---")
                        st.subheader("📋 Missing Inventory Items")
                        
                        # Prepare data for display
                        display_data = []
                        for item in missing_inventory:
                            display_data.append({
                                'Location': location_name,
                                'PLU': item.get("plu", "N/A"),
                                'Name': item.get("name", "N/A")
                            })
                        
                        df_missing = pd.DataFrame(display_data)
                        st.dataframe(df_missing, use_container_width=True, hide_index=True)
                        
                        # Download CSV
                        csv_data = df_missing.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Missing Inventory CSV",
                            data=csv_data,
                            file_name=f"missing_inventory_{location_name}_{location}.csv",
                            mime="text/csv",
                            help="Download the missing inventory items as a CSV file"
                        )
                    else:
                        st.info("✅ All catalog items are present in inventory for this location!")
                
                else:  # All Locations Overview
                    # Step 1: Fetch inventory
                    status_text.text("📦 Step 1/3: Fetching inventory data...")
                    progress_bar.progress(20)
                    
                    with log_container:
                        with st.spinner("⏳ Fetching inventory items..."):
                            inventory = getInventory(account)
                    
                    status_text.text(f"✓ Found {len(inventory)} inventory items")
                    progress_bar.progress(40)
                    
                    # Step 2: Fetch all items
                    status_text.text("🛒 Step 2/3: Fetching all catalog items...")
                    progress_bar.progress(50)
                    
                    with log_container:
                        with st.spinner("⏳ Fetching catalog items..."):
                            items = getItems(account)
                    
                    status_text.text(f"✓ Found {len(items)} catalog items")
                    progress_bar.progress(70)
                    
                    # Step 3: Get missing inventory per location (optimized with lookup set)
                    status_text.text("🔍 Step 3/3: Analyzing missing inventory per location...")
                    progress_bar.progress(80)
                    
                    with log_container:
                        with st.spinner("⏳ Comparing inventory for all locations (optimized comparison)..."):
                            # Pass already-fetched data to avoid duplicate API calls
                            missing_per_location = getMissingInventory(account, location=None, inventory=inventory, items=items)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    time.sleep(0.5)
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success(f"Analysis complete for all locations!")
                    st.info("💾 CSV files have been generated automatically for each location with missing inventory.")
                    
                    # Display overview summary
                    total_locations = len(missing_per_location)
                    total_missing = sum(loc_data["count"] for loc_data in missing_per_location.values())
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Catalog Items", len(items))
                    with col2:
                        st.metric("Locations with Missing Items", total_locations)
                    with col3:
                        st.metric("Total Missing Items", total_missing)
                    
                    if missing_per_location:
                        st.markdown("---")
                        st.subheader("📊 Overview by Location")
                        
                        # Create overview dataframe
                        overview_data = []
                        for loc_id, loc_data in missing_per_location.items():
                            overview_data.append({
                                'Location Name': loc_data["location_name"],
                                'Location ID': loc_id,
                                'Missing Items Count': loc_data["count"]
                            })
                        
                        df_overview = pd.DataFrame(overview_data)
                        df_overview = df_overview.sort_values('Missing Items Count', ascending=False)
                        st.dataframe(df_overview, use_container_width=True, hide_index=True)
                        
                        # Download overview CSV
                        csv_overview = df_overview.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Overview CSV",
                            data=csv_overview,
                            file_name=f"missing_inventory_overview_{account}.csv",
                            mime="text/csv",
                            help="Download the overview of missing inventory per location"
                        )
                        
                        st.markdown("---")
                        st.subheader("📋 Detailed Missing Items by Location")
                        
                        # Create expandable sections for each location
                        for loc_id, loc_data in sorted(missing_per_location.items(), key=lambda x: x[1]["count"], reverse=True):
                            with st.expander(f"📍 {loc_data['location_name']} - {loc_data['count']} missing items"):
                                detail_data = []
                                for item in loc_data["missing_items"]:
                                    detail_data.append({
                                        'PLU': item.get("plu", "N/A"),
                                        'Name': item.get("name", "N/A")
                                    })
                                
                                df_detail = pd.DataFrame(detail_data)
                                st.dataframe(df_detail, use_container_width=True, hide_index=True)
                                
                                # Download button for this location
                                csv_detail = df_detail.to_csv(index=False)
                                safe_location_name = "".join(c for c in loc_data['location_name'] if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
                                st.download_button(
                                    label=f"📥 Download {loc_data['location_name']} CSV",
                                    data=csv_detail,
                                    file_name=f"missing_inventory_{safe_location_name}_{loc_id}.csv",
                                    mime="text/csv",
                                    key=f"download_{loc_id}"
                                )
                    else:
                        st.info("✅ All catalog items are present in inventory for all locations!")
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                with st.expander("Show error details"):
                    st.code(traceback.format_exc())

elif page == "🔎 Find Items Not in Menu":
    # Import find items not in menu functions
    sys.path.insert(0, str(project_root))
    import importlib
    import pandas as pd
    import time
    from utils.api_helpers import extractAllProductIdsFromCategories, getAllCategoriesPerCatalog, getAccountIdfromCatalogId
    from catImporter.csvToCatalog import getAllProducts
    
    st.title("🔎 Find Items Not in Menu")
    st.markdown("Find products that exist in the account catalog but are not included in a specific menu/catalog.")
    
    catalog_id = st.text_input(
        "Catalog ID",
        placeholder="Enter catalog/menu ID",
        help="The ID of the catalog/menu to check against"
    )
    
    if st.button("🚀 Find Items Not in Menu", type="primary", disabled=not catalog_id):
        if not catalog_id:
            st.error("Please enter a Catalog ID")
        else:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Get account ID from catalog
                status_text.text("🔍 Step 1/4: Getting account information...")
                progress_bar.progress(10)
                account_id = getAccountIdfromCatalogId(catalog_id)
                if not account_id:
                    st.error("Could not retrieve account ID from catalog. Please check the catalog ID.")
                    progress_bar.empty()
                    status_text.empty()
                else:
                    status_text.text(f"✓ Found account ID: {account_id}")
                    
                    # Step 2: Get all products in the menu
                    status_text.text("📋 Step 2/4: Fetching products in menu...")
                    progress_bar.progress(30)
                    
                    with st.spinner("⏳ Loading menu products..."):
                        categories = getAllCategoriesPerCatalog(catalog_id)
                        product_ids_in_menu = extractAllProductIdsFromCategories(categories)
                    
                    status_text.text(f"✓ Found {len(product_ids_in_menu)} products in menu")
                    progress_bar.progress(50)
                    
                    # Step 3: Get all products in account
                    status_text.text("🛒 Step 3/4: Fetching all products in account...")
                    progress_bar.progress(60)
                    
                    with st.spinner("⏳ Loading all account products..."):
                        all_products = getAllProducts(account_id)
                    
                    status_text.text(f"✓ Found {len(all_products)} total products in account")
                    progress_bar.progress(80)
                    
                    # Step 4: Find products not in menu
                    status_text.text("🔍 Step 4/4: Comparing products...")
                    progress_bar.progress(90)
                    
                    # Convert product_ids_in_menu to set for faster lookup
                    product_ids_set = set(product_ids_in_menu)
                    
                    products_not_in_menu = []
                    for product in all_products:
                        product_id = product.get("_id")
                        if product_id and product_id not in product_ids_set:
                            products_not_in_menu.append(product)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    time.sleep(0.5)
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success("🎉 Analysis completed successfully!")
                    
                    # Display summary metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Products in Account", len(all_products))
                    with col2:
                        st.metric("Products in Menu", len(product_ids_in_menu))
                    with col3:
                        st.metric("Products Not in Menu", len(products_not_in_menu))
                    
                    st.markdown("---")
                    
                    if products_not_in_menu:
                        st.subheader("📋 Products Not in Menu")
                        
                        # Prepare data for display
                        display_data = []
                        for product in products_not_in_menu:
                            display_data.append({
                                'Item': product.get("name", "N/A"),
                                'PLU': product.get("plu", "N/A")
                            })
                        
                        # Sort by Item name for better readability
                        display_data.sort(key=lambda x: x['Item'])
                        
                        df_not_in_menu = pd.DataFrame(display_data)
                        st.dataframe(
                            df_not_in_menu,
                            use_container_width=True,
                            hide_index=True,
                            height=400
                        )
                    else:
                        st.info("✅ All products in the account are included in this menu!")
                        # Create empty dataframe for download
                        display_data = []
                        df_not_in_menu = pd.DataFrame(columns=['Item', 'PLU'])
                    
                    # Always show download button
                    st.markdown("---")
                    st.subheader("📥 Download Results")
                    
                    safe_catalog_id = catalog_id.replace("/", "_").replace("\\", "_")
                    
                    # Download button for products not in menu
                    csv_data = df_not_in_menu.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Products Not in Menu CSV",
                        data=csv_data,
                        file_name=f"products_not_in_menu_{safe_catalog_id}.csv",
                        mime="text/csv",
                        help="Download the products not in menu as a CSV file"
                    )
                    
                    # Optional: Download all products comparison
                    if products_not_in_menu:
                        # Create comparison data with all products and their status
                        comparison_data = []
                        product_ids_set = set(product_ids_in_menu)
                        for product in all_products:
                            comparison_data.append({
                                'Item': product.get("name", "N/A"),
                                'PLU': product.get("plu", "N/A"),
                                'In Menu': 'Yes' if product.get("_id") in product_ids_set else 'No'
                            })
                        comparison_data.sort(key=lambda x: (x['In Menu'], x['Item']))
                        df_comparison = pd.DataFrame(comparison_data)
                        
                        comparison_csv = df_comparison.to_csv(index=False)
                        st.download_button(
                            label="📥 Download All Products Comparison CSV",
                            data=comparison_csv,
                            file_name=f"all_products_comparison_{safe_catalog_id}.csv",
                            mime="text/csv",
                            help="Download all products with their menu status (In Menu: Yes/No)"
                        )
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                with st.expander("Show error details"):
                    st.code(traceback.format_exc())
                progress_bar.empty()
                status_text.empty()

elif page == "🚗 Uber Address Scraper":
    # Import Uber Address Scraper functions
    sys.path.insert(0, str(project_root))
    import importlib
    import time
    import requests
    import re
    from authentication.tokening import getHeaders
    from utils.api_helpers import getAllLocations
    
    # Import functions from uberAddressScraper (package.module format)
    uberScraper = importlib.import_module("uberAddressScraper.uberAddressScraper")
    getUberInfo = uberScraper.getUberInfo
    findUberChannelLink = uberScraper.findUberChannelLink
    findUberChannelLinkAny = uberScraper.findUberChannelLinkAny
    stripNumberFromStreet = uberScraper.stripNumberFromStreet
    mapAddressInfo = uberScraper.mapAddressInfo
    returnUberUrl = uberScraper.returnUberUrl
    updateChannelLink = uberScraper.updateChannelLink
    updateLocationAddress = uberScraper.updateLocationAddress
    
    st.title("🚗 Uber Address Scraper")
    st.markdown("Scrape Uber Eats store information and update location addresses and channel links.")
    
    account_id = st.text_input(
        "Account ID",
        placeholder="Enter your Deliverect account ID",
        help="Your Deliverect account ID"
    )
    
    st.markdown("---")
    
    if st.button("🚀 Start Scraping", type="primary", disabled=not account_id):
        if not account_id:
            st.error("Please enter an Account ID")
        else:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Create log area for detailed feedback
            st.markdown("### 📋 Update Log")
            log_placeholder = st.empty()
            log_messages = []
            
            def add_log(message, level="info"):
                """Add a log message with timestamp"""
                timestamp = time.strftime('%H:%M:%S')
                icon = {
                    "info": "ℹ️",
                    "success": "✅",
                    "warning": "⚠️",
                    "error": "❌",
                    "processing": "🔄"
                }.get(level, "•")
                log_messages.append(f"[{timestamp}] {icon} {message}")
                # Display last 100 messages
                with log_placeholder.container():
                    st.code("\n".join(log_messages[-100:]), language=None)
            
            try:
                # Step 1: Get all locations
                status_text.text("📍 Step 1/2: Fetching all locations...")
                add_log("Fetching all locations for account...", "info")
                progress_bar.progress(5)
                
                all_locs_raw = getAllLocations(account_id, return_format="raw")
                
                if not all_locs_raw:
                    st.error("No locations found for this account")
                    add_log("No locations found", "error")
                else:
                    add_log(f"Found {len(all_locs_raw)} locations to process", "success")
                    progress_bar.progress(10)
                    
                    # Step 2: Process each location
                    status_text.text(f"🔄 Step 2/2: Processing {len(all_locs_raw)} locations...")
                    
                    results = {
                        "total": len(all_locs_raw),
                        "processed": 0,
                        "updated": 0,
                        "skipped": 0,
                        "errors": []
                    }
                    
                    for idx, loc in enumerate(all_locs_raw):
                        location_id = loc.get("_id")
                        location_name = loc.get("name", "Unknown")
                        
                        # Update progress
                        progress = 10 + int((idx / len(all_locs_raw)) * 90)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing {idx + 1}/{len(all_locs_raw)}: {location_name}")
                        
                        add_log(f"Processing: {location_name} ({location_id})", "processing")
                        results["processed"] += 1
                        
                        try:
                            # Find Uber channel link
                            add_log(f"  Searching for Uber channel link...", "info")
                            uberChannelLink = findUberChannelLinkAny(location_id)
                            
                            if not uberChannelLink:
                                add_log(f"  No Uber Eats channel link found (checked channels 6007 and 7)", "warning")
                                results["skipped"] += 1
                                continue
                            
                            APIKey = uberChannelLink.get("APIKey")
                            application = uberChannelLink.get("application")
                            uberChannelLinkId = uberChannelLink.get("channelLinkId")
                            
                            if not APIKey or not application:
                                add_log(f"  Missing APIKey or application for channel link", "warning")
                                results["skipped"] += 1
                                continue
                            
                            # Get Uber info
                            add_log(f"  Fetching Uber store info...", "info")
                            UberInfo = getUberInfo(application, APIKey)
                            
                            if not UberInfo:
                                add_log(f"  Failed to get Uber info", "error")
                                results["skipped"] += 1
                                continue
                            
                            # Map address info
                            addressInfo = mapAddressInfo(UberInfo)
                            if not addressInfo:
                                add_log(f"  Failed to map address info", "warning")
                                results["skipped"] += 1
                                continue
                            
                            # Get Uber URL
                            uberUrl = returnUberUrl(UberInfo)
                            
                            # Update channel link
                            add_log(f"  Updating channel link with URL...", "processing")
                            channel_link_updated = updateChannelLink(uberChannelLinkId, uberUrl)
                            
                            if channel_link_updated:
                                add_log(f"  ✓ Channel link updated with URL: {uberUrl}", "success")
                            else:
                                add_log(f"  ✗ Failed to update channel link", "error")
                            
                            # Update location address
                            add_log(f"  Updating location address...", "processing")
                            address_updated = updateLocationAddress(location_id, addressInfo)
                            
                            if address_updated:
                                street = addressInfo.get('address', {}).get('street', 'N/A')
                                city = addressInfo.get('address', {}).get('city', 'N/A')
                                add_log(f"  ✓ Location address updated: {street}, {city}", "success")
                            else:
                                add_log(f"  ✗ Failed to update location address", "error")
                            
                            if channel_link_updated or address_updated:
                                results["updated"] += 1
                                add_log(f"  ✅ Completed updates for {location_name}", "success")
                            else:
                                results["skipped"] += 1
                                
                        except Exception as e:
                            error_msg = f"Error processing {location_name}: {str(e)}"
                            add_log(f"  ❌ {error_msg}", "error")
                            results["errors"].append(error_msg)
                            results["skipped"] += 1
                    
                    # Finalize
                    progress_bar.progress(100)
                    status_text.text("✅ Scraping completed!")
                    add_log("✅ Processing complete!", "success")
                    
                    # Show results
                    st.balloons()
                    st.success("🎉 Uber address scraping completed!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Locations", results["total"])
                    with col2:
                        st.metric("Processed", results["processed"])
                    with col3:
                        st.metric("Updated", results["updated"])
                    with col4:
                        st.metric("Skipped/Errors", results["skipped"])
                    
                    if results["errors"]:
                        st.warning(f"⚠️ {len(results['errors'])} error(s) occurred:")
                        with st.expander("View Errors"):
                            for error in results["errors"]:
                                st.text(f"• {error}")
            
            except Exception as e:
                st.error(f"❌ Error during scraping: {str(e)}")
                add_log(f"Fatal error: {str(e)}", "error")
                import traceback
                with st.expander("Show error details"):
                    st.code(traceback.format_exc())

