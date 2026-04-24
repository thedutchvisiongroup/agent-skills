# Data Visualization

## Data Bars

Compare magnitude within a column without leaving the cell:

```python
from openpyxl.formatting.rule import DataBarRule

# Blue data bars (default Excel blue)
rule = DataBarRule(
    start_type='min',
    end_type='max',
    color='4472C4'  # Excel default blue
)
ws.conditional_formatting.add('C5:C50', rule)
```

## Color Scales

Heatmap effect for matrices and ranges:

```python
from openpyxl.formatting.rule import ColorScaleRule

# White to blue gradient
rule = ColorScaleRule(
    start_type='min', start_color='FFFFFF',
    end_type='max', end_color='4472C4'
)
ws.conditional_formatting.add('D5:H20', rule)

# Three-color scale (low-mid-high)
rule = ColorScaleRule(
    start_type='min', start_color='F8696B',     # Red
    mid_type='percentile', mid_value=50, mid_color='FFEB84',  # Yellow
    end_type='max', end_color='63BE7B'          # Green
)
```

### When to Use

| Feature | Use Case |
|---------|----------|
| Data Bars | Numeric columns needing quick magnitude comparison |
| Color Scale (2-color) | Single metric ranges, distributions |
| Color Scale (3-color) | Performance data with good/neutral/bad interpretation |

## Conditional Formatting Rules

When a user asks to "highlight", "color", or "conditionally format" cells based on value thresholds, **always use Excel conditional formatting rules** (`CellIsRule`, `FormulaRule` from `openpyxl.formatting.rule`) instead of looping through cells and setting `PatternFill` directly. Static fills look the same visually but are not real conditional formatting — they don't update when values change, don't appear in Excel's conditional formatting manager, and can't be edited by the user.

## Charts

Place charts below tables with a 2-row gap, left-aligned with content:

```python
from openpyxl.chart import BarChart, LineChart, Reference

# Create chart
chart = BarChart()
chart.title = "Revenue by Region"
chart.style = 10  # Built-in style

# Set data and categories
data = Reference(ws, min_col=2, min_row=header_row, max_row=last_row)
cats = Reference(ws, min_col=1, min_row=header_row + 1, max_row=last_row)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)

# Size and position
chart.width = 15  # inches
chart.height = 7.5
ws.add_chart(chart, f"A{last_row + 3}")  # 2 rows below data
```

### Chart Type Selection

| Chart Type | Use When |
|------------|----------|
| Bar/Column | Comparing values across categories |
| Line | Time series, trends over time |
| Pie | Part-to-whole (≤6 categories only) |

### Preventing Overlap

Chart `width` and `height` are in centimeters, not rows. To place content after a chart without overlap:

```python
from math import ceil

# ~2 rows per cm of chart height (at default ~15pt row height)
rows_for_chart = ceil(chart.height * 2)
next_content_row = chart_row + rows_for_chart + 2  # 2-row gap
```

## Comparison Columns

For analytical reports, add calculated columns that surface insights:

| Column Type | Formula Pattern | Use Case |
|-------------|-----------------|----------|
| Change (Δ) | `=B2-A2` | Absolute difference |
| % Change | `=(B2-A2)/A2` | Relative growth |
| YoY Growth | `=(CurrentYear-PriorYear)/PriorYear` | Year-over-year |
| Rank | `=RANK(B2,$B$2:$B$100,0)` | Position in list |

```python
# Add YoY growth column
for row in range(data_start, data_end + 1):
    current = ws.cell(row=row, column=current_year_col).coordinate
    prior = ws.cell(row=row, column=prior_year_col).coordinate
    growth_cell = ws.cell(row=row, column=growth_col)
    growth_cell.value = f"=({current}-{prior})/{prior}"
    growth_cell.number_format = '0.0%'
```
