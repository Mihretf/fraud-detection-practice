import math

def calculate_z_score(amount, mean, std_dev):
    if mean is None or std_dev is None or std_dev == 0:
        return 0.0
    return (amount - mean) / std_dev

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def evaluate_risk(amount, lat, lon, profile):
    """
    profile is a dictionary/row containing: avg_amount, std_dev, home_lat, home_lon
    """
    is_fraud = False
    reason = "Normal"
    
    # 1. NEW USER PATH (No Profile Found)
    if profile is None:
        if amount > 500:
            return True, "Cold Start: Amount > 500"
        return False, "Normal"

    # 2. STATISTICAL PATH (Z-Score)
    z = calculate_z_score(amount, profile['avg_amount'], profile['std_dev'])
    if abs(z) > 3.0:
        return True, f"Stat Outlier: Z-Score {round(z, 2)}"

    # 3. GEOSPATIAL PATH (Distance Check)
    dist = haversine_distance(lat, lon, profile['home_lat'], profile['home_lon'])
    if dist > 200: # If transaction is > 200km from 'home'
        return True, f"Geo Outlier: {round(dist, 1)}km from home"

    return is_fraud, reason