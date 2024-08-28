import os

import re
import pandas as pd
import numpy as np


from traumascanner.text_targets import partial_trauma_targets, exact_trauma_targets, fp_trauma_phrases, fp_trauma_phrases_strings, negative_hemorrhage_phrases, negative_hemorrhage_phrases_strings, rescue_phrases
from traumascanner.import_data import import_radiology_reports, rename_radiology_reports_columns 
from traumascanner.export_data import save_dataset
from traumascanner.apply_targets import sentence_has_target, report_has_target, get_matching_sentences, find_matching_phrases

def traumascanner(path_to_data,
                  path_to_output_dir,
                  patient_id_column, 
                  scan_id_column,
                  text_column,
                  eval_partial_trauma_targets = True, 
                  eval_exact_trauma_targets = True):

    # import csv of radiology reports
    rad_reports = import_radiology_reports(path_to_data)

    # standardize column names
    rad_reports = rename_radiology_reports_columns(rad_reports, patient_id_column, scan_id_column, text_column)
    
    ## identify trauma reports with key-word matching
    
    # partial-text matching
    if eval_partial_trauma_targets == True:
        print('Searching for radiology reports with partial matches to trauma target keyword list')
    
        # create a copy of radiology report dataframe
        rad_reports_partial = rad_reports.copy()
    
        # Create a new column to store the matched trauma-related words
        rad_reports_partial['partial_matched_trauma_words'] = ''

        # Iterate over each report in the DataFrame
        for idx, report in rad_reports_partial['report_text'].iteritems():
            # Create a list of trauma-related words found in the report
            found_trauma_words = [word for word in partial_trauma_targets if pd.notna(report) and re.search(word, report, re.IGNORECASE)]

            # Store the list of found words in the 'matched_trauma_words' column
            rad_reports_partial.at[idx, 'partial_matched_trauma_words'] = found_trauma_words

        # Optionally, filter out the rows where no trauma-related words were found
        partial_matched_reports = rad_reports_partial[rad_reports_partial['partial_matched_trauma_words'].str.len() > 0]
        
        #print estimated number of potential reports
        print('Est. number of partially matched reports:', len(partial_matched_reports))
              
    ## exact-text matching
    if eval_exact_trauma_targets == True:
        print('Searching for radiology reports with exact matches to trauma target keyword list')
    
        # create a copy of radiology report dataframe
        rad_reports_exact = rad_reports.copy()
        
        # initialize an empty DataFrame to store the results
        exact_results_df = pd.DataFrame()

        rad_reports_exact['exact_matched_trauma_words'] = ''

        # Iterate over each report in the DataFrame
        for idx, report in rad_reports_exact['report_text'].iteritems():
            # Create a list of words found in the report
            found_words = [word for word in exact_trauma_targets if pd.notna(report) and re.search(fr'\b{word}\b', report, re.IGNORECASE)]

            # Store the list of found words in the 'matched_trauma_words' column
            rad_reports_exact.at[idx, 'exact_matched_trauma_words'] = found_words

        # Optionally, filter out the rows where no trauma-related words were found
        exact_matched_reports = rad_reports_exact[rad_reports_exact['exact_matched_trauma_words'].str.len() > 0]
        
        #print estimated number of potential reports
        print('Est. number of exact matched reports:', len(exact_matched_reports))

    # combine the dataframe of reports that matched our exact or partial-text matching criteria
    if eval_partial_trauma_targets == True & eval_exact_trauma_targets == True:
        
        print('combining potential and exact matches')
        report_matches = [partial_matched_reports[['unique_study_id', 'report_num', 'report_text']], 
                          exact_matched_reports[['unique_study_id', 'report_num', 'report_text']]]

        # combine dataframes and drop any duplicated reports which may appear in both
        reports_combined = pd.concat(report_matches).drop_duplicates()
        
        # combine the dataframe of reports that matched our exact or partial-text matching criteria
        reports_combined = pd.merge(reports_combined,
                                    exact_matched_reports[['unique_study_id', 'report_num', 'report_text', 'exact_matched_trauma_words']],
                                    how = 'left')

        reports_combined = pd.merge(reports_combined,
                                    partial_matched_reports[['unique_study_id', 'report_num', 'report_text', 'partial_matched_trauma_words']],
                                    on = ['unique_study_id', 'report_num', 'report_text'],
                                    how = 'left')
        
        # modify strings
        reports_combined['exact_matched_trauma_words'] = reports_combined['exact_matched_trauma_words'].astype('str').str.strip('[]')
        reports_combined['partial_matched_trauma_words'] = reports_combined['partial_matched_trauma_words'].astype('str').str.strip('[]')
        
        # combine dataframes and drop any duplicated reports which may appear in both
        potential_tbi_trauma_reports = reports_combined.drop_duplicates()

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
        potential_trauma_fp = potential_tbi_trauma_reports[potential_tbi_trauma_reports['report_text'].apply(report_has_target, target_sets = fp_trauma_phrases)]

        # add annotations to indicate which sentences matched regular expressions
        # Apply the function to the DataFrame and create a new column with matching sentences
        potential_trauma_fp['matching_sentences'] = potential_trauma_fp['report_text'].apply(get_matching_sentences, regex_phrases = fp_trauma_phrases)

        # Filter rows where there is at least one matching sentence
        potential_trauma_fp = potential_trauma_fp[potential_trauma_fp['matching_sentences'].apply(bool)]
        
        # add annotations to indicate which phrases matched
        potential_trauma_fp['report_text'] = potential_trauma_fp['report_text'].astype('str')
        potential_trauma_fp['matching_regex'] = potential_trauma_fp['report_text'].apply(find_matching_phrases, regex_phrases = fp_trauma_phrases_strings)
        
        ## **Remove the likely FP reports from the `potential_tbi_trauma_reports`**

        # remove the reports that match the regex pattern above
        potential_tbi_trauma_reports = potential_tbi_trauma_reports[~(potential_tbi_trauma_reports['report_text'].apply(report_has_target, target_sets = fp_trauma_phrases))]
        
        print('number of patients after removing false trauma reports')
        print(len(potential_tbi_trauma_reports[['unique_study_id']].drop_duplicates()))
        print('number of reports after removing false trauma reports')
        print(len(potential_tbi_trauma_reports[['report_num']].drop_duplicates()))

        ### Identify post-traumatic hemorrhage

        # The set of regular expressions curated below aims to leverage common phrases and templated language that 
        # radiologists use to describe the ***absence*** of hemorrhage or intrancranial abnormalities. 
        # This list was devised during my chart reviews and sensitivity analyses as I reviewed reports and saw the type
        # of language commonly repeated to describe the absence of any hemorrhage.

        # this will identify all reports with no hemorrhage
        # for this process; we will create an abbreviated version of the larger dataset `potential_tbi_trauma_reports` and apply our `target_sets`
        print('identify and remove reports that indicate an absence of post-traumatic hemorrhage')
        potential_tbi_no_hem = potential_tbi_trauma_reports[['unique_study_id', 'report_num', 'report_text', 'exact_matched_trauma_words', 'partial_matched_trauma_words']].drop_duplicates()
        potential_tbi_no_hem = potential_tbi_no_hem[potential_tbi_trauma_reports['report_text'].apply(report_has_target, target_sets = negative_hemorrhage_phrases)]
        
        potential_tbi_no_hem['matching_sentences'] = potential_tbi_no_hem['report_text'].apply(get_matching_sentences, regex_phrases = negative_hemorrhage_phrases)

        # print number of reports flagged as no traumatic hemorrhage
        print('num unique reports without hemorrhage', len(potential_tbi_no_hem[['report_num']].drop_duplicates()))
        print('num unique patients without no hemorrhage', len(potential_tbi_no_hem[['unique_study_id']].drop_duplicates()))

        # add annotations to indicate which phrases matched
        potential_tbi_no_hem['report_text'] = potential_tbi_no_hem['report_text'].astype('str')
        potential_tbi_no_hem['matching_regex'] = potential_tbi_no_hem['report_text'].apply(find_matching_phrases, regex_phrases = negative_hemorrhage_phrases_strings)
            
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
        print('saving processed dataset to:', path_to_output_dir)
        save_dataset(potential_tbi_trauma_reports, potential_trauma_fp, potential_tbi_no_hem, rescue_additional_reports, post_traumatic_hem_reports, path_to_output_dir = path_to_output_dir)

        #return(post_traumatic_hem_reports, potential_trauma_fp) 
        return(potential_tbi_trauma_reports, potential_trauma_fp, potential_tbi_no_hem, rescue_additional_reports, post_traumatic_hem_reports)


