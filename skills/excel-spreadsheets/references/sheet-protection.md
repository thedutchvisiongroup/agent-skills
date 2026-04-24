# Sheet Protection

Protect worksheet structure and cell contents while allowing specific user actions.

## Basic Protection

```python
# Enable sheet protection (no password)
ws.protection.sheet = True
ws.protection.enable()

# With password
ws.protection.password = "secret123"
ws.protection.sheet = True
```

## Selective Protection

Allow specific operations on a protected sheet:

```python
ws.protection.sheet = True
ws.protection.formatCells = False      # Allow cell formatting
ws.protection.formatColumns = False    # Allow column formatting
ws.protection.formatRows = False       # Allow row formatting
ws.protection.insertRows = False       # Allow inserting rows
ws.protection.sort = False             # Allow sorting
ws.protection.autoFilter = False       # Allow auto-filter
```

The `False` value means "not protected" — the user CAN perform that action.

## Unlocking Specific Cells

By default, all cells in a protected sheet are locked. Unlock input cells so users can edit them:

```python
from openpyxl.styles import Protection

# Unlock input cells before enabling sheet protection
for row in range(2, last_row + 1):
    ws.cell(row=row, column=2).protection = Protection(locked=False)

# Then enable sheet protection
ws.protection.sheet = True
```

Common pattern: Lock formula cells, unlock input cells.

## Workbook-Level Protection

```python
# Prevent adding/removing/renaming sheets
wb.security.lockStructure = True
wb.security.workbookPassword = "secret123"
```
