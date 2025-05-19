"""Client for external API services."""

import requests
import pandas as pd
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from config import WISE_API_HEADERS, DEFAULT_CUSTOMER_ID

# Split the comma-separated IDs into a list
CUSTOMER_IDS = [cid.strip() for cid in DEFAULT_CUSTOMER_ID.split(',')]

def get_tomorrow_date_range(days_ahead: int = 1) -> Tuple[datetime, datetime, datetime]:
    """
    Get tomorrow's date range for API requests.
    
    Args:
        days_ahead: Number of days ahead to calculate
        
    Returns:
        Tuple of (start_datetime, end_datetime, target_date)
    """
    target_date = datetime.now() + timedelta(days=days_ahead)
    start_datetime = target_date.replace(hour=0, minute=0, second=0)
    end_datetime = target_date.replace(hour=23, minute=59, second=59)
    return start_datetime, end_datetime, target_date

def get_priority_report(sheet_name: Optional[str] = None) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Get priority report data from the API.
    
    Args:
        sheet_name: Name of the sheet to retrieve, or 'all' for all sheets
        
    Returns:
        Dictionary of DataFrames if sheet_name is 'all', otherwise a single DataFrame
    """
    url = "https://wise.logisticsteam.com/v2/valleyview/cp/report-center/report/get-report-file"
    
    payload = {
        "reportService": "priorityReport",
        "reportFunction": "buildPriorityReport"
    }
    
    try:
        print("Fetching priority report file...")
        response = requests.post(url, headers=WISE_API_HEADERS, json=payload)
        response.raise_for_status()
        
        if response.status_code == 200:
            excel_file = io.BytesIO(response.content)
            available_sheets = pd.ExcelFile(excel_file).sheet_names
            print(f"Available sheets: {available_sheets}")
            
            if sheet_name == 'all':
                try:
                    return pd.read_excel(excel_file, sheet_name=['RG Outbound', 'Inbound'])
                    
                except ValueError:
                    print("Standard sheet names not found, trying alternative names...")
                    outbound_sheet = next((s for s in available_sheets if 'outbound' in s.lower()), None)
                    inbound_sheet = next((s for s in available_sheets if 'inbound' in s.lower()), None)
                    
                    if outbound_sheet and inbound_sheet:
                        return pd.read_excel(excel_file, sheet_name=[outbound_sheet, inbound_sheet])
                    else:
                        print("Could not find appropriate sheets in Excel file")
            else:
                target_sheet = sheet_name or 'RG Outbound'
                if target_sheet not in available_sheets:
                    target_sheet = next((s for s in available_sheets 
                                       if ('outbound' if 'outbound' in target_sheet.lower() else 'inbound') in s.lower()), None)
                
                if target_sheet and target_sheet in available_sheets:
                    return pd.read_excel(excel_file, sheet_name=target_sheet)
                else:
                    print(f"Could not find sheet {target_sheet}")
        
        return None
    
    except Exception as e:
        print(f"Error fetching priority report: {str(e)}")
        return None

def get_inbound_receipts() -> List[Dict[str, Any]]:
    """
    Get inbound receipt data from the API.
    
    Returns:
        List of receipt dictionaries
    """
    tomorrow_start, tomorrow_end, _ = get_tomorrow_date_range()
    url = "https://wise.logisticsteam.com/v2/valleyview/bam/inbound/receipt/search-by-paging"
    
    payload = {
        "appointmentTimeFrom": tomorrow_start.strftime('%Y-%m-%dT%H:%M:%S'),
        "appointmentTimeTo": tomorrow_end.strftime('%Y-%m-%dT%H:%M:%S'),
        "customerIds": CUSTOMER_IDS,  # Already supports multiple IDs
        "paging": {"pageNo": 1, "limit": 1000},
        "statuses": ["Appointment Made", "In Yard"]
    }

    try:
        print("Fetching inbound receipts...")
        response = requests.post(url, headers=WISE_API_HEADERS, json=payload)
        response.raise_for_status()
        
        data = response.json()
        receipts = data.get('receipts', [])
        print(f"Retrieved {len(receipts)} inbound receipts")
        
        return receipts
    
    except Exception as e:
        print(f"Error in inbound receipt API: {str(e)}")
        return []

def get_equipment_details() -> List[Dict[str, Any]]:
    """
    Get equipment details from the API.
    
    Returns:
        List of equipment details dictionaries with receipt IDs
    """
    url = "https://wise.logisticsteam.com/v2/valleyview/bam/wms-app/csr/equipmentDetail"
    all_equipment_details = []
    
    for customer_id in CUSTOMER_IDS:
        payload = {
            "customerId": customer_id.strip(),
            "type": "Container",
            "equipmentStatus": "Full",
            "statuses": ["Loaded", "Full to Offload"],
            "paging": {"pageNo": 1, "limit": 1000}
        }
        
        try:
            print(f"Fetching equipment details for customer {customer_id}...")
            response = requests.post(url, headers=WISE_API_HEADERS, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if not isinstance(data, list):
                print(f"Unexpected response format from equipment details API for {customer_id}. Expected list, got {type(data)}")
                continue
                
            # Extract equipment details with receipt IDs
            for equipment in data:
                if isinstance(equipment, dict):
                    receipt_ids = equipment.get('receiptIds', [])
                    if receipt_ids:
                        all_equipment_details.append({
                            'equipmentNo': equipment.get('equipmentNo', ''),
                            'receiptIds': receipt_ids,
                            'status': equipment.get('status', ''),
                            'location': equipment.get('currentLocation', ''),
                            'customerId': customer_id  # Add customer ID for reference
                        })
                
        except Exception as e:
            print(f"Error in fetching equipment details for {customer_id}: {str(e)}")
    
    print(f"Processed {len(all_equipment_details)} equipment details with receipt IDs across all customers")
    # go through all equipment details and print the equipmentNo and the receiptIds and customerId
    # for equipment in all_equipment_details:
    #     print(f"Equipment No: {equipment['equipmentNo']}, Receipt IDs: {equipment['receiptIds']}, Customer ID: {equipment['customerId']}\n")
    return all_equipment_details

def get_outbound_orders():
    """
    Get outbound orders from status report.
    
    Returns:
        List of dictionaries containing outbound order information
    """
    tomorrow_start, tomorrow_end, _ = get_tomorrow_date_range()
    url = "https://wise.logisticsteam.com/v2/valleyview/report-center/outbound/order-status-report/search-by-paging"
    all_processed_orders = []
    
    for customer_id in CUSTOMER_IDS:
        payload = {
            "statuses": ["Imported", "Open", "Planning", "Planned", "Committed"],
            "customerId": customer_id.strip(),
            "orderTypes": ["Regular Order"],
            "paging": {"pageNo": 1, "limit": 1000}
        }
        
        # Use appointment time for MAMMA CHIA, target completion for others
        if customer_id.strip() == "ORG-685351":
            payload["appointmentTimeFrom"] = tomorrow_start.strftime('%Y-%m-%dT%H:%M:%S')
            payload["appointmentTimeTo"] = tomorrow_end.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            payload["targetCompletionDateFrom"] = tomorrow_start.strftime('%Y-%m-%dT%H:%M:%S')
            payload["targetCompletionDateTo"] = tomorrow_end.strftime('%Y-%m-%dT%H:%M:%S')
        
        try:
            print(f"Fetching outbound orders for customer {customer_id}...")
            response = requests.post(url, headers=WISE_API_HEADERS, json=payload)
            response.raise_for_status()
            
            data = response.json()
            orders = data.get('results', {}).get('data', [])
            
            # Process and standardize order data
            for order in orders:
                try:
                    pallet_qty = float(order.get('Pallet QTY', 0)) or 0
                    order_qty = float(order.get('Order QTY', 0)) or 0
                    picking_type = order.get('Picking Type', '')
                except (ValueError, TypeError):
                    pallet_qty = order_qty = 0
                    picking_type = ''
                    
                all_processed_orders.append({
                    'order_no': order.get('Order No.'),
                    'status': order.get('Order Status', 'Unknown'),
                    'customer': customer_id,  # Use the actual customer ID we're querying with
                    'ship_to': order.get('Ship to', 'Unknown'),
                    'state': order.get('State', 'Unknown'),
                    'reference_no': order.get('Reference Number', ''),
                    'target_completion_date': order.get('Target Completion Date', ''),
                    'pallet_qty': pallet_qty,
                    'order_qty': order_qty,
                    'Picking Type': picking_type
                })
        
        except Exception as e:
            print(f"Error in outbound status report API for {customer_id}: {str(e)}")
    
    print(f"Retrieved {len(all_processed_orders)} outbound orders across all customers")
    # go through all processed orders and print the order_no and the customer and reference_no
    # for order in all_processed_orders:
    #     print(f"Order No: {order['order_no']}, Customer: {order['customer']}, Reference No: {order['reference_no']}\n")
    return all_processed_orders


def get_picked_outbound_orders():
    """
    Get picked outbound orders from status report.
    
    Returns:
        List of dictionaries containing picked outbound order information
    """
    tomorrow_start, tomorrow_end, _ = get_tomorrow_date_range()
    url = "https://wise.logisticsteam.com/v2/valleyview/report-center/outbound/order-status-report/search-by-paging"
    all_processed_picked_orders = []
    
    for customer_id in CUSTOMER_IDS:
        payload = {
            "statuses": ["Picked", "Packed", "Staged"],
            "customerId": customer_id.strip(),
            "orderTypes": ["Regular Order"],
            "paging": {"pageNo": 1, "limit": 1000}
        }
        
        # Use appointment time for MAMMA CHIA, target completion for others
        if customer_id.strip() == "ORG-685351":
            payload["appointmentTimeFrom"] = tomorrow_start.strftime('%Y-%m-%dT%H:%M:%S')
            payload["appointmentTimeTo"] = tomorrow_end.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            payload["targetCompletionDateFrom"] = tomorrow_start.strftime('%Y-%m-%dT%H:%M:%S')
            payload["targetCompletionDateTo"] = tomorrow_end.strftime('%Y-%m-%dT%H:%M:%S')
        
        try:
            print(tomorrow_start.strftime('%Y-%m-%dT%H:%M:%S'), tomorrow_end.strftime('%Y-%m-%dT%H:%M:%S'))
            print(f"Fetching picked outbound orders for customer {customer_id}...")
            response = requests.post(url, headers=WISE_API_HEADERS, json=payload)
            response.raise_for_status()
            
            data = response.json()
            orders = data.get('results', {}).get('data', [])
            
            # Process and standardize picked order data
            for order in orders:
                try:
                    pallet_qty = float(order.get('Pallet QTY', 0)) or 0
                    order_qty = float(order.get('Order QTY', 0)) or 0
                except (ValueError, TypeError):
                    pallet_qty = order_qty = 0
                    
                all_processed_picked_orders.append({
                    'order_no': order.get('Order No.'),
                    'status': order.get('Order Status', 'Unknown'),
                    'customer': customer_id,  # Use the actual customer ID we're querying with
                    'ship_to': order.get('Ship to', 'Unknown'),
                    'state': order.get('State', 'Unknown'),
                    'reference_no': order.get('Reference Number', ''),
                    'target_completion_date': order.get('Target Completion Date', ''),
                    'pallet_qty': pallet_qty,
                    'order_qty': order_qty
                })
        
        except Exception as e:
            print(f"Error in picked outbound status report API for {customer_id}: {str(e)}")
    
    print(f"Retrieved {len(all_processed_picked_orders)} picked outbound orders across all customers")
    # go through all processed picked orders and print the order_no and the customer and reference_no
    for order in all_processed_picked_orders:
        print(f"Order No: {order['order_no']}, Customer: {order['customer']}, Reference No: {order['reference_no']}\n")
    return all_processed_picked_orders

get_picked_outbound_orders()
get_outbound_orders()
# get_equipment_details()
# get_inbound_receipts()
# get_priority_report()
