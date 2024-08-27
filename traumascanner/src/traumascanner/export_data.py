import pandas as pd

def save_dataset(potential_tbi_trauma_reports, potential_trauma_fp, potential_tbi_no_hem, rescue_additional_reports, post_traumatic_hem_reports, path_to_output_dir):
     
    potential_tbi_trauma_reports.to_csv(path_to_output_dir + '/01_potential_trauma_reports.csv', index = False)
    potential_trauma_fp.to_csv(path_to_output_dir + '/02_false_postive_trauma_reports.csv', index = False)
    potential_tbi_no_hem.to_csv(path_to_output_dir + '/03_trauma_no_hemorrhage_reports.csv', index = False)
    rescue_additional_reports.to_csv(path_to_output_dir + '/04_resucued_reports.csv', index = False)
    post_traumatic_hem_reports.to_csv(path_to_output_dir + '/05_post_traumatic_hemorrhage_reports.csv', index = False)
