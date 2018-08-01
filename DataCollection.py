from dotenv import load_dotenv
import os
import requests
import pandas as pd
import numpy as np
import json

load_dotenv(dotenv_path='.env')

census_api_key = os.getenv("API_KEY")

# Fips Codes for States of Interest
states = ["01", "22", "28", "48","12","13"]

# Indicator Census IDs and Labels for the 2016 ACS 5 Year Estimates Data Profile Table
ProfileVariables2016 ={'DP04_0047PE': 'percent_renter_occupied',
                       'DP04_0005E': 'rental_vacancy_rate',
                       'DP04_0003PE': 'percent_vacant_units',
                       'DP03_0119PE': 'poverty_rate_fam',
                       'DP03_0062E': 'median_household_income',
                       'DP02_0067PE': 'percent_bachelors+',
                       'DP02_0086E': 'total_population',
                       'DP03_0128PE': 'poverty_rate_ind',
                       'DP03_0009PE': 'unemployment_rate'
                       }

# Indicator Census IDs and Labels for the 2011 & 2016 ACS 5 Year Estimates Detail Table
DetailVariables = { "B25064_001E" : "median_gross_rent" ,
                    "B25097_001E" : "median_property_value" }

# Indicator Census IDs and Labels for the 2011 ACS 5 Year Estimates Data Profile Table
ProfileVariables2011 ={'DP04_0046PE': 'percent_renter_occupied',
                       'DP04_0005E': 'rental_vacancy_rate',
                       'DP04_0003PE': 'percent_vacant_units',
                       'DP03_0119PE': 'poverty_rate_fam',
                       'DP03_0062E': 'median_household_income',
                       'DP02_0067PE': 'percent_bachelors+',
                       'DP02_0086E': 'total_population',
                       'DP03_0128PE': 'poverty_rate_ind',
                       'DP03_0009PE': 'unemployment_rate'
                       }

gross_rent_30HMI = ["B25070_007E", "B25070_008E", "B25070_009E", "B25070_010E","B25070_001E","B25070_011E"]
total = "B25070_001E"
not_computed = "B25070_011E"
