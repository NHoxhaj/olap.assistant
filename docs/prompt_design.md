# System Prompt Design Strategy

This document explains how the AI system prompt is engineered to generate correct Python/Pandas code for OLAP analysis.

## 1. Context Engineering

The system prompt provides the AI with comprehensive dataset context using a "Star Schema" approach:

### Dataset Schema Definition
```
DIMENSIONS (Grouping Categories):
├── Time Hierarchy
│   ├── year (2022, 2023, 2024)
│   ├── quarter (1, 2, 3, 4)
│   ├── month (1-12)
│   └── month_name (January, February, ...)
│
├── Geography
│   ├── region (North America, Europe, Asia Pacific, Latin America)
│   └── country (Country_1 through Country_10)
│
├── Product
│   ├── category (Electronics, Furniture, Office Supplies, Clothing)
│   └── subcategory (e.g., Smartphones, Laptops under Electronics)
│
└── Customer
    └── customer_segment (Consumer, Corporate, Home Office)

MEASURES (Numbers to Aggregate):
├── Transaction Metrics
│   ├── quantity
│   └── unit_price
│
└── Financial Metrics
    ├── revenue
    ├── cost
    ├── profit
    └── profit_margin
```

## 2. OLAP Operation Definitions

The prompt explicitly defines each OLAP operation with:
- **Purpose**: Why this operation is used
- **Example Query**: Natural language question
- **Example Code**: Exact Pandas implementation
- **Pandas Pattern**: Reusable code template

### 1. SLICE Operation
**Definition:** Filter by a single dimension
```python
# Pattern: df[condition][columns]
sliced_data = df[df['year'] == 2024][['month', 'category', 'revenue']]
```

### 2. DICE Operation
**Definition:** Filter by multiple dimensions using AND (&) operator
```python
# Pattern: df[(condition1) & (condition2) & (condition3)]
diced_data = df[(df['category'] == 'Electronics') & (df['region'] == 'Europe') & (df['revenue'] > 5000)]
```

### 3. GROUP & SUMMARIZE Operation
**Definition:** Aggregate measures by dimension(s)
```python
# Pattern: df.groupby('dimension')['measure'].agg_function().reset_index()
revenue_by_category = df.groupby('category')['revenue'].sum().reset_index().rename(columns={'revenue': 'total_revenue'})
```

### 4. DRILL-DOWN Operation
**Definition:** Break down higher hierarchy level to lower level
```python
# Pattern: Combine SLICE + GROUP
# Example: Year → Quarter → Month
q4_monthly = df[(df['year'] == 2024) & (df['quarter'] == 4)].groupby('month_name')['revenue'].sum().reset_index()
```

### 5. COMPARE Operation
**Definition:** Contrast metrics across periods or dimensions side-by-side
```python
# Pattern: Create separate DataFrames, then merge
revenue_2023 = df[df['year'] == 2023].groupby('region')['revenue'].sum()
revenue_2024 = df[df['year'] == 2024].groupby('region')['revenue'].sum()
year_comparison = pd.DataFrame({'2023': revenue_2023, '2024': revenue_2024}).reset_index()
```

## 3. Prompt Engineering Techniques

### Technique 1: Explicit Multi-Operation Requirement
**Problem:** User asks "Show category totals and Electronics breakdown"
- Without explicit instruction, AI might only generate one DataFrame

**Solution:** Add CRITICAL rule:
```
If user requests multiple operations, generate SEPARATE DataFrames for EACH operation.

CORRECT:
category_totals = df.groupby('category')['revenue'].sum().reset_index()
electronics_drill = df[df['category'] == 'Electronics'].groupby('subcategory')['revenue'].sum().reset_index()

WRONG (generates only one):
electronics_drill = df[df['category'] == 'Electronics'].groupby('subcategory')['revenue'].sum().reset_index()
```

**Why it Works:** AI learns from explicit examples of correct vs. wrong output

### Technique 2: Naming Convention Rules
**Problem:** Generated variable names might be unclear ("agg1", "result_df", "data")
**Solution:** Specify snake_case naming from intent:
```
"category totals" → category_totals
"monthly comparison" → monthly_comparison
"regional profit summary" → regional_profit_summary
```

