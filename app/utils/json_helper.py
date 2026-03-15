from decimal import Decimal

def convert_decimal(data):
    if isinstance(data, list):
        return [convert_decimal(item) for item in data]

    if isinstance(data, dict):
        return {k: convert_decimal(v) for k, v in data.items()}

    if isinstance(data, Decimal):
        return float(data)

    return data
