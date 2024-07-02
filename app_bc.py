DB_USERNAME = "Vinay Barnabas"

import sqlite3
import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
from lifelines.utils import median_survival_times
from datetime import datetime

# define plot style
def set_plot_style():
    '''
    function to set figure parameters
    Inputs: None
    Return: None
    '''

    # define style: plots will not have gridlines. X- and y- ticks would be present
    sns.set_style('ticks')

    # parameter to control scaling of plot elements.
    sns.set_context('notebook')

    # fix figure parameters
    plt.rcParams['figure.figsize'] = (10,6)
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['lines.linewidth'] = 2
    
    # fix color palette
    sns.set_palette('muted')

def frame_off(ax):
    '''
    function to remove outframe in plots
    Inputs: ax = plot axes
    Return: Nothing
    '''
    for _, spines in ax.spines.items():
        spines.set_visible(False)


# fix figure paraeters by calling the function
set_plot_style()


# import database
# Establish connection to sqlite3 database and define a cursor
con = sqlite3.connect("techTest.db")
cur = con.cursor()

query_patient = '''--sql
                SELECT 
                    p.patient_id as patient_id, 
                    date(p.dod) as dod,  
                    STRFTIME("%Y", MIN(d.diagnosis_date)) - STRFTIME("%Y",p.dob) as age_at_diagnosis, 
                    date(MIN(d.diagnosis_date)) as first_diagnosis_date, 
                    sub_dates.last_diagnosis_date as last_diagnosis_date, 
                    sub_dates.last_test_date as last_test_date

                ---Patient joined to Diagnosis---
                FROM 
                    patient as p 
                LEFT JOIN 
                    diagnosis as d
                        ON p.patient_id = d.patient_id

                ---Left JOIN to sub-query that calculates last_diagnosis_date and last_test_date---
                ---last_diagnosis_date and last_test_date are calculated without considered BC status---
                ---This is because last encounter in the database should be disease independent---                        
                LEFT JOIN
                    (SELECT 
                        sub_p.patient_id, 
                        date(MAX(sub_d.diagnosis_date)) as last_diagnosis_date,
                        date(MAX(sub_b.test_date)) as last_test_date
                    FROM
                        patient as sub_p
                    LEFT JOIN
                        diagnosis as sub_d 
                            ON sub_p.patient_id = sub_d.patient_id
                    LEFT JOIN
                        biomarker as sub_b
                            ON sub_p.patient_id = sub_b.patient_id
                    GROUP BY
                        sub_p.patient_id
                    ) as sub_dates
                        ON p.patient_id = sub_dates.patient_id 

                WHERE  
                    d.diagnosis_code LIKE "C50%"
                        
                GROUP BY 
                    p.patient_id;

                '''

df = pd.read_sql_query(query_patient, con)

df_dod_mod = df.copy()
# Converting columns with date-time to pandas date-time
time_format_cols = ["first_diagnosis_date", "last_diagnosis_date", "last_test_date", "dod"]
for col in time_format_cols:
    df_dod_mod[col] = pd.to_datetime(df_dod_mod[col])

today = datetime(2024, 7, 1)
df_dod_mod.loc[df_dod_mod["dod"] > today, "dod"] = today

def replace_dod(row):
    if (row["dod"] < row["first_diagnosis_date"]) | (row["dod"] < row["last_diagnosis_date"]) | (row["dod"] <  row["last_test_date"]):
        row["dod"] = np.nan
    return row["dod"]

df_dod_mod["dod"] = df_dod_mod.apply(replace_dod, axis = 1)
df_dod_mod["last_encounter_date"] = np.max(df_dod_mod[["last_diagnosis_date", "last_test_date", "dod"]], axis = 1)
df_dod_mod["follow_up_time"] = ((df_dod_mod["last_encounter_date"] - df_dod_mod["first_diagnosis_date"]).dt.days/365.25).round(1)
df_final = df_dod_mod[df_dod_mod["follow_up_time"]!=0].copy()
df_final["status"] = df_final["dod"].notna().map({
                                                    True: "event",
                                                    False: "censor"
                                                })

### begin streamlit elements
st.title("Breast Cancer Patients: Survival Times")
st.divider()
age_to_stratify = st.slider(label = "age_at_diagnosis", 
                            min_value = 10,
                            max_value = 90,
                            value = 60)

mask = df_final["age_at_diagnosis"] > age_to_stratify
df_final["stratified_age"] = mask
df_final["stratified_age"] = df_final["stratified_age"].map({
                                                                True: "above",
                                                                False: "below"
                                                            })

custom_order = ["below", "above"]

fig_status, ax = plt.subplots(1,2)
k = sns.kdeplot(df_final, 
            x = "follow_up_time", 
            hue = "stratified_age", 
            hue_order = custom_order,
            fill = True, 
            common_norm = False, 
            clip = (0,80),
            alpha = 0.8,
            linewidth = 0,
            legend = False,
            ax = ax[0])



c = sns.countplot(df_final,
            x = "status",
            hue = "stratified_age",
            hue_order = custom_order,
            alpha = 0.9,
            ax = ax[1])

# label count values on top of each bar
for container in ax[1].containers:
    ax[1].bar_label(container)


ax[1].legend_.remove()
ax[0].set_ylim([0, 0.06])
ax[1].set_ylim([0, 700])
ax[1].set_ylabel("Count")
frame_off(ax[0])
frame_off(ax[1])
fig_status.legend([f"above {age_to_stratify}", f"below {age_to_stratify}"], 
           fontsize = 12, 
           frameon = False,
           loc = "upper center",
           ncols = len(ax))
st.pyplot(fig_status)
###

df_final["status"] = df_final["status"].map({
                                                "event": 1,
                                                "censor": 0
                                            })

fig_km, axes = plt.subplots()

# Instantiating the Kaplan-Meier class
km_lower = KaplanMeierFitter()
km_upper = KaplanMeierFitter()

# fitting Kaplan-Meier for patients below the stratify_age
km_lowerage = km_lower.fit(df_final.loc[~mask,"follow_up_time"], df_final.loc[~mask,"status"])
km_lowerage.plot(label = f"lower {age_to_stratify}")

# fitting Kaplan-Meier for patient above the stratify_age
km_upperage = km_upper.fit(df_final.loc[mask,"follow_up_time"], df_final.loc[mask,"status"])
km_upperage.plot(label = f"above {age_to_stratify}", 
                 xlabel = "Survival Time (Years)", 
                 ylabel = "Estimated Probability of Survival")

# fixing figure properties
plt.legend(fontsize = 12, frameon = False)
plt.box(False)
plt.title(f"Kaplan Meier curve for patients stratified by age = {age_to_stratify}")
plt.ylim([0, 1])
st.pyplot(fig_km, use_container_width = True)

###

# Calculate median survival times and their confidence intervals (using median survival times package from lifelines)
#median_upper = km_upperage.median_survival_time_
#median_ci_upper = median_survival_times(km_upperage.confidence_interval_).to_numpy()[0]
#median_lower = km_lowerage.median_survival_time_
#median_ci_lower = median_survival_times(km_lowerage.confidence_interval_).to_numpy()[0]

#print(f"Median survival time for patients over {age_to_stratify} years of age is {median_upper} {median_ci_upper[0],median_ci_upper[1]}")
#print(f"Median survival time for patients below {age_to_stratify} years of age is {median_lower} {median_ci_lower[0],median_ci_lower[1]}")




