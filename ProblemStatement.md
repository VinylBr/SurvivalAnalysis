# Technical Test - Strategic Data Scientist - Concert AI

## Instructions

Attached is a SQLite database 'techTest.db' which contains 3 tables: patient, diagnosis, and biomarker. A data dictionary is provided. The database contains data for patients across multiple cancer indications. FOR BREAST CANCER (BC) PATIENTS ONLY, use the database to answer the following questions: 

1. Data maturity 
    - Calculate the summary statistics and plot the distribution of follow up time for BC patients.
    - Calculate the summary statistics and plot the distribution of age at initial diagnosis for BC patients

2. HER2 status
    - Calculate the intent to test rate for HER2. 
    - Calculate the tested rate for HER2.
    - Calculate the negativity rate for HER2.

3. Survival time
    - Perform a statistical test to calculate the summary statistics for survival time stratifying patients by age at initial diagnosis of 60 years old .
    - Plot a Kaplan-Meier curve stratifying patients by age at initial diagnosis of 60 years old.

The recommended tech stack is SQL/Python written in Virtual Studio Code or Dbeaver with the output pushed to a version control system. The recommended result/presentation structure is a Jupyter Notebook. However, any tech stack and result/presentation structure is acceptable.

On the interview day, you will give a 30 minute presentation on your tech stack, analytical approach, results, and code hygiene, followed by questions.


## Business Rules

* Breast cancer patients: Patients with an encounter in the diagnosis table with diagnosis_code matching regex pattern '^C50.*'

* Initial diagnosis date: The earliest encounter in the diagnosis table with the relevant filters.

* Follow up time: The duration of time between the initial diagnosis date and last encounter in the database for a given patient.

* Intent to test rate: The percentage of patients who have an encounter in the biomarker table for the relevant biomarker. 

* Tested rate: The percentage of patients who have an encounter in the biomarker table for the relevant biomarker with a valid test result.

* Negativity rate: The percentage of patients who have an encounter in the biomarker table for the relevant biomarker with a negative result.

## Requirements

* Required: Ability to manipulate a SQLite database.

* Other suggestions: [Python >= 3.12.1](https://www.python.org/downloads/release/python-3121/), [Jupyter](https://jupyter.org/install), [Virtual Studio Code](https://code.visualstudio.com/download), [DBeaver](https://dbeaver.io/download/)


## Resources

Feel free to consult online resources, but the final code and summary/presentation must be your own. Reach out to Brandon Nathasingh at bnathasingh@concertai.com with any questions.