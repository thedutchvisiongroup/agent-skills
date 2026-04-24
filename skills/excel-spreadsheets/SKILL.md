---
name: excel-spreadsheets
description: "Creates, analyzes, and formats Excel (.xlsx) spreadsheets with live formulas, charts, pivot tables, and professional styling. Use when working with Excel files, spreadsheets, .xlsx, openpyxl, financial models, or tabular data exports."
---

## Before You Start

You MUST confirm these details before building or modifying an Excel file:

1. **Output filename and location** — where to save the .xlsx file
2. **Key structure** — which sheets, what data goes where
3. **Audience** — internal team, external client, or print-ready
4. **Formatting preferences** — branding colors, specific styles, or use defaults
5. **Data source** — manual input, CSV, database, API, or existing file

Formulas MUST always be live Excel formulas, never Python-computed constants.

## When NOT to Use This Skill

- **CSV/TSV files** — use standard Python csv module; no Excel formatting needed
- **Large datasets (100k+ rows)** — consider a database or Parquet; Excel has a ~1M row limit
- **Real-time dashboards** — use a BI tool (Metabase, Grafana), not static spreadsheets
- **PDF reports** — use a PDF generation tool; Excel is not a layout engine

## Dependencies

- **openpyxl** — Excel file creation and formatting (`pip install openpyxl`)
- **pandas** — data analysis and bulk operations (`pip install pandas`)
- **LibreOffice** — required for `scripts/recalc.py` and `scripts/pivot_table.py` (must be installed and on PATH)

# Requirements for Outputs

**Design defaults:** Use Calibri 11pt, black text on white background. Reserve color for emphasis (header rows, key totals). Apply branding colors only when explicitly requested by the user. Ensure readable spacing between sections.

## User-Facing Delivery

When reporting back to the user:

- describe what the spreadsheet does, not which library created it
- mention the structure, formulas, sheets, charts, and outputs in plain language
- say that calculations update automatically when inputs change when that is true
- do not narrate internal implementation details unless the user explicitly asks

## All Excel files

### Professional Font
- Use a consistent, professional font (e.g., Calibri, Arial) for all deliverables unless otherwise instructed by the user

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates (when updating templates)
- Study and EXACTLY match existing format, style, and conventions when modifying files
- Never impose standardized formatting on files with established patterns
- Existing template conventions ALWAYS override these guidelines

### Formulas Over Hardcoded Values

Every derived value must be an Excel formula, not a Python-computed constant. The spreadsheet must recalculate when inputs change.

```python
# WRONG — value dies when inputs change
margin = (revenue - cogs) / revenue
ws["D5"] = margin

# RIGHT — formula stays live
ws["D5"] = "=(B5-C5)/B5"
ws["D5"].number_format = "0.0%"
```

```python
# WRONG — snapshot of a sum
ws["F20"] = df["Amount"].sum()

# RIGHT — Excel does the aggregation
ws["F20"] = "=SUM(F2:F19)"
ws["F20"].number_format = "#,##0"
```

This applies to totals, ratios, growth rates, averages, ranks — anything Excel can compute. Hardcoded numbers are acceptable only for raw input data and sourced assumptions.

## Financial Models

For industry-standard color coding, number formatting, formula construction rules, and documentation requirements, see [references/financial-models.md](references/financial-models.md).

## Structure & Usability

### Sheet Organization

| Guideline | Recommendation |
|-----------|----------------|
| Sheet order | Summary/Overview first, then supporting detail (General → Specific) |
| Sheet count | 3-5 ideal, max 7 |
| Naming | Descriptive names (e.g., "Revenue Data", not "Sheet1") |

**Information architecture**:
- Overview sheet should stand alone — user understands the main message without opening other sheets
- Progressive disclosure: summary first, details available for those who want to dig deeper
- Consistent structure across sheets: same layout patterns, same starting positions

### Layout Rules

