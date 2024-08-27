# traumascanner

Identify radiology text-reports of patients with post-traumatic hemorrhage

## Installation

```bash
$ pip install traumascanner
```

## Usage

Use `traumaScanner()` to identify patients with post-traumatic hemorrhage from radiology text reports. 

`traumaScanner()` is a key-word matching/regular expression (regex) and rules-based algorithm for identifying patients with post-traumatic hemorrhage after a traumatic brain injury (TBI). 

In brief, the algorithm functions as follows: 


1) Identifies radiology reports with at least one of the provided set of trauma-related keywords
2) Considers negation to remove false positive trauma related reports
3) Identifies and removes reports without hemorrhage

The function will output the following csv files:

- 01_potential_trauma_reports.csv - all radiology reports which matched at least one keyword
- 02_false_postive_trauma_reports.csv - the subset of potential_trauma_reports identified as being likely false positive for trauma
- 03_trauma_no_hemorrhage_reports.csv - the subset of potential_trauma_reports which had no hemorrhage
- 04_resucued_reports.csv - the subset of trauma_no_hemorrhage_reports which were likely false negatives
- 05_post_traumatic_hemorrhage_reports - the complete set of post-traumatic hemorrhage reports identified via the `traumaScanner()` algorithm. 




## License

`traumascanner` was created by Meghan Hutch. It is licensed under the terms of the MIT license.

## Credits

`traumascanner` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
