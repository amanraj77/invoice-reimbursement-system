import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(
    page_title="Invoice System",
    page_icon="📄",
    layout="wide"
)

# Simple API configuration - no secrets needed for local development
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("🏢 IAI Solution Invoice Reimbursement System")
st.write("AI-powered invoice analysis with Google Gemini")

# Test backend connection
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        st.success("✅ Connected to backend successfully!")
    else:
        st.error("❌ Backend connection failed")
except:
    st.warning("⚠️ Backend not running. Start with: uvicorn app.main:app --reload")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose Page", ["📄 Invoice Analysis", "💬 Chat Assistant", "📊 System Info"])

if page == "📄 Invoice Analysis":
    st.header("📄 Invoice Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Policy Document")
        policy_file = st.file_uploader("Upload Policy PDF", type=['pdf'])
        
        st.subheader("👤 Employee Info")
        employee_name = st.text_input("Employee Name", placeholder="Enter name")
    
    with col2:
        st.subheader("📁 Invoice Files")
        invoices_zip = st.file_uploader("Upload Invoices ZIP", type=['zip'])
        
        if invoices_zip:
            st.success(f"✅ {invoices_zip.name}")
    
    if st.button("🚀 Analyze Invoices", type="primary", use_container_width=True):
        if not all([policy_file, invoices_zip, employee_name]):
            st.error("❌ Please provide all inputs")
        else:
            progress = st.progress(0)
            status = st.empty()
            
            try:
                status.text("📤 Uploading...")
                progress.progress(20)
                
                files = {'policy_file': policy_file, 'invoices_zip': invoices_zip}
                data = {'employee_name': employee_name}
                
                status.text("🧠 AI analyzing...")
                progress.progress(60)
                
                response = requests.post(f"{API_BASE_URL}/analyze-invoices", files=files, data=data, timeout=120)
                
                progress.progress(90)
                
                if response.status_code == 200:
                    result = response.json()
                    progress.progress(100)
                    status.text("✅ Complete!")
                    
                    # Display results
                    st.success("🎉 Analysis Complete!")
                    
                    summary = result.get('summary', {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total", summary.get('total_invoices', 0))
                    with col2:
                        st.metric("Approved", summary.get('approved', 0))
                    with col3:
                        st.metric("Total ₹", f"{summary.get('total_amount', 0):,.0f}")
                    with col4:
                        st.metric("Reimbursable ₹", f"{summary.get('total_reimbursable', 0):,.0f}")
                    
                    # Results table
                    results = result.get('analysis_results', [])
                    if results:
                        df_data = []
                        for inv in results:
                            status_icon = {'approved': '✅', 'declined': '❌', 'partial_approved': '⚠️'}.get(inv.get('status'), '❓')
                            df_data.append({
                                'Invoice': inv.get('invoice_id', 'N/A'),
                                'Amount': f"₹{inv.get('amount', 0):,.0f}",
                                'Status': f"{status_icon} {inv.get('status', '').replace('_', ' ').title()}",
                                'Alcohol': '🍷' if inv.get('contains_alcohol') else '✅'
                            })
                        
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # Download JSON
                        st.download_button(
                            "📄 Download Results",
                            data=json.dumps(result, indent=2),
                            file_name=f"analysis_{employee_name}.json",
                            mime="application/json"
                        )
                else:
                    st.error(f"❌ Failed: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                progress.empty()
                status.empty()

elif page == "💬 Chat Assistant":
    st.header("💬 Chat Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sample questions
    st.subheader("💡 Try These:")
    samples = [
        "Show me all declined invoices",
        "Which invoices contain alcohol?",
        "What's the total reimbursable amount?",
        "List invoices over ₹500"
    ]
    
    selected = st.selectbox("Sample questions:", [""] + samples)
    user_input = st.text_input("Ask a question:", value=selected)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Send"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                try:
                    with st.spinner("Thinking..."):
                        response = requests.post(f"{API_BASE_URL}/chat", json={"query": user_input}, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.messages.append({"role": "assistant", "content": result.get('response', 'No response')})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": f"Error: {response.text}"})
                        
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
                
                st.rerun()
    
    with col2:
        if st.button("Clear"):
            st.session_state.messages = []
            st.rerun()
    
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

elif page == "📊 System Info":
    st.header("📊 System Information")
    
    # System status
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            st.success("🟢 System Online")
            st.json(response.json())
        else:
            st.error("🔴 System Issues")
    except:
        st.warning("⚠️ Cannot connect to backend")
    
    # Policy info
    st.subheader("📋 IAI Solution Policy")
    
    policy_info = {
        "Food & Beverages": "₹200 per meal (no alcohol)",
        "Travel Expenses": "₹2,000 per trip + ₹150 daily cabs",
        "Accommodation": "₹50 per night",
        "Submission": "30 days with receipts"
    }
    
    for category, rule in policy_info.items():
        st.write(f"**{category}:** {rule}")
    
    # Features
    st.subheader("✨ Features")
    features = [
        "🧠 AI-powered analysis with Google Gemini",
        "🍷 Automatic alcohol detection",
        "💬 Natural language chat interface",
        "📊 Real-time analytics dashboard",
        "🔍 Intelligent document search"
    ]
    
    for feature in features:
        st.write(feature)
    
    # API endpoints
    st.subheader("🔗 API Endpoints")
    endpoints = [
        "**POST /analyze-invoices** - Upload and analyze invoice batch",
        "**POST /chat** - Natural language queries",
        "**GET /health** - System health check"
    ]
    
    for endpoint in endpoints:
        st.write(endpoint)