from collections import defaultdict
import json

"""
Definition of a function to calculate the GDI
"""

import json
from collections import defaultdict

def calculate_green_deal_index(data):
    """
    Calculate the Green Deal Index (GDI) based on weighted normalized indicators
    aggregated across hierarchical levels using AHP-derived weights.
    """
 
    # Initialize dictionary to store partial scores per hierarchy level
    hierarchy_level_scores = defaultdict(float)
 
    # Extract hierarchy weights from the dataset
    hierarchy_weights = data["hierarchy_weights"]
 
    for indicator in data["gdi_indicators"]:
        current = indicator["current_value"]
        target = indicator["target_value"]
        weight = indicator["indicator_weight"]
        # Clean hierarchy level name (remove extra spaces)
        level = indicator["hierarchy_level"].strip()
        impact_type = indicator["impact_type"].strip().lower()
 
        # Handle normalization depending on impact type
        if current == 0 or target == 0:
            normalized = 0   # Avoid division by zero
        elif impact_type == "positive":
            normalized = current / target
        elif impact_type == "negative":
            normalized = target / current
        else:
            raise ValueError(f"Invalid impact_type: {impact_type}")
 
        # Add weighted contribution to the corresponding hierarchy level
        contribution = normalized * weight
        indicator["contribution"] = contribution
 
        hierarchy_level_scores[level] += contribution
 
    # Final weighted sum across hierarchy levels
    gdi = sum(
        hierarchy_level_scores[level] * hierarchy_weights.get(level, 0)
        for level in hierarchy_level_scores
    )
 
    data["gdi"] = gdi
 
    return data
 