| Element | Position |
|---------|----------|
| Left margin | Column A empty (width 3) |
| Top margin | Row 1 empty |
| Content start | Cell B2 |
| Section spacing | 1 empty row between sections |
| Table spacing | 2 empty rows between tables |
| Charts | Below tables (2 rows gap), or right of related table |

Charts must never overlap each other or tables.

```python
ws.column_dimensions['A'].width = 3
```

### Standalone Text Rows

For rows with a single text cell (titles, descriptions, notes), text naturally extends into empty cells to the right. However, text is **clipped** if right cells contain any content (including spaces).

| Condition | Action |
|-----------|--------|
| Right cells guaranteed empty | No action needed—text extends naturally |
| Right cells may have content | Merge cells to content width, or wrap text |
| Text exceeds content area width | Wrap text + set row height manually |

Common cases requiring merge:
- Titles and subtitles (usually span full content width)
- Section headers (span width of related table)
- Long bullet points or insight text
- Notes and disclaimers

```python
from openpyxl.utils import get_column_letter

# Merge title across content width
last_col = 8  # Match table width
ws.merge_cells(f'B2:{get_column_letter(last_col)}2')
ws['B2'] = "Report Title"

# Wrapped text with manual row height
ws['B20'].alignment = Alignment(wrap_text=True)
ws.row_dimensions[20].height = 30  # Adjust based on content
```

### Navigation

For workbooks with 3+ sheets, add a sheet index with hyperlinks on the Overview.

**Internal links** (cross-sheet references) — use `Hyperlink` class for reliability:
```python
from openpyxl.worksheet.hyperlink import Hyperlink

cell = ws.cell(row=6, column=2, value="Revenue Data")
cell.hyperlink = Hyperlink(ref=cell.coordinate, location="'Revenue Data'!A1")
cell.font = Font(color='0000FF', underline='single')
```

**External links** (source documents):
```python
cell.hyperlink = "https://example.com/source"
cell.font = Font(color='0000FF', underline='single')
```

### Freeze Panes

For tables with >10 rows, freeze below the header row:

```python
ws.freeze_panes = f'A{header_row + 1}'
```

### Filters

For tables with >20 rows, enable auto-filter to allow users to explore data:

```python
from openpyxl.utils import get_column_letter

# Apply filter to entire data range
ws.auto_filter.ref = f"A{header_row}:{get_column_letter(last_col)}{last_row}"
```

### Excel Tables

For any contiguous data range with one header row + data rows, always create a formal Excel Table object instead of manual formatting. Tables provide automatic row banding, filters, structured references (e.g., `=SUM(Table1[Revenue])`), and auto-updating styles when rows are added or deleted. This makes manual alternating-row fills, manual auto-filter setup, and manual header styling unnecessary. Each sheet can have its own Table (use unique `displayName` values).

When the sheet is purely a data table, data should start at A1 — the B2 layout rule applies to dashboards/reports with titles, not raw data tables. Use `openpyxl.worksheet.table.Table` with `TableStyleInfo` to create the table.

When editing an existing file, **check for Table objects** (`ws.tables`) before writing formulas. If tables exist, **use structured table references in all formulas** instead of raw cell ranges. For example, use `=AVERAGE(PeopleData[Salary])` instead of `=AVERAGE('Sheet1'!N2:N500)`. For VLOOKUP, use `TableName[#All]` as the lookup array: `=VLOOKUP(A2,PeopleData[#All],3,FALSE)`. Structured references auto-adjust when rows are added or removed.

### Pre-sorting

Pre-sort by most meaningful dimension:
- Rankings → by value descending
- Time series → by date ascending
- Alphabetical → when no clear priority

```python
df = df.sort_values('revenue', ascending=False)
```

### Data Context

Every dataset needs context for the user to trust and understand it:

| Element | Location | Example |
|---------|----------|---------|
| Data source | Footer or notes | "Source: Company 10-K, FY2024" |
| Time range | Near title or subtitle | "Data from Jan 2022 - Dec 2024" |
| Generation date | Footer | "Generated: 2024-01-15" |
| Definitions | Notes section | "Revenue = Net sales excluding returns" |

