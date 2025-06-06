"""Configuration settings for the warehouse scheduler application."""

import os
from typing import List, Dict, Any

# API Settings
WISE_API_HEADERS = {
    "authorization": os.getenv("WISE_API_KEY", "a9e744a2-1ba8-4797-85ca-d41e0a2cbf8e"),
    "wise-facility-id": os.getenv("WISE_FACILITY_ID", "F1"),
    "content-type": "application/json;charset=UTF-8",
    "user": os.getenv("WISE_USER", "rshah")
}

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.office365.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL", "raj.shah@unisco.com"),
    "sender_password": os.getenv("SENDER_PASSWORD", "Raj@UNIS123"),
    "default_recipients": os.getenv("DEFAULT_RECIPIENTS", "raj.shah@unisco.com, diego.delgado@unisco.com, mark.tuttle@unisco.com,john.diaz@unisco.com,steven.balbas@unisco.com, ricardo.tapia@unisco.com").split(',')
}

# Database Settings
DB_PATH = os.getenv("DB_PATH", "./chroma_db_orgain")

# we will use the following orgs
# ORG-629731 Rise and Shine, 
# ORG-625900 Zen
# ORG-625904 Recovery Sports
# ORG-625907 WATER PLUS
# ORG-625905 MUSE
# ORG-55783 Sans Wine Spirits
# ORG-647815 MELOGRANO
# ORG-674362 Gimme health Foods
# ORG-540512 SOUTHERN GLAZERs
# ORG-434827 DIVINELY NECTAR
# ORG-538772 PASSION TREE
# ORG-582188 PREFERRED BRANDS INTERNATIONAL
# ORG-646997 Ritual Beverage
# ORG-723580 Uptime Energy
# ORG-672896 KACE TEA
# ORG-616507 Roar Beverages
# ORG-539166 AMERICAN VINES
# ORG-685351 MAMMA CHIA
# ORG-714892 NATURAL DECADANCE


# Customer Settings############### 

DEFAULT_CUSTOMER_ID = os.getenv("DEFAULT_CUSTOMER_ID", 
                               "ORG-629731, ORG-625900, ORG-625904, ORG-625907, "
                               "ORG-625905, ORG-55783, ORG-647815, ORG-674362, "
                               "ORG-540512, ORG-434827, ORG-538772, ORG-582188, "
                               "ORG-646997, ORG-723580, ORG-672896, ORG-616507, "
                               "ORG-539166, ORG-685351, ORG-714892")
                                                                    

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