import pandas as pd

from text_targets import partial_trauma_targets, exact_trauma_targets, fp_trauma_phrases, negative_hemorrhage_phrases

# function to add targets to list
def add_target_list(target_list_to_update, list_of_new_targets):

    # apply function if `target_list_to_update` has been selected appropriately as the partial or exact list
    lists_of_text_targets = [partial_trauma_targets, exact_trauma_targets]

    if target_list_to_update in lists_of_text_targets:
        print('adding new targets')

        # Add new targets to the list_to_update
        target_list_updated = target_list_to_update + list_of_new_targets

        # drop any duplicates
        target_list_updated = list(set(target_list_updated))

        # sort list alphabetically
        target_list_updated = sorted(target_list_updated)

        # print number of targets
        print('total number of targets', len(target_list_updated))

        return target_list_updated  
    else:
        print('Error: Please select a valid list to add words to from one of [partial_trauma_targets, exact_trauma_targets]')

        
# update list of regular expressions to the default lists of regular expressions `fp_trauma_phrases' or 'negative_hemorrhage_phrases'
def add_regex_list(default_regex, list_of_new_regex):  
    
    # apply function if `default_regex` has been selected appropriately as either 'fp_trauma_phrases' or the 'negative_hemorrhage_phrases'
    lists_of_default_regex = [fp_trauma_phrases, negative_hemorrhage_phrases]

    if default_regex in lists_of_default_regex:
        print('adding new regex phrases')

        # Add new regex to the list_to_update
        regex_list_updated = default_regex + list_of_new_regex

        # drop any duplicates
        regex_list_updated = list(set(regex_list_updated))

        # sort list alphabetically
        regex_list_updated = sorted(regex_list_updated)

        # print number of regex phrases
        print('total number of regex phrases', len(regex_list_updated))

        return regex_list_updated  
    else:
        print('Error: Please select a valid list of regex phrases from either [fp_trauma_phrases, negative_hemorrhage_phrases]')