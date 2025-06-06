"""Service for warehouse metrics calculations."""

from typing import Dict, Any
from config import DEFAULT_METRICS, WORKFORCE_EFFICIENCY, HOURS_PER_SHIFT

def get_metrics_summary() -> Dict[str, Dict[str, float]]:
    """
    Return metrics summaries.
    
    Returns:
        Dictionary of metrics by operation type
    """
    return DEFAULT_METRICS

def calculate_required_roles(metrics_summaries: Dict[str, Dict[str, float]],
                            forecast_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate required roles based on metrics and forecast data.
    
    Args:
        metrics_summaries: Dictionary of metrics by operation type
        forecast_data: Dictionary containing forecast data
        
    Returns:
        Dictionary of required role counts
    """
    try:
        incoming_pallets = forecast_data.get("daily_incoming_pallets", 0)
        shipping_pallets = forecast_data.get("daily_shipping_pallets", 0)
        total_cases = forecast_data.get("daily_order_qty", 0)
        cases_to_pick = forecast_data.get("cases_to_pick", 0)
        staged_pallets = forecast_data.get("staged_pallets", 0)

        
        required_roles = {}
        effective_work_mins_per_person = HOURS_PER_SHIFT * 60 * WORKFORCE_EFFICIENCY
        calculated_shipping_pallets = round(total_cases/75)
        shipping_pallets = shipping_pallets + calculated_shipping_pallets
        
        if "inbound" in metrics_summaries and incoming_pallets > 0:
            inbound = metrics_summaries["inbound"]
            total_offload_time = incoming_pallets * inbound.get("avg_offload_time", 2.15)
            total_scan_time = incoming_pallets * inbound.get("avg_scan_time", 0.15)
            total_putaway_time = incoming_pallets * inbound.get("avg_putaway_time", 3.0)
            
            required_roles["forklift_driver_inbound"] = max(1, round(total_offload_time / effective_work_mins_per_person))
            required_roles["scanner_inbound"] = max(1, round(total_scan_time / effective_work_mins_per_person))
            required_roles["bendi_driver_inbound"] = max(1, round(total_putaway_time / effective_work_mins_per_person))
            
        
        if shipping_pallets > 0 or cases_to_pick > 0:
            if "picking" in metrics_summaries:
                picking = metrics_summaries["picking"]
                
                total_pick_time_floor = cases_to_pick * picking.get("avg_pick_time_floor", 1.0)
                total_pick_time_bendi = shipping_pallets * picking.get("avg_pick_time_bendi", 2.0)
                total_wrap_time = shipping_pallets * picking.get("avg_wrap_time", 3.5)
                total_scan_time_picking = cases_to_pick * picking.get("avg_scan_time", 0.15)
                

                required_roles["bendi_driver_picking"] = max(1, round(total_pick_time_bendi / effective_work_mins_per_person))
                required_roles["picker"] = max(1, round(total_pick_time_floor / effective_work_mins_per_person))
                required_roles["packer"] = max(1, round((total_wrap_time + total_scan_time_picking)/ effective_work_mins_per_person))
                
            
            if "load" in metrics_summaries:
                load = metrics_summaries["load"]
                load_time_per_pallet = load.get("avg_load_time_per_pallet", 3.75)
            
            # Calculate loading time for picked orders
            if staged_pallets:
                picked_load_time = staged_pallets * load_time_per_pallet
                required_roles["forklift_driver_loading"] = max(1, round(picked_load_time / effective_work_mins_per_person))
            
            # Calculate loading time for forecasted shipping pallets (non-picked)
            if shipping_pallets > 0:
                forecast_load_time = shipping_pallets * load_time_per_pallet
                required_roles["forklift_driver_loading"] += max(1, round(forecast_load_time / effective_work_mins_per_person))

        # Combine roles
        total_forklift_drivers = sum(
            required_roles.get(role, 0)
            for role in [
                "forklift_driver_inbound",
                "forklift_driver_loading"
            ]
        )
        total_scanners = required_roles.get("scanner_inbound", 0) + required_roles.get("picker", 0)
        total_packers = required_roles.get("packer", 0)
        total_bendi_drivers = required_roles.get("bendi_driver_inbound", 0) + required_roles.get("bendi_driver_picking", 0)
        total_headcount = (total_forklift_drivers + total_bendi_drivers + total_scanners + total_packers)
        
        # Consolidation as 10% of total headcount
        consolidation_head_count = max(1, round(total_headcount * 0.1))
        
        final_roles = {
            "inbound": {
                "forklift_driver": required_roles.get("forklift_driver_inbound", 0),
                "receiver": required_roles.get("scanner_inbound", 0),
                "bendi_driver": required_roles.get("bendi_driver_inbound", 0)
            },
            "picking": {
                "bendi_driver": required_roles.get("bendi_driver_picking", 0),
                "general labor": required_roles.get("packer", 0) + required_roles.get("picker", 0)
            },
            "loading": {
                "forklift_driver": required_roles.get("forklift_driver_loading", 0)
            },
            "replenishment": {
                "staff": consolidation_head_count
            }
        }
        
        
        return final_roles
        
        
    except Exception as e:
        print(f"ERROR in calculate_required_roles: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "inbound": {
                "forklift_driver": 3,
                "receiver": 2,
                "bendi_driver": 2
            },
            "picking": {
                "bendi_driver": 2,
                "general labor": 3
            },
            "loading": {
                "forklift_driver": 2
            },
            "replenishment": {
                "staff": 1
            }
        }