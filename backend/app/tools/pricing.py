def calculate_project_price(estimated_hours: int, resource_levl: str="mid") -> int:
    """
    calculates the total cost based on hours and developer seniority.
    Args:
        estimated_hours (int): number of hours the project will take.
        resource_level (str): The complexity/seniority required ('junior', 'mid', 'senior', 'expert').
    Returns:
        int: The total calculated price in INR.
    """

# Define hourly rates for different levels
    RATES={
        "junior":100,
        "mid":400,
        "senior":600,
        "expert":1000
    }

    # Normalize input
    level=resource_levl.lower().strip()

    # partial matching: if 'senior' is in string. map it to 'senior'
    if "expert" in level:
        rate=RATES["expert"]
    elif "senior" in level:
        rate=RATES["senior"]
    elif "junior" in level:
        rate=RATES["junior"]
    else:
        rate=RATES["mid"] #default to mid if unclear

    # Price calculator

    total_price=estimated_hours*rate
    return total_price

if __name__=="__main__":
    hours=100
    level='Senior Developer'
    price=calculate_project_price(hours,level)
    print(f"The total price for a {hours} hour project with a {level} is estimated Rs.{price}, !! Please contact us for exact pricing and attractive discounts !! ")
