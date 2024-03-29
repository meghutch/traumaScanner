import pandas as pd

def save_dataset(processed_dataset, path_to_save):
     processed_dataset.to_csv(path_to_save, index = False)
