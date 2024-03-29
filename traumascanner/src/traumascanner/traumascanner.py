import os

import re
import pandas as pd
import numpy as np


from text_targets import partial_trauma_targets, exact_trauma_targets, fp_trauma_phrases, negative_hemorrhage_phrases, rescue_phrases
from import_data import import_radiology_reports, rename_radiology_reports_columns 
from export_data import save_dataset
from apply_targets import sentence_has_target, report_has_target

#todo: 
# add flags/annotations/separate file for which words/phrases were flagged? 
# add regex notes in docs (documentation folder)
# add docstrings and documentation within this/other scripts
# return/save multiple outputs:potential_trauma_fp? 

def traumascanner(path_to_csv,
                  path_to_save,
                  patient_id_column, 
                  scan_id_column,
                  text_column,
                  eval_partial_trauma_targets = True, 
                  eval_exact_trauma_targets = True):

    # import csv of radiology reports
    rad_reports = import_radiology_reports(path_to_csv)

    # standardize column names
    rad_reports = rename_radiology_reports_columns(rad_reports, patient_id_column, scan_id_column, text_column)

    ## partial-text matching
    if eval_partial_trauma_targets == True:
        print('eval partial_trauma_targets')
        potential_tbi_trauma = rad_reports[rad_reports['report_text'].str.contains('|'.join(partial_trauma_targets), case = False, regex = True)]
    
    ## exact-text matching
    if eval_exact_trauma_targets == True:
        print('eval exact_trauma_targets')
        # initialize an empty DataFrame to store the results
        exact_results_df = pd.DataFrame()

        for word in exact_trauma_targets:
            exact_match_result = rad_reports[rad_reports["report_text"].str.contains(fr'\b{word}\b', case=False, regex=True)]
            exact_results_df = pd.concat([exact_results_df, exact_match_result])

    # combine the dataframe of reports that matched our exact or partial-text matching criteria
    if eval_partial_trauma_targets == True & eval_exact_trauma_targets == True:
        print('combining potential and exact matches')
        report_matches = [potential_tbi_trauma, exact_results_df]

        # combine dataframes and drop any duplicated reports which may appear in both
        potential_tbi_trauma_reports = pd.concat(report_matches).drop_duplicates()

        ### Remove likely/uncertain false positives for trauma

        # When devising this method, we noticed that some reports were returned if there was a phrase such as 'No history of trauma'. 
        # Previously, I thought the downstream regex for stratifying patients with and without hemorrhage would ensure these patients were not included in our post-traumatic hemorrhage cohort, 
        # but sometimes, these patients have what appears to be spontaneous / post-operative hemorrhage from non-trauma sources. 
        # Thus, this step attempts to ensure that we only maintain patients who we are highly confident are being evaluated for traumatic brain injury.
        # 
        # This method will remove some patients who did have a trauma type injury as mentioned. 
        # For example, a patient may have a MVC, however, the radiologist might write: "no evidence of recent traumatic injury". 
        # This is okay, because the overall objective is to identify patients with post-traumatic hemorrhage. 
        print('identifying reports that are false positives for trauma')
        potential_trauma_fp = potential_tbi_trauma_reports[potential_tbi_trauma_reports['report_text'].apply(report_has_target, target_sets=fp_trauma_phrases)]

        ## **Remove the likely FP reports from the `potential_tbi_trauma_reports`**

        # remove the reports that match the regex pattern above
        potential_tbi_trauma_reports = potential_tbi_trauma_reports[~(potential_tbi_trauma_reports['report_text'].apply(report_has_target, target_sets=fp_trauma_phrases))]

        ### Identify post-traumatic hemorrhage

        # The set of regular expressions curated below aims to leverage common phrases and templated language that 
        # radiologists use to describe the ***absence*** of hemorrhage or intrancranial abnormalities. 
        # This list was devised during my chart reviews and sensitivity analyses as I reviewed reports and saw the type
        # of language commonly repeated to describe the absence of any hemorrhage.

        # this will identify all reports with no hemorrhage
        # for this process; we will create an abbreviated version of the larger dataset `potential_tbi_trauma_reports` and apply our `target_sets`
        print('identify and remove reports that indicate an absence of post-traumatic hemorrhage')
        potential_tbi_no_hem = potential_tbi_trauma_reports[['unique_study_id', 'report_num', 'report_text']].drop_duplicates()
        potential_tbi_no_hem = potential_tbi_no_hem[potential_tbi_no_hem['report_text'].apply(report_has_target, target_sets=negative_hemorrhage_phrases)]

        # print number of reports flagged as no traumatic hemorrhage
        print('num unique reports without hemorrhage', len(potential_tbi_no_hem[['report_num']].drop_duplicates()))
        print('num unique patients without no hemorrhage', len(potential_tbi_no_hem[['unique_study_id']].drop_duplicates()))

        #### Return patients with likely hemorrhage

        #Next, we will merge the patients with potentially no hemorrhage, with the original `potential_tbi_trauma_reports` dataset, 
        # in order to return the patients with likely post-traumatic hemorrhage
        print('filter dataset for patients with likely post-traumatic hemorrhage')
        potential_tbi_hem = pd.merge(potential_tbi_trauma_reports, 
                                     potential_tbi_no_hem,
                                     indicator = True, how = 'left').query('_merge=="left_only"').drop('_merge', axis=1)
        
        print('printing sample size of reports and patients before excluding the no hemorrhage patients')
        print('number of unique reports with potential post-traumatic hemorrhage:', len(potential_tbi_hem[['report_num']].drop_duplicates()))
        print('number of unique patients with potential post-traumatic hemorrhage:', len(potential_tbi_hem[['unique_study_id']].drop_duplicates()))

        # **Rescue reports** 
        # Next, we will rescue reports that may have been excluded do the regex rules that excluded reports with phrases of negation
        rescue_additional_reports = potential_tbi_no_hem[potential_tbi_no_hem['report_text'].apply(report_has_target, target_sets=rescue_phrases)]
        print('number of rescued reports:', len(rescue_additional_reports[['report_num']].drop_duplicates()))

        # add rescued reports to the `potential_tbi_hem` dataset
        tbi_reports_list = [potential_tbi_hem, rescue_additional_reports]

        post_traumatic_hem_reports = pd.concat(tbi_reports_list)
        print('number of total reports:', len(post_traumatic_hem_reports))
        print('number of unique reports with post-traumatic hemorrhage:', len(post_traumatic_hem_reports[['report_num']].drop_duplicates()))
        print('number of unique patients with post-traumatic hemorrhage:', len(post_traumatic_hem_reports[['unique_study_id']].drop_duplicates()))

        # save post-traumatic hemorrhage reports
        print('saving processed dataset to:', path_to_save)
        save_dataset(processed_dataset = post_traumatic_hem_reports, path_to_save = path_to_save)

        return(post_traumatic_hem_reports) 
    


