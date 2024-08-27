import re

# list of trauma related key-words for partial-text matching
partial_trauma_targets = ['trauma', 'fall', 'lacera', 'assault', 'gun', 'kick', 'gsw', 'punch',
                  'shot', 'mva', 'mvc', 'bike', 'vehicle', 'vehicular', 'collision', 'automobile']

# list of trauma related key-words for exact-text matching
exact_trauma_targets = ['auto', 'accidents', 'accident', 'hit', 'stab', 'stabbed', 'stabbing', 'slip', 'slipped', 'struck', 'car', 
                 'brain injury', 'head injury', 'fell', 'contrecoup', 'contracoup', 'coup', 'tSAH']

 # the following regex employs a positive lookahead assertion; 
 # it makes sure to remove sentences where 'No' comes before the words (recent|known|history|...), which also come before (trauma|traumatic)
fp_trauma_phrases = [
    [r'(?i)\b(no|negative)\b(?=.*(\b(recent|known|obvious|history|reported|definite)\b.*\b(trauma|traumatic)\b))'],
    [r'(?i)\b(vascular accident)\b'],
    [r'(?i)\b(anoxic brain injury)\b']
]

# add string based version to support annotation functions
fp_trauma_phrases_strings = [r'(?i)\b(no|negative)\b(?=.*(\b(recent|known|obvious|history|reported|definite)\b.*\b(trauma|traumatic)\b))',
                             r'(?i)\b(vascular accident)\b',
                             r'(?i)\b(anoxic brain injury)\b']


# Define the regular expression pattern for each of the expressions
# this set of patterns will be applied to each sentence of each report
negative_hemorrhage_phrases = [
    # detects sentences that contains the word no or negative before at least one of the following words (evidence|acute|negative), which also occur before the words (trauma|traumatic|hemorrhage|hematoma)
    # importantly, we ensure that if the word 'new' or 'additional' is present that we do not exclude it. Often these words are part of phrases that suggest there is hemorrhage
    [r'(?i)\b(no|negative)\b(?!.*\b(new|additional)\b).*?\b(evidence|acute|intracranial)\b.*?\b(trauma|traumatic|hemorrhage|hematoma)\b'],
    # detect matches without the previous qualifier (evidence|acute|intracranial) from above
    [r'(?i)\b(no|negative)\b(?:(?!(\bnew\b|\badditional\b)).)*\b(trauma|traumatic|hemorrhage|hematoma)\b'],
    # detects no acute findings
    # note: adding 'intracranial' as a prefix before 'findings' leads to two false positives; thus will not combine the two subsequent regex
    [r'(?i)\b(no|negative)\b(?=.*(\b(acute)\b.*\b(findings)\b))'],
    # detects no CT abnormalities
    [r'(?i)\b(no|negative)\b(?=.*(\b(intracranial|acute)\b.*\b(abnormality|abnormalities)\b))'],
    # detects no abnormality
    [r'(?i)\b(no|negative)\b(?=.*(\b(abnormality|abnormalities)\b))'],
    # detects negative|unremarkable head CT / negative finding
    [r'(?i)\b(unremarkable|negative)\b(?=.*(\b(exam|head\sCT|CT|study)\b))'],
    # detects normal exam
    [r'(?i)\b(normal study|normal CT|normal head CT|normal exam|normal head CT|normal noncontrast|normal plain)\b'],
    # detects no intracranial process - including acute might return us old scans that we may want to keep
    [r'(?i)\b(no|negative|without\sevidence)\b(?=.*(\b(intracranial)\b.*\b(process|pathology)\b))'],
    # remove exact phrases of the following:
    [r'(?i)\b(without acute intracranial abnormality)\b'],
    [r'(?i)\b(without evidence for acute abnormality)\b'],
    [r'(?i)\b(without acute abnormality)\b']
]


# add string based version to support annotation functions
negative_hemorrhage_phrases_strings = ['(?i)\\b(no|negative)\\b(?!.*\\b(new|additional)\\b).*?\\b(evidence|acute|intracranial)\\b.*?\\b(trauma|traumatic|hemorrhage|hematoma)\\b',
'(?i)\\b(no|negative)\\b(?:(?!(\\bnew\\b|\\badditional\\b)).)*\\b(trauma|traumatic|hemorrhage|hematoma)\\b',
 '(?i)\\b(no|negative)\\b(?=.*(\\b(acute)\\b.*\\b(findings)\\b))',
 '(?i)\\b(no|negative)\\b(?=.*(\\b(intracranial|acute)\\b.*\\b(abnormality|abnormalities)\\b))',
 '(?i)\\b(no|negative)\\b(?=.*(\\b(abnormality|abnormalities)\\b))',
 '(?i)\\b(unremarkable|negative)\\b(?=.*(\\b(exam|head\\sCT|CT|study)\\b))',
 '(?i)\\b(normal study|normal CT|normal head CT|normal exam|normal head CT|normal noncontrast|normal plain)\\b',
 '(?i)\\b(no|negative|without\\sevidence)\\b(?=.*(\\b(intracranial)\\b.*\\b(process|pathology)\\b))',
 '(?i)\\b(without acute intracranial abnormality)\\b',
 '(?i)\\b(without evidence for acute abnormality)\\b',
 '(?i)\\b(without acute abnormality)\\b']

# evaluate whether we are excluding patients with "no additional hemorrohage"
# try ensuring "No" prior to (additional|change|decrease) in (hematoma|hemorrhage|contusion)
# our regex also enables capturing `change, changed, changing (and similar matching with increase and decrease)
# we will also include the word hemorrhage; in this instance, we want to try and identify any reports that may have been false negative for post-traumatic hemorrhage
# contusion appears sensitive for brain trauma/potential hemorrhage 
rescue_phrases = [
    [r'(?i)\b(no|negative)\b(?=.*(\b(additional|(chang|increas|decreas)(e|ed|ing))\b.*\b(hematoma|hemorrhage|hemorrhagic|contusion)\b))']
]

