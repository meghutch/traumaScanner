import pandas as pd

# prepare rad reports
def import_radiology_reports(path_to_csv):
    rad_reports = pd.read_csv(path_to_csv)
    return(rad_reports)

def rename_radiology_reports_columns(rad_reports, patient_id_column, scan_id_column, text_column):
    rad_reports = rad_reports.rename(columns={patient_id_column: "unique_study_id", scan_id_column: "report_num", text_column: "report_text"})
    return(rad_reports)

