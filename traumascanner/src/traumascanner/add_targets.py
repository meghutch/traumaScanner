import pandas as pd

from text_targets import partial_trauma_targets, exact_trauma_targets, fp_trauma_phrases, negative_hemorrhage_phrases

# function to add targets to list
def add_target_list(target_list_to_update, list_of_new_targets):

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
        print('Error: Please select a valid list from one of [partial_trauma_targets, exact_trauma_targets]')

# update list of regular expressions
# def add_phrases(list):  