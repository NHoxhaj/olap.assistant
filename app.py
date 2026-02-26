import streamlit as st
import pandas as pd
import anthropic
import plotly.express as px
from data_utils import load_data, get_analytics_summary, get_data_quality_report
from prompts import SYSTEM_PROMPT
import plotly.graph_objs as go
import logging
import signal
import time
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. API and Model Configuration
if "ANTHROPIC_API_KEY" in st.secrets:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
else:
    st.error("Error: ANTHROPIC_API_KEY not found in .streamlit/secrets.toml")
    st.stop()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=api_key)

# 2. UI Configuration
st.set_page_config(page_title="OLAP Assistant", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main page background */
    .stApp {
        background: linear-gradient(160deg, #f8f9ff 0%, #f0f2ff 30%, #e8ecff 60%, #f5f0ff 100%);
    }
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0a2e 0%, #2d1b69 40%, #1e1250 70%, #0f0a30 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    section[data-testid="stSidebar"] .stMetric label {
        color: #a0a0c0 !important;
    }
    section[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
    }
    section[data-testid="stSidebar"] button {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background: rgba(255,255,255,0.2) !important;
        border-color: rgba(255,255,255,0.35) !important;
    }
    section[data-testid="stSidebar"] button p {
        color: #ffffff !important;
    }
    /* Welcome flow cards */
    .flow-container {
        display: flex;
        align-items: stretch;
        justify-content: center;
        gap: 0;
        margin: 1.5rem 0;
    }
    .flow-card {
        flex: 1;
        padding: 2rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .flow-card-1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    .flow-card-2 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white !important;
    }
    .flow-card-3 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white !important;
    }
    .flow-card .flow-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    .flow-card .flow-step {
        font-size: 0.85rem;
        opacity: 0.85;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .flow-card .flow-title {
        font-size: 1.3rem;
        font-weight: 700;
        line-height: 1.3;
    }
    .flow-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: #667eea;
        padding: 0 0.5rem;
        min-width: 40px;
    }
    /* Chat input bar styling */
    .stChatInput {
        border-radius: 16px !important;
        overflow: hidden;
    }
    .stChatInput > div {
        background: linear-gradient(135deg, #667eea08 0%, #764ba208 100%) !important;
        border: 2px solid #667eea40 !important;
        border-radius: 16px !important;
        padding: 0.6rem 0.75rem !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        min-height: 60px !important;
    }
    .stChatInput > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15), 0 4px 12px rgba(102, 126, 234, 0.1) !important;
    }
    .stChatInput textarea {
        font-size: 1.15rem !important;
        color: #333 !important;
        line-height: 1.5 !important;
    }
    .stChatInput textarea::placeholder {
        color: #999 !important;
        font-style: italic !important;
    }
    .stChatInput button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        min-width: 42px !important;
        min-height: 42px !important;
        transition: opacity 0.2s ease, transform 0.2s ease !important;
    }
    .stChatInput button:hover {
        opacity: 0.9 !important;
        transform: scale(1.05) !important;
    }
    .stChatInput button svg {
        fill: white !important;
    }
    /* Footer info boxes */
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        border: 1px solid #e0e5ec;
    }
    .info-box h3 {
        margin-top: 0;
        margin-bottom: 0.75rem;
        font-size: 1.15rem;
    }
    .info-box ul {
        list-style: none;
        padding-left: 0;
        margin: 0;
    }
    .info-box ul li {
        padding: 0.25rem 0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"> AI-Powered OLAP Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask questions. Get insights. No SQL required.</div>', unsafe_allow_html=True)

# Sidebar styling
st.sidebar.markdown("# 🎛️ Dashboard")
st.sidebar.markdown("---")

# 3. Data Loading
try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset not found: {e}. Please run 'python generate_dataset.py'.")
    st.stop()

# Display dataset statistics
stats = get_analytics_summary(df)
if stats:
    st.sidebar.subheader("📈 Dataset Overview")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("📊 Transactions", stats["Transactions"], delta=None)
    with col2:
        st.metric("💼 Records", stats["Transactions"], delta=None)

    col3, col4 = st.sidebar.columns(2)
    with col3:
        st.metric("💰 Revenue", stats["Total Revenue"], delta=None)
    with col4:
        st.metric("📈 Profit", stats["Total Profit"], delta=None)

st.sidebar.markdown("---")

# Initialize session state early
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "query_cache" not in st.session_state:
    st.session_state.query_cache = {}

if "saved_queries" not in st.session_state:
    st.session_state.saved_queries = []

# Example queries section
st.sidebar.subheader("💡 Quick Query Examples")
query_examples = {
    "🔍 Slice": "Show only 2024 data",
    "🎯 Dice": "Electronics in Europe",
    "📊 Aggregate": "Total revenue by category",
    "📉 Drill-Down": "Break down Q4 by month",
    "⚖️ Compare": "Compare 2023 vs 2024 revenue"
}

for label, query in query_examples.items():
    if st.sidebar.button(f"{label}: {query[:25]}...", key=f"query_{label}"):
        st.session_state.chat_input_value = query

st.sidebar.markdown("---")

# Query history section
if st.session_state.query_history:
    st.sidebar.subheader("📜 Recent Queries")
    for i, query in enumerate(reversed(st.session_state.query_history[-5:])):
        if st.sidebar.button(f"🔄 {query[:45]}...", key=f"history_{i}"):
            st.session_state.chat_input_value = query

st.sidebar.markdown("---")

# Saved queries section
if st.session_state.saved_queries:
    st.sidebar.subheader("⭐ Saved Queries")
    for i, saved_query in enumerate(st.session_state.saved_queries):
        col1, col2 = st.sidebar.columns([0.85, 0.15])
        with col1:
            if st.button(f"📌 {saved_query[:40]}...", key=f"saved_{i}"):
                st.session_state.chat_input_value = saved_query
        with col2:
            if st.button("✕", key=f"remove_saved_{i}", help="Remove"):
                st.session_state.saved_queries.pop(i)
                st.rerun()
    st.sidebar.markdown("---")

# Database viewer with tabs
st.sidebar.subheader("🗄️ Database Tools")
db_tab = st.sidebar.radio("View:", ["Full Database", "Column Info", "Statistics", "Data Quality"])

if db_tab == "Full Database":
    with st.sidebar.expander("📋 View Full Database", expanded=False):
        st.write(f"**Total Records:** {len(df)}")
        st.write(f"**Total Columns:** {len(df.columns)}")

        # Add search functionality
        search_term = st.text_input("🔍 Search in database:", key="db_search")

        if search_term:
            # Search in all columns
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            filtered_df = df[mask]
            st.write(f"Found {len(filtered_df)} matching records")
            st.dataframe(filtered_df, width='stretch')
        else:
            st.dataframe(df, width='stretch', height=400)

elif db_tab == "Column Info":
    with st.sidebar.expander("📋 Column Information", expanded=False):
        col_info = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.values,
            "Non-Null": df.count().values,
            "Null": df.isnull().sum().values
        })
        st.dataframe(col_info, width='stretch')

