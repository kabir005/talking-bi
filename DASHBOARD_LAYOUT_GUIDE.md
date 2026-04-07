# Dashboard Layout Guide - Power BI Style

## Layout System

### Grid System
- **12-column grid** (like Bootstrap and Power BI)
- **60px row height** for consistent sizing
- **16px margins** between tiles
- **Responsive** - adapts to container width

---

## KPI Card Design

### Visual Structure
```
┌─────────────────────────────────────┐
│ SALES                    (label)    │
│                                     │
│ $875,649.092            (value)     │
│                                     │
│ ↑ +12.5% vs prev        (trend)     │
│                                     │
│ ▁▂▃▄▅▆▇█               (sparkline) │
└─────────────────────────────────────┘
```

### Dimensions
- **Width:** 3 columns (25% of 12-column grid)
- **Height:** 3 row units (180px)
- **Padding:** 20px all sides

### Colors
- **Background:** Gradient from slate-800 to slate-900
- **Border:** slate-700
- **Label:** slate-400 (uppercase, small)
- **Value:** white (large, bold)
- **Trend Up:** emerald-400 (#34d399)
- **Trend Down:** rose-400 (#fb7185)
- **Sparkline:** Matches trend color

---

## Chart Tile Design

### Visual Structure
```
┌─────────────────────────────────────┐
│ ≡ Chart Title          ⛶ ⚙ ✕      │ Header
├─────────────────────────────────────┤
│                                     │
│                                     │
│         Chart Content               │ Body
│                                     │
│                                     │
└─────────────────────────────────────┘
```

### Header Elements
- **Grip Icon (≡):** Drag handle for rearranging
- **Title:** Chart name (truncated if too long)
- **Actions:**
  - ⛶ Fullscreen
  - ⚙ Settings
  - ✕ Delete

### Dimensions
- **Width:** Variable (4, 6, or 12 columns)
- **Height:** Variable (4, 5, or 6 row units)
- **Padding:** 16px all sides

### Colors
- **Background:** Gradient from slate-800 to slate-900
- **Border:** slate-700
- **Header:** slate-800/50 with bottom border
- **Title:** white
- **Icons:** slate-400, hover to white

---

## Preset Layouts

### Executive Preset

**Purpose:** High-level overview for executives

**Layout:**
```
Row 1 (h=3):  [KPI 1] [KPI 2] [KPI 3] [KPI 4]
              3 cols  3 cols  3 cols  3 cols

Row 2 (h=5):  [    Chart 1    ] [    Chart 2    ]
              6 columns         6 columns

Row 3 (h=5):  [Chart 3][Chart 4][Chart 5]
              4 cols   4 cols   4 cols

Row 4 (h=6):  [        Chart 6 (Full Width)      ]
              12 columns
```

**Tile Count:** 4 KPIs + 6 Charts = 10 tiles

**Best For:**
- Executive dashboards
- High-level metrics
- Key performance indicators
- Strategic overview

---

### Operational Preset

**Purpose:** Detailed operational metrics

**Layout:**
```
Row 1 (h=3):  [KPI 1] [KPI 2] [KPI 3] [KPI 4]
              3 cols  3 cols  3 cols  3 cols

Row 2 (h=5):  [    Chart 1    ] [    Chart 2    ]
              6 columns         6 columns

Row 3 (h=5):  [    Chart 3    ] [    Chart 4    ]
              6 columns         6 columns

Row 4 (h=5):  [    Chart 5    ] [    Chart 6    ]
              6 columns         6 columns

... continues in 2x2 grid pattern
```

**Tile Count:** 4 KPIs + 10-20 Charts

**Best For:**
- Operational dashboards
- Detailed analysis
- Multiple metrics
- Comprehensive view

---

### Trend Preset

**Purpose:** Time-series analysis

**Layout:**
```
Row 1 (h=3):  [KPI 1] [KPI 2] [KPI 3] [KPI 4]
              3 cols  3 cols  3 cols  3 cols

Row 2 (h=4):  [        Trend Chart 1 (Full)      ]
              12 columns

Row 3 (h=4):  [        Trend Chart 2 (Full)      ]
              12 columns

Row 4 (h=4):  [        Trend Chart 3 (Full)      ]
              12 columns

... continues with full-width charts
```

**Tile Count:** 4 KPIs + 5-10 Full-Width Charts

**Best For:**
- Time-series analysis
- Trend visualization
- Historical data
- Forecasting

---

### Comparison Preset

**Purpose:** Side-by-side comparisons

**Layout:**
```
Row 1 (h=3):  [KPI 1] [KPI 2] [KPI 3] [KPI 4]
              3 cols  3 cols  3 cols  3 cols

Row 2 (h=4):  [    Compare 1   ] [    Compare 2   ]
              6 columns          6 columns

Row 3 (h=4):  [    Compare 3   ] [    Compare 4   ]
              6 columns          6 columns

Row 4 (h=4):  [    Compare 5   ] [    Compare 6   ]
              6 columns          6 columns

... continues in 2-column pattern
```

**Tile Count:** 4 KPIs + 8-12 Comparison Charts

**Best For:**
- A/B comparisons
- Regional analysis
- Category comparisons
- Benchmark analysis

---

## Responsive Behavior

### Desktop (> 1200px)
- Full 12-column grid
- All tiles visible
- Optimal spacing

### Tablet (768px - 1200px)
- 12-column grid maintained
- Tiles may stack more
- Reduced margins

### Mobile (< 768px)
- Single column layout
- Tiles stack vertically
- Full-width tiles

---

## Color Scheme

### Background Colors
```css
Dashboard Background: #020617 (slate-950)
Tile Background:      linear-gradient(to-br, #1e293b, #0f172a)
                      (slate-800 to slate-900)
```

### Border Colors
```css
Default Border:  #334155 (slate-700)
Hover Border:    Current accent color
Active Border:   Current accent color
```

### Text Colors
```css
Primary Text:    #ffffff (white)
Secondary Text:  #94a3b8 (slate-400)
Tertiary Text:   #64748b (slate-500)
```

### Trend Colors
```css
Positive:  #34d399 (emerald-400)
Negative:  #fb7185 (rose-400)
Neutral:   #3b82f6 (blue-500)
```

---

## Typography

### Font Families
```css
Headings:  font-heading (system font stack)
Body:      font-body (system font stack)
Numbers:   font-mono (monospace)
```

### Font Sizes
```css
KPI Label:     0.75rem (12px) - uppercase
KPI Value:     1.875rem (30px) - bold
Chart Title:   0.875rem (14px) - semibold
Trend Text:    0.875rem (14px) - medium
Body Text:     1rem (16px) - regular
```

### Font Weights
```css
Light:     300
Regular:   400
Medium:    500
Semibold:  600
Bold:      700
```

---

## Spacing System

### Padding
```css
KPI Card:      1.25rem (20px)
Chart Tile:    1rem (16px)
Header:        0.75rem (12px)
```

### Margins
```css
Grid Margin:   1rem (16px)
Section Gap:   1.5rem (24px)
```

### Heights
```css
Row Unit:      60px
KPI Card:      180px (3 units)
Small Chart:   240px (4 units)
Medium Chart:  300px (5 units)
Large Chart:   360px (6 units)
```

---

## Interactive Elements

### Hover States
- **KPI Cards:** Border color changes to accent
- **Chart Tiles:** Border color changes to accent
- **Buttons:** Background darkens, text brightens
- **Drag Handle:** Cursor changes to move

### Transitions
```css
All transitions: 200ms ease-in-out
Border color:    transition-all duration-200
Background:      transition-colors
Transform:       transition-transform
```

### Drag & Drop
- **Drag Handle:** Visible grip icon (≡)
- **Dragging:** Tile becomes semi-transparent
- **Drop Zone:** Highlighted area
- **Snap:** Tiles snap to grid

---

## Accessibility

### Color Contrast
- All text meets WCAG AA standards
- Trend colors have sufficient contrast
- Icons are clearly visible

### Keyboard Navigation
- Tab through interactive elements
- Enter to activate buttons
- Escape to close modals

### Screen Readers
- Semantic HTML structure
- ARIA labels on icons
- Alt text for charts

---

## Best Practices

### KPI Cards
✅ Use for key metrics
✅ Include sparklines when possible
✅ Show trend direction
✅ Keep labels short
❌ Don't overload with data
❌ Don't use for detailed charts

### Chart Tiles
✅ Use descriptive titles
✅ Choose appropriate chart type
✅ Ensure data is visible
✅ Use consistent colors
❌ Don't overcrowd with data
❌ Don't use too many colors

### Layout
✅ Group related metrics
✅ Put KPIs at top
✅ Use consistent sizing
✅ Leave breathing room
❌ Don't mix too many sizes
❌ Don't overcrowd the dashboard

---

## Examples

### Sales Dashboard
```
[Total Sales] [Revenue] [Orders] [Customers]
[Sales Trend Chart (full width)            ]
[Top Products    ] [Regional Sales         ]
[Sales by Category (full width)            ]
```

### Marketing Dashboard
```
[Impressions] [Clicks] [Conversions] [ROI]
[Campaign Performance ] [Channel Mix      ]
[Engagement Trend (full width)            ]
[Top Campaigns   ] [Audience Demographics]
```

### Operations Dashboard
```
[Uptime] [Errors] [Response Time] [Throughput]
[System Health  ] [Error Rate             ]
[Request Volume ] [Database Performance   ]
[API Latency    ] [Cache Hit Rate         ]
```

---

**Last Updated:** March 25, 2026  
**Version:** 2.0.0  
**Style:** Power BI Professional Dark Theme
