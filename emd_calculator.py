# emd_calculator.py

def calculate_emd_value(basic_fare, overall_fare, basic_commission, overall_commission, passenger_count):
    commission_amount = (basic_fare * basic_commission / 100) + (overall_fare * overall_commission / 100)
    adjusted_fare = overall_fare - commission_amount
    emd_value = round(adjusted_fare * passenger_count * 0.25)
    return emd_value