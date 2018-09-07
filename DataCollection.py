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

# Text Fields
txt_fields = ["NAME","state", "county", "tract"]

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

gross_rent_30HMI = ["B25070_007E", "B25070_008E", "B25070_009E", "B25070_010E"]
total = "B25070_001E"
not_computed = "B25070_011E"

# Function that retrieves fields from the Data Profile ACS Table
def retrieveProfileData(fields):
    dfs = []
    for s in states:
        endpoint = "https://api.census.gov/data/2016/acs/acs5/profile?get=" + fields + ",NAME&for=tract:*&in=state:" + s + "&key=" + census_api_key
        response = requests.get(endpoint)
        jsonobject = json.JSONDecoder().decode(response.text)
        dfnxt = pd.DataFrame(columns=jsonobject[0], data=jsonobject[1:])
        dfs.append(dfnxt)
    df_ret = pd.concat(dfs)
    return df_ret

# Function that retrieves fields from the Detail ACS Table
def retrieveDetailData(fields, year):
    dfs = []
    for s in states:
        endpoint = "https://api.census.gov/data/"+ year + "/acs/acs5?get=" + fields + ",NAME&for=tract:*&in=state:" + s + "&key=" + census_api_key
        response = requests.get(endpoint)
        jsonobject = json.JSONDecoder().decode(response.text)
        dfnxt = pd.DataFrame(columns=jsonobject[0], data=jsonobject[1:])
        dfs.append(dfnxt)
    df_ret = pd.concat(dfs)
    return df_ret

def calculateRentBurden():
    dfs = []
    for s in states:
        endpoint = "https://api.census.gov/data/2016/acs/acs5?get=" + ','.join(gross_rent_30HMI) + ',' + total + ',' + not_computed + ",NAME&for=tract:*&in=state:" + s + "&key=" + census_api_key
        response = requests.get(endpoint)
        jsonobject = json.JSONDecoder().decode(response.text)
        dfnxt = pd.DataFrame(columns=jsonobject[0], data=jsonobject[1:])
        dfs.append(dfnxt)
    df_ret = pd.concat(dfs)
    df_ret["percent_gross_rent_>30%HI"] = pd.Series();
    for index,row in df_ret.iterrows():
        numerator = sum([float(row[i]) for i in gross_rent_30HMI])
        denominator = float(row[total]) - float(row[not_computed])
        try:
            row["percent_gross_rent_>30%HI"] = numerator/denominator
        except ZeroDivisionError, e:
            row["percent_gross_rent_>30%HI"] = np.NaN
    print(df_ret.head())
    df_ret.drop(gross_rent_30HMI + [total, not_computed], inplace = True)
    return df_ret

DF_2016RentBurden = calculateRentBurden();
print(DF_2016RentBurden.head())
DF_2016Profile = retrieveProfileData(','.join(ProfileVariables2016.keys()))
DF_2016Detail = retrieveDetailData(','.join(DetailVariables.keys()), '2016')

# The combination of Text Fields will be unique, and this will allow us to avoid duplicate columns.
DF_2016 = pd.merge(DF_2016Profile, DF_2016Detail, on=txt_fields, how="left")
new_columns = ProfileVariables2016.values() + txt_fields + DetailVariables.values()

DF_2016.columns = new_columns
DF_2016.to_csv("2016_Raw.csv")
