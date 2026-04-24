# Data Validation

Add input constraints and dropdown menus to Excel cells using openpyxl's `DataValidation`.

## List Validation (Dropdown Menus)

### Inline list

```python
from openpyxl.worksheet.datavalidation import DataValidation

dv = DataValidation(type="list", formula1='"Yes,No,N/A"', allow_blank=True)
dv.error = "Please select from the list"
dv.errorTitle = "Invalid Entry"
dv.prompt = "Choose an option"
dv.promptTitle = "Selection"

ws.add_data_validation(dv)
dv.add("B2:B100")
```

### Range-based list (from another sheet)

```python
from openpyxl.utils import quote_sheetname

dv = DataValidation(
    type="list",
    formula1=f"{quote_sheetname('Lookup')}!$A$1:$A$50",
)
ws.add_data_validation(dv)
dv.add("C2:C100")
```

## Numeric Constraints

```python
# Whole numbers between 1 and 100
dv = DataValidation(type="whole", operator="between", formula1=1, formula2=100)

# Decimal greater than 0
dv = DataValidation(type="decimal", operator="greaterThan", formula1=0)

# Date after a specific date
dv = DataValidation(type="date", operator="greaterThan", formula1="2024-01-01")
```

## Pitfalls

- **`showDropDown=True` hides the dropdown** — this is counterintuitive. The parameter name means "show the dropdown restriction indicator" which actually suppresses the arrow. Leave it at the default (`False`) to show the dropdown arrow.
- **Formula1 quoting** — inline lists MUST be wrapped in double quotes inside the formula string: `formula1='"A,B,C"'` (note the nested quotes).
- **Max 255 characters** — inline list values are limited to 255 characters total. For longer lists, use a range reference instead.
