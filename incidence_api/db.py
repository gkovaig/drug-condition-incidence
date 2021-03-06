from sqlalchemy import create_engine
from sqlalchemy import text

import settings
from db_util import determine_dialect

ENGINE = create_engine(settings.conn_str)
DIALECT = determine_dialect(settings.conn_str)

DRUG_CONDITION_QUERY = """
SELECT DISTINCT condition_concept_id AS outcome_concept_id, 
  condition AS outcome_concept_name,
  f.incidence_proportion_range_low,
  f.incidence_proportion_range_high 
FROM drug_condition_filtered d
JOIN IR_all_exposure_outcome_summary_overall f
  ON d.condition_concept_id = f.outcome_concept_id 
  AND d.ingredient_concept_id = f.drug_concept_id
WHERE ingredient_concept_id = :drug_concept_id AND time_at_risk_id = 365
AND cohort_type = 'First diagnosis of'
ORDER BY condition"""

DRUG_LIST_QUERY = """
SELECT *
FROM drug_list
"""

CONDITION_LIST_QUERY = """
SELECT DISTINCT outcome_concept_id,
  outcome_concept_name
FROM IR_all_exposure_outcome_summary_overall f
WHERE drug_concept_id = :drug_concept_id AND time_at_risk_id = 365
AND cohort_type = 'First diagnosis of'
ORDER BY outcome_concept_name"""

INCIDENCE_RATE_QUERY = """
SELECT
  incidence_proportion_range_low, 
  incidence_proportion_range_high 
FROM IR_all_exposure_outcome_summary_overall
WHERE drug_concept_id = :drug_concept_id
AND outcome_concept_id = :outcome_concept_id  
AND time_at_risk_id = :time_at_risk_id
AND cohort_type = 'First diagnosis of'"""

INCIDENCE_RATE_SOURCE_QUERY = """
SELECT source_short_name, 
  source_country, 
  incidence_proportion, 
  incidence_rate,
  num_persons_at_risk,
  CASE
	WHEN requires_full_time_at_risk = 1  THEN 'Yes'
	ELSE 'No'
  END as requires_full_time_at_risk 
FROM IR_all_exposure_outcome_summary_full
WHERE drug_concept_id = :drug_concept_id 
AND outcome_concept_id = :outcome_concept_id  
AND time_at_risk_id = :time_at_risk_id
AND cohort_type = 'First diagnosis of'
ORDER BY incidence_proportion DESC"""


def execute(q, ps=None):
    connection = ENGINE.connect()
    if settings.schema is not None:
        if DIALECT == 'postgresql':
            connection.execute('SET search_path TO ' + settings.schema)
    return connection.execute(text(q), **ps)


def drug_condition(drug_concept_id):
    """
    Given a drug concept_id, return associated conditions as list of dict
    """
    params = {'drug_concept_id': drug_concept_id}
    items = execute(DRUG_CONDITION_QUERY, params)
    rows = []
    for item in items:
        row = dict(zip(item.keys(), item))
        rows.append(row)
    return rows

def drug_list():
    """
    Return distinct drugs as list of dict
    """
    params = {}
    items = execute(DRUG_LIST_QUERY, params)
    rows = []
    for item in items:
        row = dict(zip(item.keys(), item))
        rows.append(row)
    return rows

def condition_list(drug_concept_id):
    """
    Given a drug concept_id, return associated distinct conditions as list of dict
    """
    params = {'drug_concept_id': drug_concept_id}
    items = execute(CONDITION_LIST_QUERY, params)
    rows = []
    for item in items:
        row = dict(zip(item.keys(), item))
        rows.append(row)
    return rows

def incidence_rate(drug_concept_id, outcome_concept_id, time_at_risk_id):
    """
    Given a drug concept_id and condition_concept_id, return incidence_proportion_range_low and
    incidence_proportion_range_high
    """
    params = {'drug_concept_id': drug_concept_id,
              'outcome_concept_id': str(outcome_concept_id),
              'time_at_risk_id': time_at_risk_id}
    items = execute(INCIDENCE_RATE_QUERY, params)
    for item in items:
        row = dict(zip(item.keys(), item))
        return row
    return None


def incidence_rate_source_details(drug_concept_id, outcome_concept_id, time_at_risk_id):
    """
    Given a drug concept_id and condition_concept_id, return incidence_proportion_range_low and
    incidence_proportion_range_high
    """
    params = {'drug_concept_id': drug_concept_id,
              'outcome_concept_id': outcome_concept_id,
              'time_at_risk_id': time_at_risk_id}
    items = execute(INCIDENCE_RATE_SOURCE_QUERY, params)
    rows = []
    for item in items:
        row = dict(zip(item.keys(), item))
        rows.append(row)
    return rows