```python
# Add data context in footer area
ws.cell(row=last_row + 3, column=1, value="Source: Company Annual Report 2024")
ws.cell(row=last_row + 4, column=1, value=f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
```

### Content Completeness

| Check | Action |
|-------|--------|
| Missing values | Show as blank or "N/A", never 0 unless actually zero |
| Units | Include in header (e.g., "Revenue ($M)", "Growth (%)") |
| Abbreviations | Define on first use or in notes section |
| Calculated fields | Use formulas so users can audit; add note if formula is complex |

### Number Formatting

**Critical**: Formula cells need `number_format` too — they display raw precision unless explicitly formatted.

```python
# WRONG: Formula cell without number_format
ws['C10'] = '=C7-C9'  # Displays 14.123456789

# CORRECT: Always set number_format for formula cells
ws['C10'] = '=C7-C9'
ws['C10'].number_format = '#,##0.0'  # Displays 14.1
```

Apply consistent formatting to entire columns (both values and formulas):

| Data Type | Format Code | Example |
|-----------|-------------|---------|
| Integer | `#,##0` | 1,234,567 |
| Decimal (1) | `#,##0.0` | 1,234.6 |
| Percentage | `0.0%` | 12.3% |
| Currency | `$#,##0.00` | $1,234.56 |

### Alignment

| Content | Horizontal | Notes |
|---------|------------|-------|
| Headers | Center | |
| Numbers | Right | |
| Short text | Center | Single words, status values |
| Long text | Left | Sentences, descriptions; use `indent=1` for padding |
| Dates | Center | |

```python
# Numbers right-aligned
cell.alignment = Alignment(horizontal='right', vertical='center')

# Text with padding
cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)
```

### Column Width

Calculate width based on content. Only consider data cells, not titles or notes:

```python
def set_column_width(ws, col, min_width=12, max_width=50, padding=2):
    max_len = 0
    for row in ws.iter_rows(min_col=col, max_col=col):
        for cell in row:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))

    width = min(max(max_len + padding, min_width), max_width)
    ws.column_dimensions[get_column_letter(col)].width = width
```

**Guidelines**:
| Column Type | Min Width | Notes |
|-------------|-----------|-------|
| Labels/Text | 15 | First column usually |
| Numbers | 12 | Allow room for formatting (commas, negatives) |
| Dates | 12 | Standard date format |
| Long text | 20-40 | Consider wrapping if exceeds 40 |

### Row Height

