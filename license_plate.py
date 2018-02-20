# -*- coding: utf-8 -*-
# Determine the license plate of the car

def plate_type(str):
    if len(str) == 6 and str[:3].isupper() and str[3:].isdigit():
        print('Old type license plate')
    elif len(str) == 7 and str[:4].isdigit() and str[4:].isupper():
        print('New type license plate')
    else:
        print('Wrong plate type')

# Ok
plate_type('ABC123')
plate_type('1234POW')
# Wrong
plate_type('123POW')
plate_type('abc123')
