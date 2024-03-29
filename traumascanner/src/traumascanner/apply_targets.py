import pandas as pda
import re

## functions to apply regex; created with help from chatgpt
# Function to check if a sentence contains any words from the target_set
def sentence_has_target(sentence, target_sets):
    return any(all(re.search(target, sentence) for target in target_set) for target_set in target_sets)

# Function to check if a report contains at least one sentence with any words from the target_set
def report_has_target(report, target_sets):
    sentences = report.split('.')
    return any(sentence_has_target(sentence, target_sets) for sentence in sentences)
