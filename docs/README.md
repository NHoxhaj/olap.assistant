# 📊 AI-Powered OLAP Assistant

A Streamlit web application that uses Anthropic's Claude AI to translate natural language questions into Python code that performs OLAP (Online Analytical Processing) analysis on retail sales data, with automatic visualizations.

**Ask questions. Get insights. No SQL required.**

## Features

✅ **Natural Language Analysis** - Ask business questions in plain English
✅ **OLAP Operations** - Slice, Dice, Group & Summarize, Drill-Down, Compare
✅ **AI Code Generation** - Claude AI generates Pandas code automatically
✅ **Interactive Visualizations** - Plotly charts for data exploration
✅ **Chat Interface** - Maintain conversation history with context
✅ **Error Handling** - Helpful guidance when queries fail
✅ **Query Caching** - Instant results for repeated queries with performance metrics
✅ **Query Bookmarks** - Save favorite queries for quick re-execution
✅ **Multi-Format Export** - Download results as CSV, JSON, or Excel
✅ **Execution Metrics** - See execution time, row counts, and cache status

## Quick Start

### Prerequisites
- Python 3.8+
- Anthropic API key (available at [console.anthropic.com](https://console.anthropic.com))
- 500MB disk space

### Installation

1. **Clone or setup the project:**
   ```bash
   cd olapppp
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate the sample dataset:**
   ```bash
   python generate_dataset.py
   ```
   This creates a 10,000-row retail sales dataset at `data/global_retail_sales.csv`

5. **Configure API key:**
   Create `.streamlit/secrets.toml`:
   ```toml
   ANTHROPIC_API_KEY = "your_api_key_here"
   ```
   Get your API key from [Anthropic Console](https://console.anthropic.com)

6. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   The app opens at `http://localhost:8501`

## Usage

### Example Queries

The app supports all 5 OLAP operations:

| Operation | Example Query |
|-----------|---------------|
| **Slice** | "Show only 2024 data" |
| **Dice** | "Electronics in Europe" |
| **Group & Summarize** | "Total revenue by region" |
| **Drill-Down** | "Break down Q4 by month" |
| **Compare** | "Compare 2023 vs 2024 revenue" |

### Multi-Operation Queries

You can ask complex questions combining multiple operations:
- "Show category totals, then drill into Electronics by subcategory"
- "Compare Consumer segment profit vs Corporate segment, by region"

### Dataset Schema

The app analyzes a global retail dataset with:

**Dimensions (Categories for grouping):**
- Time: `year`, `quarter`, `month`, `month_name`
- Geography: `region`, `country`
- Product: `category`, `subcategory`
- Customer: `customer_segment` (Consumer, Corporate, Home Office)

**Measures (Numbers to aggregate):**
- Transactions: `quantity`, `unit_price`
- Financial: `revenue`, `cost`, `profit`, `profit_margin`

**Time Coverage:** 2022-2024 (3 full years)
**Regions:** North America, Europe, Asia Pacific, Latin America
**Categories:** Electronics, Furniture, Office Supplies, Clothing

## Architecture

```
App Flow:
User Query → Claude AI → Generated Python Code → Pandas Execution → Results Display
                      ↓
              (with code validation & safety checks)
```

### Key Components

- **app.py** - Main Streamlit application (UI, chat, execution)
- **prompts.py** - Claude system prompt with OLAP operation definitions
- **data_utils.py** - Data loading and caching utilities
- **generate_dataset.py** - Creates synthetic retail dataset

## Troubleshooting

### "Error: ANTHROPIC_API_KEY not found"
**Solution:** Create `.streamlit/secrets.toml` with your API key:
```toml
ANTHROPIC_API_KEY = "your_key_here"
```
Get a key at [console.anthropic.com](https://console.anthropic.com)

### "Dataset not found"
**Solution:** Run the dataset generator:
```bash
python generate_dataset.py
```
This creates `data/global_retail_sales.csv`

### "AI did not generate valid code"
**Cause:** The query was unclear
**Solution:** Try rephrasing:
- ❌ "Show stuff" → ✅ "Show total revenue by category"
- ❌ "Compare things" → ✅ "Compare 2023 vs 2024 profit by region"

### "Column Not Found" error
**Cause:** Used wrong column name
**Solution:** Enable "Show Dataset Preview" in the sidebar to see available columns

### API Quota Exceeded
**Error:** "API Error: Failed to generate response"
**Cause:** Hit API rate limit or insufficient credits
**Solution:**
- Check your API usage at [console.anthropic.com](https://console.anthropic.com)
- Add credits to your account
- Batch simpler queries

### Code contains unsafe operations
**Cause:** Generated code attempted file I/O or system calls
**Solution:** Rephrase your query to focus on data analysis only

## Advanced Features

### Dataset Preview
Click "Show Dataset Preview" in the sidebar to see the first 10 rows and verify column names.

### Generated Code Review
Expand "View Generated Code" to see the Python code Claude created (useful for debugging).

### Performance
- First query is slower (model initialization)
- Subsequent queries are faster (caching)
- Typical query time: 2-5 seconds

## Development

### Running Tests
```bash
pytest tests/
```

### Modifying System Prompt
Edit `prompts.py` to change how Claude generates code:
- Add new OLAP operations
- Change code style (e.g., require Plotly charts for all outputs)
- Add domain-specific terminology

### Customizing Dataset
Edit `generate_dataset.py` to create custom data:
- Change regions, categories, time periods
- Add new dimensions (e.g., product cost tiers)
- Adjust record count

## Project Structure

```
olapppp/
├── app.py                          # Main Streamlit app
├── prompts.py                      # System prompt for Claude
├── data_utils.py                   # Data loading utilities
├── generate_dataset.py             # Dataset generation script
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── secrets.toml               # API keys (NOT in git)
├── data/
│   └── global_retail_sales.csv    # Sample dataset (10K rows)
└── docs/
    ├── README.md                  # This file
    └── prompt_design.md           # System prompt strategy
```

## Limitations

- Query timeouts after 30 seconds
- Maximum 1M response tokens per day (free tier)
- No persistent query history across sessions
- Analytics on single CSV only (no multi-table joins)

## Security

- API keys stored in `.streamlit/secrets.toml` (excluded from git)
- Generated code is validated before execution
- No file I/O or system commands allowed
- Runs in isolated Python namespace

## Contributing

To improve the app:
1. Test new query types
2. Suggest better prompt engineering
3. Report bugs via issues

## License

Created as part of Tier 2 Builder curriculum.

## Support

- **API Key Issues:** See [Anthropic Documentation](https://docs.anthropic.com)
- **Streamlit Help:** [docs.streamlit.io](https://docs.streamlit.io)
- **Data Questions:** Check "Show Dataset Preview" in the app

---

**Happy analyzing! 📊**