Set row heights explicitly for consistency (openpyxl doesn't auto-adjust):

```python
ws.row_dimensions[1].height = 30   # Title row
ws.row_dimensions[2].height = 20   # Subtitle row
ws.row_dimensions[3].height = 25   # Header row
# Data rows: default 15-18 is usually fine
```

### Data Visualization

For data bars, color scales, conditional formatting, charts, and comparison columns, see [references/data-visualization.md](references/data-visualization.md).

# Scripts

LibreOffice is pre-installed. Both scripts configure it automatically on first run.

Use **pandas** for data analysis and bulk operations. Use **openpyxl** for formulas, formatting, and Excel-specific features. After saving, always recalculate:

## Recalculating Formulas

openpyxl writes formulas as strings but does not evaluate them. The `scripts/recalc.py` script drives LibreOffice headless to recalculate all formulas and then scans every cell for Excel errors.

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

On success:
```json
{"status": "success", "total_errors": 0, "total_formulas": 42, "error_summary": {}}
```

When errors remain:
```json
{
  "status": "errors_found",
  "total_errors": 2,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {"count": 2, "locations": ["Sheet1!B5", "Sheet1!C10"]}
  }
}
```

If `errors_found`, fix the referenced cells and re-run. Common errors: `#REF!` (bad cell reference), `#DIV/0!` (division by zero), `#VALUE!` (wrong type), `#NAME?` (unknown function).

## Pivot Tables

openpyxl cannot create pivot tables. Use `scripts/pivot_table.py`, which creates real, interactive Excel pivot tables via LibreOffice's DataPilot engine.

```bash
# Create a pivot table
python scripts/pivot_table.py create output.xlsx '{
    "source_sheet": "Data",
    "target_sheet": "Revenue Pivot",
    "pivot_name": "RevPivot",
    "row_fields": ["Region", "Product"],
    "column_fields": ["Quarter"],
    "data_fields": [{"name": "Revenue", "function": "SUM"}]
}'

# Delete a pivot table
python scripts/pivot_table.py delete output.xlsx "Data" "RevPivot"
```

Config fields:
- `source_sheet`: Sheet containing the source data (must have headers in row 1)
- `target_sheet`: Sheet where the pivot table will be created (created automatically if it doesn't exist)
- `pivot_name`: Unique name for the pivot table
- `source_range`: Optional, e.g. `"A1:E100"`. Defaults to the full used area of the source sheet
- `row_fields`: Fields to use as row labels
- `column_fields`: Fields to use as column labels
- `data_fields`: Fields to aggregate, each with `name` and `function` (SUM, COUNT, AVERAGE, MAX, MIN, PRODUCT, STDEV, STDEVP, VAR, VARP). Each field name can only appear once — for multiple aggregations on the same column, create separate pivot tables
- `page_fields`: Optional filter fields

The resulting pivot tables are fully interactive in Excel — users can drag fields, filter, and refresh.

To edit a pivot table, recreate it with the new configuration using a new `pivot_name`.

Workflow with pivot tables:
1. Create/modify the spreadsheet with openpyxl (data, formulas, formatting)
2. Save the file
3. Run `pivot_table.py create` to add each pivot table
4. Continue modifying with openpyxl if needed — existing pivots are preserved
5. Run `recalc.py` to recalculate formulas

Multiple pivot tables can be added by running the script multiple times with different configs.

## Formula Verification Checklist

Quick checks to ensure formulas work correctly:

### Essential Verification
- [ ] **Test 2-3 sample references**: Verify they pull correct values before building full model
- [ ] **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
- [ ] **Row offset**: Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)

### Common Pitfalls
- [ ] **NaN handling**: Check for null values with `pd.notna()`
- [ ] **Far-right columns**: FY data often in columns 50+
- [ ] **Multiple matches**: Search all occurrences, not just first
- [ ] **Division by zero**: Check denominators before using `/` in formulas (#DIV/0!)
- [ ] **Wrong references**: Verify all cell references point to intended cells (#REF!)
- [ ] **Cross-sheet references**: Use correct format (Sheet1!A1) for linking sheets

### Formula Testing Strategy
- [ ] **Start small**: Test formulas on 2-3 cells before applying broadly
- [ ] **Verify dependencies**: Check all cells referenced in formulas exist
- [ ] **Test edge cases**: Include zero, negative, and very large values

# Additional Features

- **Data validation** (dropdowns, input constraints): See [references/data-validation.md](references/data-validation.md)
- **Print setup** (page layout, margins, orientation): See [references/print-setup.md](references/print-setup.md)
- **Sheet protection** (lock structure, unlock input cells): See [references/sheet-protection.md](references/sheet-protection.md)
- **Named ranges** (formula clarity, validation sources): See [references/named-ranges.md](references/named-ranges.md)

# Pitfalls

## openpyxl
- **`data_only=True` destroys formulas on save** — opening with `data_only=True` replaces formula strings with cached values. Never save a workbook opened this way; use it only for reading computed results.
- **Cell indices are 1-based** — `row=1, column=1` is cell A1. DataFrame row 5 = Excel row 6.
- **Formulas are stored as strings, not evaluated** — openpyxl does not compute formula results. Always run `recalc.py` after writing formulas.
- **Large files** — use `read_only=True` for reading or `write_only=True` for writing to avoid loading the entire file into memory.

## pandas
- **Type inference** — specify dtypes to avoid silent coercion: `pd.read_excel('file.xlsx', dtype={'id': str})`
- **Large files** — read only needed columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- **Dates** — parse explicitly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`
