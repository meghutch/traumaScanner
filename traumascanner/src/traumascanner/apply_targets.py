import pandas as pd
import re

## functions to apply regex; created with help from chatgpt
# Function to check if a sentence contains any words from the target_set
def sentence_has_target(sentence, target_sets):
    return any(all(re.search(target, sentence) for target in target_set) for target_set in target_sets)

# Function to check if a report contains at least one sentence with any words from the target_set
def report_has_target(report, target_sets):
    sentences = report.split('.')
    return any(sentence_has_target(sentence, target_sets) for sentence in sentences)

# Function to check if a sentence contains all required words from any target set and return matching sentences
def get_matching_sentences(report, regex_phrases):
    sentences = report.split('.')
    matches = []
    for sentence in sentences:
        if any(all(re.search(target, sentence) for target in regex_phrases) for regex_phrases in regex_phrases):
            matches.append(sentence.strip())
    return matches

# function to identify the regular expressions that matched to a report
def find_matching_phrases(report, regex_phrases):
    if not isinstance(report, str):  # Ensure the report is a string
        return []
    
    matched_phrases = []
    for phrase in regex_phrases:
        if re.search(phrase, report):
            matched_phrases.append(phrase)
    return matched_phrases

