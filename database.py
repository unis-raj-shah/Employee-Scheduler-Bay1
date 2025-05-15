"""Database connection and operations for the warehouse scheduler."""

import chromadb
import json
import re
import Levenshtein
from typing import Dict, List, Any, Optional
from config import DB_PATH, ROLE_MAPPINGS

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=DB_PATH)
employee_collection = chroma_client.get_or_create_collection(name="employees")

def normalize_role(role: str) -> str:
    """
    Normalize role names for consistent matching.
    
    Args:
        role: Role name to normalize
        
    Returns:
        Normalized role name
    """
    role = role.lower().strip()
    # Remove trailing 's' if present (e.g., "drivers" -> "driver")
    role = re.sub(r's$', '', role)  
    # Replace spaces with underscores for consistency
    role = re.sub(r'\s+', '_', role)
    return role

def retrieve_employees(required_roles: Dict[str, int]) -> Dict[str, List[str]]:
    """
    Retrieves employees from ChromaDB matching the required roles.
    
    Args:
        required_roles: Dictionary of roles and their required counts
        
    Returns:
        Dictionary mapping roles to lists of available employee IDs
    """
    matched_employees = {}
    
    try:
        # Get all employees from the database once
        all_employees = employee_collection.get()
        all_ids = all_employees.get("ids", [])
        all_metadatas = all_employees.get("metadatas", [])
        
        for role in required_roles:
            matched_employees[role] = []
            # Extract base role without operation prefix
            base_role = role.split('_', 1)[-1] if '_' in role else role
            role_variations = ROLE_MAPPINGS.get(base_role, [base_role])
            
            for i, metadata in enumerate(all_metadatas):
                if is_employee_available(metadata):
                    employee_skills = metadata.get("skills", "").lower().split(',')
                    employee_skills = [skill.strip() for skill in employee_skills]
                    
                    # Check if employee has any of the role variations in their skills
                    if any(variation.lower() in employee_skills for variation in role_variations):
                        matched_employees[role].append(all_ids[i])
            
            if not matched_employees[role]:
                print(f"Warning: No employees found for role {role}")
    
    except Exception as e:
        print(f"Error retrieving employees: {e}")
    
    return matched_employees

def is_employee_available(metadata: Dict[str, Any]) -> bool:
    """
    Check if an employee is available for scheduling based on their metadata.
    
    Args:
        metadata: Employee metadata from ChromaDB
        
    Returns:
        bool: True if employee is available, False otherwise
    """
    try:
        # Check if employee is active
        if not metadata.get("active", True):
            return False
        
        # Check if employee is on leave
        if metadata.get("on_leave", False):
            return False
        
        # Check shift preferences if available
        shift_preferences = metadata.get("shift_preferences", [])
        if shift_preferences and "day" not in shift_preferences:
            return False
        
        return True
        
    except Exception:
        return False

def find_best_match(name: str, employee_list: List[str]) -> Optional[str]:
    """
    Find the best matching employee name using fuzzy matching.
    
    Args:
        name: Name to search for
        employee_list: List of employee IDs to search within
        
    Returns:
        Best matching employee ID or None if no good match found
    """
    best_match = None
    best_score = float('inf')  # Lower is better for Levenshtein distance
    
    name_lower = name.lower()
    
    for emp_id in employee_list:
        # Get name variations
        try:
            emp_data = employee_collection.get(ids=[emp_id])
            if not emp_data or not emp_data["metadatas"]:
                continue
            
            metadata = emp_data["metadatas"][0]
            name_variations_json = metadata.get("name_variations", "[]")
            name_variations = json.loads(name_variations_json)
            
            # If no variations stored, use the ID
            if not name_variations:
                name_variations = [emp_id]
            
            # Try all variations and find the best match
            for variation in name_variations:
                variation_lower = variation.lower()
                
                # Exact match
                if name_lower == variation_lower:
                    return emp_id
                
                # Calculate Levenshtein distance
                distance = Levenshtein.distance(name_lower, variation_lower)
                if distance < best_score:
                    best_score = distance
                    best_match = emp_id
        except Exception as e:
            print(f"Error in name matching for {emp_id}: {e}")
    
    # Only return a match if the score is below a threshold (30% of name length)
    if best_score <= len(name) * 0.3:
        return best_match
    return None

def get_employee_details(emp_id: str) -> Dict[str, Any]:
    """
    Get employee details from the database.
    
    Args:
        emp_id: Employee ID
        
    Returns:
        Dictionary containing employee details
    """
    try:
        emp_data = employee_collection.get(ids=[emp_id])
        if not emp_data or not emp_data["metadatas"]:
            return {}
        
        return emp_data["metadatas"][0]
    except Exception as e:
        print(f"Error getting employee details: {e}")
        return {}