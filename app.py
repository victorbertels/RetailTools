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
        "😴 Snooze History"
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
    from authentication.tokening import getToken, headers
    
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
    if st.button("🚀 Start Import", type="primary", use_container_width=True, disabled=not all_ready):
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
                resp = requests.post(f"https://api.deliverect.io/catalog/accounts/{account_id}/items", json=payload, headers=headers).json()
                
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
    from authentication.tokening import getToken, headers
    
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
    
    if st.button("🚀 Analyze catalog", type="primary", use_container_width=True):
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
    
    if st.button("🔍 Search Snooze History", type="primary", use_container_width=True):
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