elif db_tab == "Statistics":
    with st.sidebar.expander("📊 Quick Statistics", expanded=False):
        st.write("**Numeric Columns Summary:**")
        st.dataframe(df.describe(), width='stretch')

elif db_tab == "Data Quality":
    with st.sidebar.expander("✅ Data Quality Report", expanded=False):
        quality_report = get_data_quality_report(df)

        if quality_report:
            # Overall completeness gauge
            st.metric("📊 Overall Completeness", f"{quality_report['overall_completeness']}%")
            st.markdown("---")

            # Missing values breakdown
            st.write("**📍 Missing Values by Column:**")
            missing_data = quality_report["missing_values"]
            if any(missing_data.values()):
                missing_df = pd.DataFrame({
                    "Column": missing_data.keys(),
                    "Missing": missing_data.values()
                })
                missing_df["Completeness %"] = (100 - (missing_df["Missing"] / len(df) * 100)).round(1)
                st.dataframe(missing_df, width='stretch', hide_index=True)
            else:
                st.success("✅ No missing values detected!")

            st.markdown("---")

            # Outliers detection
            if quality_report["outliers"]:
                st.write("**⚠️ Outliers Detected:**")
                outlier_df = pd.DataFrame({
                    "Column": quality_report["outliers"].keys(),
                    "Outlier Count": quality_report["outliers"].values()
                })
                st.dataframe(outlier_df, width='stretch', hide_index=True)
            else:
                st.info("ℹ️ No statistical outliers detected (z-score > 3)")

            st.markdown("---")

            # Data type validation
            st.write("**🔍 Column Data Types:**")
            type_df = pd.DataFrame({
                "Column": quality_report["type_validation"].keys(),
                "Type": quality_report["type_validation"].values()
            })
            st.dataframe(type_df, width='stretch', hide_index=True)

