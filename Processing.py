import pandas as pd
import numpy as np
import os

def standardize(DF1):
    DF = DF1.copy()
    for i in all_fields:
        mean = DF[i].mean()
        std_dev = DF[i].std()
        if i in negative_factors:
            DF[i] = DF[i].apply(lambda x : -1 * ((x - mean) / std_dev))
        else:
            DF[i] = DF[i].apply(lambda x : (x - mean) / std_dev)
    return DF

def score(DF1, columnName):
    DF = DF1.copy()
    score_list = []
    for index, row in DF.iterrows():
        score = 0
        n = 0
        for i in all_fields:
            if not np.isnan(row[i]) and row[i] is not None:
                score += float(row[i])
                n += 1
        score_list.append(score/n)
    DF[columnName] = pd.Series(data=score_list,index=DF.index)
    return DF

def rescale(DF1, columnName, new_column):
    DF = DF1.copy()
    max_val = DF[columnName].max()
    min_val = DF[columnName].min()
    DF[new_column] = DF[columnName].apply(lambda x : 100 * (( x - max_val)/(max_val - min_val)) + 100)
    return DF

# Main Routine
df2016 = pd.read_csv("C:\Users\powicki\Desktop\Housing Market Index\2016raw.csv")
df2011 = pd.read_csv("C:\Users\powicki\Desktop\Housing Market Index\2011raw.csv")

df_composite = pd.DataFrame()

text_fields = set(["NAME","state","county","tract","Unnamed: 0"])
money_fields = set(["median_gross_rent","median_household_income","median_property_value"])
negative_factors = ["rental_vacancy_rate","percent_vacant_units","poverty_rate_fam","poverty_rate_ind","unemployment_rate","percent_gross_rent_>30%HI"]
all_fields = ["median_gross_rent","median_household_income","median_property_value","rental_vacancy_rate","percent_renter_occupied",
    "percent_vacant_units","poverty_rate_fam","poverty_rate_ind","unemployment_rate","percent_gross_rent_>30%HI","percent_bachelors+","total_population"]


negative_factors = negative_factors + [i + "%change" for i in negative_factors]

if 'composite.csv' not in os.listdir('.'):
    print('Creating Composite File...')
    for i in money_fields:
        df2011[i] = df2011[i].apply(lambda x : x * 1.06686838)

    for i in range(len(df2016.index)):
        row_2016 = df2016.iloc[i,:].copy()
        row_2011 = df2011.iloc[i,:].copy()
        n = 0
        for i in all_fields:
            val2016 = float(row_2016[i])
            val2011 = float(row_2011[i])

            if val2011 == 0 or np.isnan(val2011) or np.isnan(val2016):
                delta = np.NaN
                n += 1
            else:
                delta = (val2016 - val2011) / val2011
            row_2016[i + "%change"] = delta
        if(n <= 4):
            df_composite = df_composite.append(row_2016, ignore_index = True)

    df_composite.to_csv('composite.csv', index=False)
    print("Done.")
else:
    df_composite = pd.read_csv('composite.csv')

all_fields = all_fields + [i + "%change" for i in all_fields]

for i in all_fields:
    df_composite[i] = df_composite[i].apply(lambda x : float(x))

dfLA = df_composite[df_composite["state"] == '="22"']
dfAL = df_composite[df_composite["state"] == '="01"']
dfMS = df_composite[df_composite["state"] == '="28"']
dfTX = df_composite[df_composite["state"] == '="48"']

DF_States = [dfLA, dfAL, dfMS, dfTX]

df3State = df_composite[df_composite.state.isin(['="22"','="01"','="28"'])]

Counties = []
for i in dfLA.county.unique():
    Counties.append(dfLA[dfLA.county == i])

for i in dfAL.county.unique():
    Counties.append(dfAL[dfAL.county == i])

for i in dfMS.county.unique():
    Counties.append(dfMS[dfMS.county == i])

for i in dfTX.county.unique():
    Counties.append(dfTX[dfTX.county == i])

df_composite = standardize(df_composite)
df_composite = score(df_composite, "base_score")
df_composite = rescale(df_composite, "base_score","six_state_score")

df3State = standardize(df3State)
df3State = score(df3State, 'three_state_score_raw')
df3State = rescale(df3State, "three_state_score_raw", 'three_state_score')
df3State = pd.DataFrame({'NAME' : df3State["NAME"], 'three_state_score' : df3State["three_state_score"]})

df_composite = pd.merge(df_composite, df3State, on = "NAME", how = "left")

df_StateScores = pd.DataFrame(columns = [ "NAME","state_score" ])

for i in DF_States:
    i = standardize(i)
    i = score(i, 'state_score_raw')
    i = rescale(i, "state_score_raw", 'state_score')
    i = pd.DataFrame({'NAME' : i["NAME"], 'state_score' : i["state_score"]})
    df_StateScores = pd.concat([df_StateScores,i])

df_composite = pd.merge(df_composite, df_StateScores, on = "NAME", how = "left")

df_county_scores = pd.DataFrame(columns = ["NAME","county_score"])
for i in Counties:
    if len(i.index) == 1:
        i = pd.DataFrame({'NAME' : i["NAME"], 'county_score' : [np.NaN]})
    else:
        i = standardize(i)
        i = score(i, 'county_score_raw')
        i = rescale(i, "county_score_raw", "county_score")
        i = pd.DataFrame({'NAME' : i["NAME"], 'county_score' : i["county_score"]})
    df_county_scores = pd.concat([df_county_scores,i])

df_composite = pd.merge(df_composite, df_county_scores, on = "NAME", how = "left")
df_composite = df_composite[df_composite.state.isin(['="22"','="01"','="28"', '="48"'])]
df_composite.to_csv("compositescores_groupstandardized.csv", index=False)
df_composite[(df_composite.state == '="22"') & (df_composite.county == '="071"')].to_csv("NOLA.csv")
