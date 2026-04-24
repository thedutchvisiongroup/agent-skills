# Print Setup

Configure page layout, margins, and print options for professional printed output.

## Page Orientation and Size

```python
from openpyxl.worksheet.page import PageMargins

# Landscape orientation, fit to one page wide
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0  # 0 = unlimited pages tall
ws.sheet_properties.pageSetUpPr.fitToPage = True

# Paper size (1 = Letter, 9 = A4)
ws.page_setup.paperSize = 9  # A4
```

## Print Area

```python
# Set print area to a specific range
ws.print_area = "A1:H50"

# Multiple print areas
ws.print_area = "A1:H25,A30:H50"

# Clear print area
ws.print_area = None
```

## Page Margins

```python
ws.page_margins = PageMargins(
    left=0.5,    # inches
    right=0.5,
    top=0.75,
    bottom=0.75,
    header=0.3,
    footer=0.3,
)
```

## Print Options

```python
# Center content on page
ws.print_options.horizontalCentered = True
ws.print_options.verticalCentered = False

# Print gridlines
ws.print_options.gridLines = True

# Print row/column headings (A, B, C... / 1, 2, 3...)
ws.print_options.headings = True
```

## Repeat Rows/Columns on Every Page

```python
# Repeat header row on every printed page
ws.print_title_rows = "1:1"

# Repeat first two columns on every page
ws.print_title_cols = "A:B"
```

## Page Breaks

```python
from openpyxl.worksheet.pagebreak import Break, RowBreak

# Add a page break before row 25
ws.row_breaks = RowBreak()
ws.row_breaks.append(Break(id=25))
```