# 4. Chat Interface
# Welcome section when no messages yet
if not st.session_state.messages:
    st.markdown("""
    <div class="flow-container">
        <div class="flow-card flow-card-1">
            <div class="flow-icon">💬</div>
            <div class="flow-step">Step 1</div>
            <div class="flow-title">Ask questions about your data in natural language</div>
        </div>
        <div class="flow-arrow">➜</div>
        <div class="flow-card flow-card-2">
            <div class="flow-icon">⚡</div>
            <div class="flow-step">Step 2</div>
            <div class="flow-title">AI generates code automatically</div>
        </div>
        <div class="flow-arrow">➜</div>
        <div class="flow-card flow-card-3">
            <div class="flow-icon">📊</div>
            <div class="flow-step">Step 3</div>
            <div class="flow-title">Visualizations created on the fly</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%); border-radius: 12px; padding: 1.5rem 2rem; border: 1px solid #667eea30;">
        <h3 style="margin-top: 0;">🚀 Getting Started</h3>
        <p style="margin-bottom: 0.75rem; font-size: 1.05rem;"><strong>Try asking questions like:</strong></p>
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <div style="background: white; padding: 0.6rem 1rem; border-radius: 8px; border-left: 3px solid #667eea; font-size: 1rem;">⚖️ Compare 2023 vs 2024 revenue by region</div>
            <div style="background: white; padding: 0.6rem 1rem; border-radius: 8px; border-left: 3px solid #f5576c; font-size: 1rem;">🏆 Show top 5 countries by profit</div>
            <div style="background: white; padding: 0.6rem 1rem; border-radius: 8px; border-left: 3px solid #4facfe; font-size: 1rem;">📊 What percentage of revenue comes from each category?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User query input - handle both chat input and sidebar example buttons
user_query = st.chat_input("Ask a question, e.g.: 'Compare revenue by category for 2024'")

# If no direct input but an example query was clicked via sidebar button, use that
if not user_query and "chat_input_value" in st.session_state:
    user_query = st.session_state.chat_input_value
    del st.session_state.chat_input_value  # Clear after use

if user_query:
    # Save to query history
    if user_query not in st.session_state.query_history:
        st.session_state.query_history.append(user_query)

    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Check if query result is cached
    is_cached = user_query in st.session_state.query_cache

    with st.chat_message("assistant"):
        # Show different spinner text for cached vs new query
        spinner_text = "📚 Loading from cache..." if is_cached else "AI is generating insights..."
        with st.spinner(spinner_text):
            try:
                query_start_time = time.time()

                # If query is cached, skip execution and restore cached results
                if is_cached:
                    local_vars = st.session_state.query_cache[user_query]['local_vars']
                    execution_time = st.session_state.query_cache[user_query]['execution_time']
                    is_cache_hit = True
                    st.info("💾 Results loaded from cache")
                else:
                    is_cache_hit = False

                    full_prompt = user_query

                    try:
                        response = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=4096,
                            system=SYSTEM_PROMPT,
                            messages=[{"role": "user", "content": full_prompt}]
                        )
                    except Exception as api_err:
                        st.error(f"🌐 API Error: Failed to generate response.\n\nIssue: {str(api_err)}\n\nTry:\n- Check your internet connection\n- Verify API key is valid\n- Wait a moment and retry")
                        logger.error(f"API call failed: {api_err}")
                        st.stop()

                    # Validate API response
                    if not response or not response.content:
                        st.error("⚠️ Empty Response: The AI didn't generate any code.\n\nTry:\n- Rephrasing your question\n- Using more specific metrics (revenue, profit)\n- Adding time period (2024, Q4)")
                        st.stop()

                    # Extract Python code from markdown code block
                    response_text = response.content[0].text
                    code_to_run = response_text.replace("```python", "").replace("```", "").strip()

                    # Validate that we have code to run
                    if not code_to_run or len(code_to_run) < 10:
                        st.error("⚠️ Invalid Code Generation: AI response doesn't contain valid Python code.\n\nTry:\n- Asking a more specific question\n- Breaking down complex queries\n- Using technical column names")
                        with st.expander("View AI Response"):
                            st.text(response_text[:500])  # Show first 500 chars
                        st.stop()

                    # Validate code syntax (basic check)
                    if code_to_run.startswith("I ") or code_to_run.startswith("Sorry"):
                        st.error("⚠️ AI did not generate valid code. Try rephrasing your question with more specific details.")
                        with st.expander("View AI Response"):
                            st.text(response_text)
                        st.stop()

                    # Validate code safety (block dangerous imports/functions)
                    dangerous_patterns = ['__import__', 'eval(', 'exec(', 'compile(', 'open(', 'subprocess', 'os.', 'import os', 'import sys', 'import socket']
                    found_dangers = [p for p in dangerous_patterns if p in code_to_run]
                    if found_dangers:
                        st.error(f"❌ Generated code contains unsafe operations: {', '.join(found_dangers)}\n\nPlease try a different query focused on data analysis only")
                        logger.warning(f"Unsafe code detected: {found_dangers}")
                        st.stop()

                    # Create isolated execution environment
                    local_vars = {'df': df, 'px': px, 'st': st, 'pd': pd, 'go': go}

                    # Execute generated code
                    exec(code_to_run, globals(), local_vars)

                # Display results - skip the original database
                results_shown = False
                for key, value in local_vars.items():
                    if key == 'df':  # Skip the original database
                        continue
                    if isinstance(value, pd.DataFrame):
                        # Create result card with styling
                        result_title = key.replace("_", " ").title()
                        st.markdown(f"### 📊 {result_title}")

                        # Auto-visualization recommendations based on query keywords
                        if len(value) > 0:
                            # Check if DataFrame has 2 columns (key-value pair for visualization)
                            if len(value.columns) == 2:
                                col1, col2 = value.columns
                                numeric_col = col2 if pd.api.types.is_numeric_dtype(value[col2]) else col1

                                # Auto-generate visualization if query suggests it
                                if any(kw in user_query.lower() for kw in ['compare', 'trend', 'revenue', 'profit', 'total', 'by']):
                                    try:
                                        # Create automatic chart with better styling
                                        auto_chart = px.bar(
                                            value,
                                            x=col1,
                                            y=numeric_col,
                                            title=f"{result_title}",
                                            color=numeric_col,
                                            color_continuous_scale='viridis'
                                        )
                                        auto_chart.update_layout(
                                            height=400,
                                            showlegend=False,
                                            margin=dict(l=0, r=0, t=40, b=0)
                                        )
                                        st.plotly_chart(auto_chart, width='stretch')
                                    except:
                                        pass  # Silently fail to not break data display

                        # Display the data table with export option
                        tab1, tab2 = st.tabs(["📋 Data", "📥 Export"])

                        with tab1:
                            # Show row count
                            st.caption(f"📍 {len(value)} rows × {len(value.columns)} columns")
                            st.dataframe(value, width='stretch')

                        with tab2:
                            col1_csv, col2_json, col3_excel = st.columns(3)
                            with col1_csv:
                                csv = value.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download CSV",
                                    data=csv,
                                    file_name=f"{key}.csv",
                                    mime="text/csv",
                                    key=f"download_csv_{key}"
                                )
                            with col2_json:
                                json_data = value.to_json(orient='records', indent=2)
                                st.download_button(
                                    label="📥 Download JSON",
                                    data=json_data,
                                    file_name=f"{key}.json",
                                    mime="application/json",
                                    key=f"download_json_{key}"
                                )
                            with col3_excel:
                                from io import BytesIO
                                excel_buffer = BytesIO()
                                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                    value.to_excel(writer, sheet_name='Data', index=False)
                                excel_data = excel_buffer.getvalue()
                                st.download_button(
                                    label="📥 Download Excel",
                                    data=excel_data,
                                    file_name=f"{key}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"download_excel_{key}"
                                )

                        results_shown = True
                    elif isinstance(value, go.Figure):
                        st.plotly_chart(value, width='stretch')
                        results_shown = True

                if not results_shown:
                    st.info("✓ Query executed. No tables or charts to display.")

                # Calculate execution time and metrics
                execution_time = time.time() - query_start_time if not is_cache_hit else execution_time

                # Count results
                table_count = sum(1 for k, v in local_vars.items() if k != 'df' and isinstance(v, pd.DataFrame))
                row_count = sum(len(v) for k, v in local_vars.items() if k != 'df' and isinstance(v, pd.DataFrame))

                # Store in cache if this is a new query
                if not is_cache_hit:
                    st.session_state.query_cache[user_query] = {
                        'local_vars': local_vars,
                        'execution_time': execution_time
                    }

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Analysis complete. ✅"
                })

                # Display save button
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    if st.button("⭐ Save Query", key=f"save_{id(user_query)}"):
                        if user_query not in st.session_state.saved_queries:
                            st.session_state.saved_queries.append(user_query)
                            st.success("✅ Saved to favorites!")
                            st.rerun()

            except ValueError as e:
                error_str = str(e)
                if "could not convert" in error_str.lower():
                    st.error("❌ Type Conversion Error: Data types don't match.\n\nTry:\n- Using numeric columns for calculations\n- Converting dates properly")
                else:
                    st.error(f"❌ Data Error: {error_str}\n\nThis might mean:\n- Column name doesn't exist\n- Invalid filter value\n- Check 'Database Tools' to see available columns")
                with st.expander("🔍 View Generated Code"):
                    st.code(code_to_run if 'code_to_run' in locals() else "Code not generated", language="python")

            except KeyError as e:
                st.error(f"❌ Column Not Found: {str(e)}\n\n**Available columns:**\n{', '.join(df.columns)}\n\nCheck the column name spelling (case-sensitive)")
                with st.expander("🔍 View Generated Code"):
                    st.code(code_to_run if 'code_to_run' in locals() else "Code not generated", language="python")

            except ZeroDivisionError:
                st.error("❌ Math Error: Division by zero detected.\n\nThis happens when:\n- Dividing by a column with zeros\n- Calculating percentage with zero totals\n\nTry filtering out zero values first")
                with st.expander("🔍 View Generated Code"):
                    st.code(code_to_run if 'code_to_run' in locals() else "Code not generated", language="python")

            except NameError as e:
                st.error(f"❌ Variable Error: {str(e)}\n\nThe generated code references a variable that doesn't exist.\n\nTry rephrasing your question or simplify the query")
                logger.error(f"NameError: {e}")
                with st.expander("🔍 View Generated Code"):
                    st.code(code_to_run if 'code_to_run' in locals() else "Code not generated", language="python")

            except TypeError as e:
                st.error(f"❌ Type Error: {str(e)}\n\nData types don't match (e.g., adding string to number).\n\nTry:\n- Using consistent data types\n- Converting columns explicitly (e.g., .astype(float))")
                with st.expander("🔍 View Generated Code"):
                    st.code(code_to_run if 'code_to_run' in locals() else "Code not generated", language="python")

            except AttributeError as e:
                st.error(f"❌ Method Error: {str(e)}\n\nThe object doesn't have this method or property.\n\nCommon issues:\n- Misspelled method name\n- Using method on wrong data type")
                with st.expander("🔍 View Generated Code"):
                    st.code(code_to_run if 'code_to_run' in locals() else "Code not generated", language="python")

            except IndexError as e:
                st.error(f"❌ Index Error: {str(e)}\n\nTrying to access an invalid position in data.\n\nThis might mean:\n- The filtered result is empty\n- Accessing row/column that doesn't exist")
                with st.expander("🔍 View Generated Code"):
                    st.code(code_to_run if 'code_to_run' in locals() else "Code not generated", language="python")

            except TimeoutError:
                st.error("⏱️ Timeout Error: Query took too long to execute.\n\nTry:\n- Simplifying the query\n- Using fewer rows/columns\n- Breaking into multiple queries")
                logger.warning("Query execution timed out")

            except ConnectionError as e:
                st.error("🌐 Connection Error: Failed to reach the AI service.\n\nTry:\n- Checking internet connection\n- Waiting a moment and retrying\n- Check if API is working")
                logger.error(f"Connection error: {e}")

            except Exception as e:
                # Generic catch-all with better formatting
                error_type = type(e).__name__
                error_msg = str(e)

                st.error(f"❌ {error_type}: {error_msg}\n\n**Quick fixes to try:**\n- Simplify your question\n- Ask for one operation at a time\n- Check the database tools for available data\n- Rephrase with specific column names")

                # Log detailed error for debugging
                logger.error(f"{error_type}: {error_msg}", exc_info=True)

                with st.expander("🔍 View Generated Code"):
                    st.code(code_to_run if 'code_to_run' in locals() else "Code not generated", language="python")
                with st.expander("📋 Debug Information"):
                    st.code(f"Error Type: {error_type}\nError Message: {error_msg}", language="text")

# Footer with helpful information
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-box">
        <h3>💡 Tips</h3>
        <ul>
            <li>📌 Use specific metrics (revenue, profit)</li>
            <li>📌 Mention time periods (2024, Q4)</li>
            <li>📌 Ask for comparisons or trends</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <h3>📌 OLAP Operations</h3>
        <ul>
            <li>🔹 <strong>Slice</strong>: Filter single dimension</li>
            <li>🔹 <strong>Dice</strong>: Filter multiple dimensions</li>
            <li>🔹 <strong>Drill</strong>: Break down hierarchies</li>
            <li>🔹 <strong>Compare</strong>: Contrast periods</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-box">
        <h3>⚙️ Features</h3>
        <ul>
            <li>✅ Natural language queries</li>
            <li>✅ Auto-visualizations</li>
            <li>✅ CSV/JSON/Excel export</li>
            <li>✅ Query caching & bookmarks</li>
            <li>✅ Execution metrics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)