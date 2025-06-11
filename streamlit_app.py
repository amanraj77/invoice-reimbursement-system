import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(
    page_title="Invoice System",
    page_icon="📄",
    layout="wide"
)

# API configuration
API_BASE_URL = "https://invoice-backend-lhn7.onrender.com"

st.title("🏢 IAI Solution Invoice Reimbursement System")
st.write("AI-powered invoice analysis with Google Gemini")

# DEBUG SECTION
st.write("**Debug Info:**")
st.write(f"Backend URL: {API_BASE_URL}")

if st.button("🔬 Debug Backend"):
    st.write("Testing backend connection...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=30)
        st.success(f"✅ Root endpoint works: {response.status_code}")
        st.json(response.json())
    except Exception as e:
        st.error(f"❌ Root endpoint failed: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=30)
        st.success(f"✅ Health endpoint works: {response.status_code}")
        st.json(response.json())
    except Exception as e:
        st.error(f"❌ Health endpoint failed: {e}")

st.write("---")

# Test backend connection
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=30)
    if response.status_code == 200:
        st.success("✅ Connected to backend successfully!")
        st.json(response.json())
        backend_connected = True
    else:
        st.error(f"❌ Backend returned status {response.status_code}")
        backend_connected = False
except Exception as e:
    st.error(f"❌ Backend connection failed: {str(e)}")
    backend_connected = False

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose Page", ["📄 Invoice Analysis", "�� Chat Assistant"])

if page == "📄 Invoice Analysis":
    st.header("📄 Invoice Analysis")
    
    if not backend_connected:
        st.warning("⚠️ Backend not connected. Please wait for backend to start.")
        st.stop()
    
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
            with st.spinner("�� AI analyzing invoices..."):
                try:
                    files = {'policy_file': policy_file, 'invoices_zip': invoices_zip}
                    data = {'employee_name': employee_name}
                    
                    response = requests.post(f"{API_BASE_URL}/analyze-invoices", files=files, data=data, timeout=120)
                    
                    if response.status_code == 200:
                        result = response.json()
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
                    else:
                        st.error(f"❌ Analysis failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

elif page == "💬 Chat Assistant":
    st.header("💬 Chat Assistant")
    
    if not backend_connected:
        st.warning("⚠️ Backend not connected. Chat feature unavailable.")
        st.stop()
    
    user_input = st.text_input("Ask a question:", placeholder="Show me all declined invoices")
    
    if st.button("Send") and user_input:
        try:
            with st.spinner("Thinking..."):
                response = requests.post(f"{API_BASE_URL}/chat", json={"query": user_input}, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                st.success("Response:")
                st.write(result.get('response', 'No response'))
            else:
                st.error(f"Chat failed: {response.text}")
                
        except Exception as e:
            st.error(f"Chat error: {str(e)}")
