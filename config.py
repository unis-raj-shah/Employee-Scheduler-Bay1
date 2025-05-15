"""Configuration settings for the warehouse scheduler application."""

import os
from typing import List, Dict, Any

# API Settings
WISE_API_HEADERS = {
    "authorization": os.getenv("WISE_API_KEY", "6d95c4d1-a408-4cc4-b1e1-04f3485ec78a"),
    "wise-company-id": os.getenv("WISE_COMPANY_ID", "ORG-1"),
    "wise-facility-id": os.getenv("WISE_FACILITY_ID", "F1"),
    "content-type": "application/json;charset=UTF-8",
    "user": os.getenv("WISE_USER", "rshah")
}

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.office365.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL", "raj.shah@unisco.com"),
    "sender_password": os.getenv("SENDER_PASSWORD", "T%058811678539oy"),
    "default_recipients": os.getenv("DEFAULT_RECIPIENTS", "raj.shah@unisco.com").split(',') #,mark.tuttle@unisco.com,john.diaz@unisco.com,carlos.morales@unisco.com,steven.balbas@unisco.com,steven.garcia@unisco.com").split(',')
}

# Database Settings
DB_PATH = os.getenv("DB_PATH", "./chroma_db_orgain")

# Customer Settings
DEFAULT_CUSTOMER_ID = os.getenv("DEFAULT_CUSTOMER_ID", "ORG-714892") #ORG-655338 orgain id, ORG-601372 Overseas, ORG-536926 KingsH, ORG-629731 Rise and Shine, ORG-625900 Zen, ORG-685351 Mamma Chia, ORG-714892 Natural Deca, 

# Role mappings for consistent matching
ROLE_MAPPINGS = {
    'forklift_driver': ['forklift', 'forklift driver', 'forklift operator', 'lift driver', 'Level 1 Forklift Driver', 'Level 2 Forklift Driver', 'Level 3 Forklift Driver'],
    'picker/packers': ['picker', 'packer', 'picker/packer', 'order picker', 'warehouse picker', 'General Labor', 'Quality Control'],
    'bendi_driver': ['bendi', 'bendi driver', 'bendi operator', 'reach truck'],
    'consolidation': ['consolidation', 'consolidator', 'inventory', 'inventory control'],
    'lumper': ['lumper', 'Lumper']
}

# Efficiency factor for workforce calculations (as a decimal)
WORKFORCE_EFFICIENCY = 0.8

# Work hours per shift
HOURS_PER_SHIFT = 7.5

# Default metrics summaries
DEFAULT_METRICS = {
    "inbound": {
        "avg_offload_time": 3.0,  # minutes per pallet
        "avg_scan_time": 1.5,     # minutes per pallet
        "avg_putaway_time": 3.25  # minutes per pallet
    },
    "picking": {
        "avg_pick_time_floor": 0.4,  # minutes per case
        "avg_pick_time_bendi": 2.0,  # minutes per case
        "avg_scan_time": 0.15,       # minutes per case
        "avg_wrap_time": 3.5     # minutes per pallet
    },
    "load": {
        "avg_load_time_per_pallet": 3.0  # minutes per pallet
    }
}

# Default shift schedule
DEFAULT_SHIFT = {
    "start_time": "6:00 AM",
    "end_time": "2:30 PM",
    "lunch_duration": "30 Mins",
    "location": "Buena Park, CA"
}