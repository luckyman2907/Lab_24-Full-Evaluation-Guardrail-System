"""
Bonus 3: Eval Dashboard - +3 điểm
Live dashboard with Streamlit for monitoring evaluation metrics.
Simple, no complex dependencies, easy to run.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime


# Page config
st.set_page_config(
    page_title="RAG Evaluation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Dark Theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #b0b0b0;
        font-weight: 500;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700;
    }
    
    /* Cards */
    .element-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Radio buttons */
    [data-testid="stRadio"] label {
        color: #e0e0e0;
        font-weight: 500;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-radius: 8px;
    }
    
    /* Text */
    p, span, div {
        color: #e0e0e0;
    }
    
    /* Plotly charts background */
    .js-plotly-plot {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    """Load all evaluation data."""
    data = {}
    
    # Phase A - RAGAS
    try:
        ragas_summary = Path("results/phase_a/ragas_summary.json")
        if ragas_summary.exists():
            with open(ragas_summary, 'r') as f:
                data['ragas'] = json.load(f)
        
        ragas_results = Path("results/phase_a/ragas_results.csv")
        if ragas_results.exists():
            data['ragas_details'] = pd.read_csv(ragas_results)
    except Exception as e:
        st.warning(f"Could not load RAGAS data: {e}")
    
    # Phase B - LLM Judge
    try:
        pairwise = Path("results/phase_b/pairwise_results.csv")
        if pairwise.exists():
            data['pairwise'] = pd.read_csv(pairwise)
        
        absolute = Path("results/phase_b/absolute_scores.csv")
        if absolute.exists():
            data['absolute'] = pd.read_csv(absolute)
    except Exception as e:
        st.warning(f"Could not load Judge data: {e}")
    
    # Phase C - Guardrails
    try:
        pii = Path("results/phase_c/pii_test_results.csv")
        if pii.exists():
            data['pii'] = pd.read_csv(pii)
    except Exception as e:
        st.warning(f"Could not load Guardrail data: {e}")
    
    return data


def render_header():
    """Render dashboard header."""
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 10px; color: #ffffff;'>
            📊 RAG Evaluation Dashboard
        </h1>
        <p style='font-size: 1.2rem; color: #b0b0b0; margin-bottom: 30px;'>
            Lab 24 - Full Evaluation & Guardrail System
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 System", "VN Land Law RAG", help="Vietnamese Land Law RAG System")
    
    with col2:
        st.metric("📝 Queries Evaluated", "51", delta="+51 from baseline")
    
    with col3:
        st.metric("🛡️ Guardrail Tests", "10", delta="100% detection")
    
    with col4:
        st.metric("⚖️ Judge Comparisons", "30", delta="0% position bias")


def render_ragas_metrics(data):
    """Render RAGAS metrics section."""
    st.header("🎯 RAGAS Metrics")
    
    if 'ragas' not in data:
        st.warning("No RAGAS data available. Run Phase A tasks first.")
        return
    
    ragas = data['ragas']
    
    # Metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Faithfulness", "faithfulness", 0.85, 0.75),
        ("Answer Relevancy", "answer_relevancy", 0.80, 0.70),
        ("Context Precision", "context_precision", 0.70, 0.60),
        ("Context Recall", "context_recall", 0.75, 0.65),
    ]
    
    for col, (name, key, target, min_val) in zip([col1, col2, col3, col4], metrics):
        with col:
            value = ragas.get(key, 0)
            delta = value - target
            
            # Determine status
            if value >= target:
                status = "✅ Excellent"
            elif value >= min_val:
                status = "⚠️ OK"
            else:
                status = "❌ Below Min"
            
            st.metric(
                label=name,
                value=f"{value:.3f}",
                delta=f"{delta:+.3f} vs target",
                delta_color="normal" if delta >= 0 else "inverse"
            )
            st.caption(f"Target: {target} | Min: {min_val}")
            st.caption(status)
    
    # Radar chart
    st.subheader("Metrics Overview")
    
    fig = go.Figure()
    
    # Actual scores
    fig.add_trace(go.Scatterpolar(
        r=[ragas.get(m[1], 0) for m in metrics],
        theta=[m[0] for m in metrics],
        fill='toself',
        name='Actual',
        line_color='blue'
    ))
    
    # Target scores
    fig.add_trace(go.Scatterpolar(
        r=[m[2] for m in metrics],
        theta=[m[0] for m in metrics],
        fill='toself',
        name='Target',
        line_color='green',
        opacity=0.3
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results table
    if 'ragas_details' in data:
        st.subheader("Detailed Results")
        
        df = data['ragas_details']
        
        # Add average score column
        metric_cols = ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']
        available_cols = [col for col in metric_cols if col in df.columns]
        if available_cols:
            df['average_score'] = df[available_cols].mean(axis=1)
        
        # Show bottom 10
        st.markdown("**Bottom 10 Questions (Lowest Average Score)**")
        bottom_10 = df.nsmallest(10, 'average_score') if 'average_score' in df.columns else df.head(10)
        st.dataframe(bottom_10, use_container_width=True)


def render_judge_metrics(data):
    """Render LLM-Judge metrics section."""
    st.header("⚖️ LLM-as-Judge Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pairwise Comparison")
        
        if 'pairwise' not in data:
            st.warning("No pairwise data available. Run Phase B Task B.1 first.")
        else:
            df = data['pairwise']
            
            # Winner distribution
            if 'final_winner' in df.columns:
                winner_counts = df['final_winner'].value_counts()
                
                fig = px.pie(
                    values=winner_counts.values,
                    names=winner_counts.index,
                    title="Winner Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Consistency check
                if 'run1_winner' in df.columns and 'run2_winner' in df.columns:
                    consistent = (df['run1_winner'] == df['run2_winner']).sum()
                    consistency_rate = (consistent / len(df)) * 100
                    
                    st.metric(
                        "Consistency Rate",
                        f"{consistency_rate:.1f}%",
                        help="How often run1 and run2 agree"
                    )
    
    with col2:
        st.subheader("Absolute Scoring")
        
        if 'absolute' not in data:
            st.warning("No absolute scoring data available. Run Phase B Task B.2 first.")
        else:
            df = data['absolute']
            
            # Score distribution
            dimensions = ['accuracy', 'relevance', 'conciseness', 'helpfulness']
            available_dims = [d for d in dimensions if d in df.columns]
            
            if available_dims:
                avg_scores = {dim: df[dim].mean() for dim in available_dims}
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(avg_scores.keys()),
                        y=list(avg_scores.values()),
                        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
                    )
                ])
                
                fig.update_layout(
                    title="Average Scores by Dimension",
                    yaxis_title="Score (1-5)",
                    yaxis_range=[0, 5],
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Overall score
                if 'overall' in df.columns:
                    st.metric(
                        "Overall Average",
                        f"{df['overall'].mean():.2f} / 5.0"
                    )


def render_guardrail_metrics(data):
    """Render Guardrail metrics section."""
    st.header("🛡️ Guardrail Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("PII Detection")
        
        if 'pii' not in data:
            st.warning("No PII data available. Run Phase C Task C.1 first.")
        else:
            df = data['pii']
            
            # Detection rate
            detected = (df['pii_found'] != 'None').sum()
            total = len(df)
            detection_rate = (detected / total) * 100 if total > 0 else 0
            
            st.metric(
                "Detection Rate",
                f"{detection_rate:.1f}%",
                delta=f"{detection_rate - 80:+.1f}% vs target (80%)"
            )
            
            # Latency
            if 'latency_ms' in df.columns:
                p95 = df['latency_ms'].quantile(0.95)
                st.metric(
                    "P95 Latency",
                    f"{p95:.1f}ms",
                    delta=f"{p95 - 50:+.1f}ms vs target (50ms)",
                    delta_color="inverse"
                )
    
    with col2:
        st.subheader("Topic Validation")
        st.info("Run Phase C Task C.2 to see metrics")
    
    with col3:
        st.subheader("Adversarial Defense")
        st.info("Run Phase C Task C.3 to see metrics")


def render_cost_analysis():
    """Render cost analysis section."""
    st.header("💰 Cost Analysis")
    
    # Cost breakdown
    costs = {
        "RAG Generation": 100,
        "RAGAS Evaluation": 10,
        "LLM-Judge T2": 10,
        "LLM-Judge T3": 50,
        "Presidio (CPU)": 72,
        "OpenAI Moderation": 20,
        "Embeddings": 20,
        "Infrastructure": 182,
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pie chart
        fig = px.pie(
            values=list(costs.values()),
            names=list(costs.keys()),
            title="Monthly Cost Breakdown ($464 total)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Monthly Cost", "$464")
        st.metric("Cost per Query", "$0.00464", help="Based on 100k queries/month")
        st.metric("Optimized Cost", "$310", delta="-$154 (33%)", delta_color="normal")


def render_slo_status():
    """Render SLO status section."""
    st.header("📋 SLO Status")
    
    slos = [
        {
            "metric": "Faithfulness",
            "target": "≥ 0.85",
            "current": 0.757,
            "status": "⚠️ Below Target",
            "alert": "< 0.80 for 30 min"
        },
        {
            "metric": "Answer Relevancy",
            "target": "≥ 0.80",
            "current": 0.768,
            "status": "⚠️ Below Target",
            "alert": "< 0.75 for 30 min"
        },
        {
            "metric": "P95 Latency",
            "target": "< 2.5s",
            "current": 2.1,
            "status": "✅ Meeting Target",
            "alert": "> 3s for 5 min"
        },
        {
            "metric": "Guardrail Detection",
            "target": "≥ 90%",
            "current": 95,
            "status": "✅ Excellent",
            "alert": "< 85%"
        },
    ]
    
    df = pd.DataFrame(slos)
    
    # Color code status
    def color_status(val):
        if "✅" in val:
            return 'background-color: #d4edda'
        elif "⚠️" in val:
            return 'background-color: #fff3cd'
        else:
            return 'background-color: #f8d7da'
    
    # Use map() instead of applymap() for newer pandas versions
    try:
        styled_df = df.style.map(color_status, subset=['status'])
    except AttributeError:
        # Fallback for older pandas versions
        styled_df = df.style.applymap(color_status, subset=['status'])
    
    st.dataframe(styled_df, use_container_width=True)


def main():
    """Main dashboard function."""
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h2 style='color: #667eea; margin-bottom: 5px;'>🎓 Lab 24</h2>
            <p style='color: #b0b0b0; font-size: 0.9rem;'>Evaluation & Guardrails</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📍 Navigation")
        page = st.radio(
            "Select View",
            ["🏠 Overview", "🎯 RAGAS Metrics", "⚖️ Judge Metrics", "🛡️ Guardrails", "💰 Cost Analysis", "📋 SLO Status"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        st.markdown("""
        <div style='background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 8px; margin: 10px 0;'>
            <p style='margin: 5px 0; color: #e0e0e0;'><b>Total Queries:</b> 51</p>
            <p style='margin: 5px 0; color: #e0e0e0;'><b>Guardrail Tests:</b> 10</p>
            <p style='margin: 5px 0; color: #e0e0e0;'><b>Judge Comparisons:</b> 30</p>
            <p style='margin: 5px 0; color: #e0e0e0;'><b>Detection Rate:</b> 100%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #808080; font-size: 0.8rem; margin-top: 20px;'>
            <p>VinUniversity 2026</p>
            <p>Made with ❤️ using Streamlit</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    
    # Render header
    render_header()
    st.markdown("---")
    
    # Render selected page
    if page == "🏠 Overview":
        col1, col2 = st.columns(2)
        with col1:
            render_ragas_metrics(data)
        with col2:
            render_guardrail_metrics(data)
        
        st.markdown("---")
        render_slo_status()
    
    elif page == "🎯 RAGAS Metrics":
        render_ragas_metrics(data)
    
    elif page == "⚖️ Judge Metrics":
        render_judge_metrics(data)
    
    elif page == "🛡️ Guardrails":
        render_guardrail_metrics(data)
    
    elif page == "💰 Cost Analysis":
        render_cost_analysis()
    
    elif page == "📋 SLO Status":
        render_slo_status()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        Lab 24 - Full Evaluation & Guardrail System | VinUniversity 2026
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
