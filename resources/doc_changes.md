# Change log

## V1.1.1 19/06/2024
- Wrapped up all modules

## V0.0.1 11/06/2024

### Added
- NLG Insights in place (4 types of recommendations in total)

## V0.0.1 04/06/2024

### Added

- `[asset/data/data_template]` Added 7 types of data template (xlsx)
- `[asset/data/data_filled]` Added 7 types of sample data filled (xlsx) to S3
    - [ ]  glucose
    - [ ]  blood pressure
    - [ ]  cholesterol level
    - [ ]  food intake
    - [ ]  hba1c
    - [ ]  insulin
    - [ ]  physical activity
- `[app.py]` created download page for both sample file and template files
- `[app.py]` add ability to handle all 8 types of data files

- auto generate uuid when creation of entry (doesnt work, reverted)
- change all id for records to entry_id
- currently uploaded_file_handling.py.data_insert_internal limit to 2 rows only for testing purpose
- Added a "Contact us.html" (hvnt finish)
- Added Loading animations to base.html

<!-- Tracy todo -->
- Dashboard backend (Patient)
- Dashboard backend (HP)
- Chat module
- insertion of data into kg