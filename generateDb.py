#Functions & modules
import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import sqlite3
import uuid
import random

import os
os.getcwd()
os.chdir('/home/bnathasingh@ConcertoHealth.AI/projects/solutions-book-of-work/personal/brandon/interviewTechTest')

def generate_random_dates(start_date, end_date, n):
    return [start_date + timedelta(days=random.randint(7000, (end_date - start_date).days)) for _ in range(n)]

#Patient table
np.random.seed(1)
patient = pd.DataFrame()
n_pats = 1000
patient['patient_id'] = np.array([uuid.uuid4().__str__() for i in range(n_pats)])
base_date = np.datetime64('1930-01-01')
patient['dob'] = base_date + np.random.randint(0,15000,n_pats)
patient['dod'] = patient['dob'] + pd.to_timedelta(np.random.randint(10000,30000,n_pats),unit='D')
#suppress death dates past 2025
patient['gender'] = random.choices(['male','female','nonbinary','other','NULL'],[0.45,0.45,0.02,0.02,0.06],k=n_pats)


# Diagnosis table
diagnosis_codes = ['C50', 'C50.2', 'C50.4', 'C50.49', 'C61', 'I10', 'J18.9', 'C51']
diagnosis_codes_probs = [0.2, 0.2, 0.2, 0.2, 0.05, 0.05, 0.05, 0.05]

diagnosis_code_types = ['icd10']

dx_records = []

for _, row in patient.iterrows():
    num_records = random.randint(1, 5)  # Random number of dx records per patient
    diagnosis_dates = generate_random_dates(row['dob'], pd.Timestamp('2024-01-01'), num_records)
    
    for diagnosis_date in diagnosis_dates:
        record = {
            'patient_id': row['patient_id'],
            'diagnosis_date': diagnosis_date,
            'diagnosis_code': random.choices(diagnosis_codes, diagnosis_codes_probs)[0],
            'diagnosis_code_type': random.choice(diagnosis_code_types)
        }
        dx_records.append(record)

diagnosis = pd.DataFrame(dx_records)

#Biomarker table
biomarker_names = ['HER2', 'ER', 'BRCA1', 'BRCA2', 'PIK3CA', 'NA']
biomarker_names_probs = [0.5, 0.125, 0.125, 0.125, 0.12, 0.005]

biomarker_test_types = ['IHC', 'DNA sequencing', 'PCR', 'NA']
biomarker_test_types_probs = [0.5, 0.3, 0.15, 0.05]

test_results = ['Positive', 'Negative', 'Equivocal', 'Inconclusive', 'Unknown', 'NA']
test_results_probs = [0.2, 0.3, 0.2, 0.1, 0.1, 0.1]

biomarker_records = []

for _, row in patient.iterrows():
    num_records = random.randint(1,5)
    test_dates = generate_random_dates(row['dob'], pd.Timestamp('2024-01-01'), num_records)
    for test_date in test_dates:
        record = {
            'patient_id': row['patient_id'],
            'test_date': test_date,
            'biomarker_name': random.choices(biomarker_names, biomarker_names_probs)[0],
            'biomarker_test_type': random.choices(biomarker_test_types, biomarker_test_types_probs)[0],
            'test_result': random.choices(test_results, test_results_probs)[0]
        }
        biomarker_records.append(record)

biomarker = pd.DataFrame(biomarker_records)

conn = sqlite3.connect("techTestv2.db")

#Build the database
patient.to_sql('patient',con=conn,schema='sqlite_schema',if_exists='replace',index=False)
diagnosis.to_sql('diagnosis',con=conn,schema='sqlite_schema',if_exists='replace',index=False)
biomarker.to_sql('biomarker',con=conn,schema='sqlite_schema',if_exists='replace',index=False)

conn.commit()
conn.close()

#Run a query on the database
#conn = sqlite3.connect("techTest.db")
#pd.read_sql("select count(*) from biomarker",con=conn) 
#pd.read_sql("select * from biomarker limit 10",con=conn) 
#pd.read_sql("select * from biomarker where test_date > '2023-01-01' limit 10",con=conn)