### Technique 3: Code Quality Standards
**Problem:** Generated code might be inefficient or error-prone
**Solution:** Include procedural rules:
```
1. Always use .reset_index() after groupby()
2. Use .rename(columns={...}) for clarity
3. Filter BEFORE grouping for efficiency
4. Use exact column values from data
5. Sort results when appropriate
```

### Technique 4: Prohibited Actions
**Problem:** AI might generate harmful code (file I/O, imports, etc.)
**Solution:** Explicit prohibition with rationale:
```
NEVER generate:
- explanations
- print() or st.write() statements
- file operations
- new libraries/imports
- overwrites to 'df'
```

### Technique 5: Hallucination Prevention
**Problem:** AI invents dimensions/columns that don't exist
**Solution:** Comprehensive column enumeration:
```
"The dataset has EXACTLY these columns:
order_date, year, quarter, month, month_name,
region, country, category, subcategory,
customer_segment, quantity, unit_price,
revenue, cost, profit, profit_margin"
```

## 4. Code Execution Safety Measures

### Pre-Execution Validation (app.py)

```python
# 1. Validate code is generated
if not code_to_run or code_to_run.startswith("I "):
    st.error("AI did not generate valid code")

# 2. Check for dangerous patterns
dangerous_patterns = ['__import__', 'eval(', 'exec(', 'open(', 'subprocess']
if any(pattern in code_to_run for pattern in dangerous_patterns):
    st.error("Code contains unsafe operations")

# 3. Use isolated namespace
local_vars = {'df': df, 'px': px, 'st': st, 'pd': pd, 'go': go}
exec(code_to_run, globals(), local_vars)
```

## 5. Error Recovery & Output Inspection

### Specific Exception Handling

```python
try:
    exec(code_to_run, globals(), local_vars)
except ValueError as e:
    st.error("Data Error: Column missing or invalid filter value")
except KeyError as e:
    st.error("Column Not Found")
except Exception as e:
    st.error(f"Execution Error: Try simplifying your query")
```

### Result Display Logic

```python
# Only display AI-generated DataFrames, not the original data
for key, value in local_vars.items():
    if key == 'df':  # Skip original database
        continue
    if isinstance(value, pd.DataFrame):
        st.dataframe(value)
    if isinstance(value, go.Figure):
        st.plotly_chart(value)
```

## 6. Prompt Iterations & Improvements

### Version History

**v1 (Initial):** Basic OLAP definitions
- ❌ Missing Compare operation examples
- ❌ Vague "Roll-Up" guidance
- ❌ No multi-operation handling

**v2 (Current):** Comprehensive engineering
- ✅ All 5 OLAP operations with examples
- ✅ Explicit multi-operation guidance
- ✅ Code quality standards
- ✅ Naming conventions
- ✅ Safety requirements

### Future Improvements

Potential enhancements:
1. Add visualization requirements (auto-generate charts)
2. Support for aggregate functions (min, max, avg, count)
3. Date range filtering patterns
4. Percentage calculations and ranking
5. Export to CSV/Excel functionality

## 7. Testing the Prompt

### Test Cases for OLAP Operations

| Operation | Test Query | Expected Behavior |
|-----------|-----------|-------------------|
| Slice | "Show 2024 data" | Filter with df[df['year'] == 2024] |
| Dice | "Electronics in Europe" | Multiple conditions with & operator |
| Group | "Total by category" | groupby().sum().reset_index() |
| Drill | "2024 Q4 by month" | Combine slice and groupby |
| Compare | "2023 vs 2024" | Two DataFrames, merged for comparison |

### Test Multiple Operations
```
Query: "Show category totals, then drill into Electronics by subcategory"
Expected: TWO DataFrames generated
- category_totals
- electronics_drill
```

## 8. Performance Considerations

### Prompt Length Trade-offs

- **Longer prompts** (more examples) → Better results, slower API
- **Shorter prompts** (fewer examples) → Fast but less accurate
- **Current approach:** ~2000 tokens = 2-3 seconds per query

### Caching Opportunities

- Cache prompts for identical queries
- Store generated code for re-use
- Session-based history prevents re-generation

## 9. Integration with Streamlit

- Chat history maintained in `st.session_state.messages`
- Code execution in isolated namespace
- Error messages provide actionable guidance
- Dataset preview available for reference

---

**Designed for:** Tier 2 Builder - Production-Ready AI Analytics Application
