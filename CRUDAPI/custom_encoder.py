import json
from typing import Any
from decimal import Decimal

class CustomEncoder(json.JSONEncoder): # This class takes in a JSON Encoder
    def default(self, obj):            # This is a default function that takes in an object
        if isinstance(obj, Decimal):   # Check if object is an instance of Decimal
            return float(obj)          # Return a float version of Decimal object
        
        return json.JSONEncoder.default(self, obj)    # If not return a default value of the object- which is orginial 
