# Named Ranges

Create, use, and manage named ranges (defined names) for clearer formulas and data validation sources.

## Creating Named Ranges

```python
from openpyxl.workbook.defined_name import DefinedName

# Define a named range scoped to the workbook
ref = "Sheet1!$A$1:$A$50"
defn = DefinedName("ProductList", attr_text=ref)
wb.defined_names.add(defn)

# Define a named range scoped to a specific sheet
# Use localSheetId (0-indexed sheet position)
defn = DefinedName("LocalRange", attr_text="Sheet1!$B$2:$B$100", localSheetId=0)
wb.defined_names.add(defn)
```

## Using Named Ranges in Formulas

Named ranges make formulas self-documenting:

```python
# Instead of: ws["D2"] = "=SUM(B2:B100)"
ws["D2"] = "=SUM(Revenue)"

# Instead of: ws["E2"] = "=VLOOKUP(A2,Sheet2!$A:$C,3,FALSE)"
ws["E2"] = "=VLOOKUP(A2,ProductLookup,3,FALSE)"
```

## As Data Validation Sources

Named ranges work well as dropdown sources across sheets:

```python
from openpyxl.worksheet.datavalidation import DataValidation

# First create the named range
defn = DefinedName("StatusOptions", attr_text="Lookups!$A$1:$A$5")
wb.defined_names.add(defn)

# Then use it in data validation
dv = DataValidation(type="list", formula1="StatusOptions")
ws.add_data_validation(dv)
dv.add("C2:C100")
```

## Reading Named Ranges

```python
# List all defined names
for defn in wb.defined_names.definedName:
    print(f"{defn.name} -> {defn.attr_text}")

# Get a specific named range
defn = wb.defined_names.get("Revenue")
if defn:
    print(defn.attr_text)  # e.g., "Sheet1!$B$2:$B$100"
```

## Deleting Named Ranges

```python
wb.defined_names.delete("OldRange")
```
