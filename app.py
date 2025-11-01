# app.py
# Financial Decision Simulation Model (Enhanced UI + Professional Styling)
# By: Akhilesh Kakarla

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime
from fpdf import FPDF
import xlsxwriter

# ---------------------------
# Page Config & Styling
# ---------------------------
st.set_page_config(page_title="Financial Decision Simulation Model", page_icon="📊", layout="wide")

# Custom CSS for premium look
st.markdown("""
    <style>
      /* Main title box */
      .title-box {
          font-size: 46px !important;
          color: white;
          background: linear-gradient(90deg, #0066ff, #00c6ff);
          padding: 18px;
          border-radius: 14px;
          text-align: center;
          font-weight: 800;
          letter-spacing: 1px;
          box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
      }

      /* Subtitle */
      .subtitle {
          text-align: center;
          color: #333;
          font-size: 18px;
          margin-bottom: 20px;
          font-weight: 500;
      }

      /* Sidebar controls */
      [data-testid="stSidebar"] {
          background-color: #f8f9fa;
          font-size: 18px !important;
          padding: 15px;
      }

      [data-testid="stSidebar"] label {
          font-size: 18px !important;
          font-weight: 600;
          color: #0d6efd !important;
      }

      [data-testid="stSidebar"] input, [data-testid="stSidebar"] .stSlider {
          font-size: 16px !important;
      }

      /* Cards and boxes */
      .kpi {
          background: #ffffff;
          padding: 14px;
          border-radius: 10px;
          text-align: center;
          box-shadow: 0 3px 10px rgba(0,0,0,0.1);
      }

      .css-1v0mbdj, .css-12oz5g7 { font-size: 16px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-box">📊 Financial Decision Simulation Model</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Professional Financial Simulator for Academic & Analytical Projects</div>', unsafe_allow_html=True)

# ---------------------------
# Sidebar Controls
# ---------------------------
st.sidebar.header("⚙️ Simulation Controls")
student_name = st.sidebar.text_input("Student Name", "Akhilesh Kakarla")
uploaded_file = st.sidebar.file_uploader("Optional: Upload CSV (historical data)", type=["csv"])
sales = st.sidebar.number_input("Base Sales (Rs.)", min_value=10000, max_value=50_000_000, value=500_000, step=10000)
growth_rate = st.sidebar.slider("Growth Rate (%)", 0.0, 0.5, 0.10)
cost_pct = st.sidebar.slider("Cost % of Revenue", 0.05, 0.9, 0.40)
tax_pct = st.sidebar.slider("Tax %", 0.0, 0.5, 0.20)
runs = st.sidebar.slider("Simulation Runs", 50, 5000, 300)
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=False)
refresh_seconds = st.sidebar.number_input("Refresh Interval (sec)", min_value=5, max_value=300, value=10)
save_folder = st.sidebar.text_input("Auto-save Folder", value="simulation_outputs")

os.makedirs(save_folder, exist_ok=True)

# ---------------------------
# Simulation Logic
# ---------------------------
def simulate_df(base_sales, gr, cost_pct, tax_pct, n_runs):
    rows = []
    for _ in range(n_runs):
        rev = base_sales * (1 + np.random.uniform(-gr, gr))
        cost = rev * np.random.uniform(cost_pct - 0.05, cost_pct + 0.05)
        profit = (rev - cost) * (1 - tax_pct)
        rows.append((rev, cost, profit))
    df = pd.DataFrame(rows, columns=["Revenue", "Cost", "Profit"])
    return df

# ---------------------------
# Excel Export with Chart
# ---------------------------
def save_excel_with_chart(df, filepath):
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Simulations', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Simulations']
        chart = workbook.add_chart({'type': 'column'})
        max_row = len(df)
        chart.add_series({
            'name': 'Profit',
            'values':     ['Simulations', 1, 2, max_row, 2],
            'categories': ['Simulations', 1, 0, max_row, 0],
        })
        chart.set_title({'name': 'Simulated Profits'})
        chart.set_x_axis({'name': 'Run'})
        chart.set_y_axis({'name': 'Profit (Rs.)'})
        worksheet.insert_chart('F2', chart, {'x_scale': 1.3, 'y_scale': 1.3})

# ---------------------------
# Chart Images for PDF
# ---------------------------
def save_chart_images(df, basepath):
    hist_path = f"{basepath}_hist.png"
    fig1, ax1 = plt.subplots(figsize=(8,4))
    ax1.hist(df["Profit"], bins=20, edgecolor='black')
    ax1.set_title("Simulated Profit Distribution")
    ax1.set_xlabel("Profit (Rs.)")
    ax1.set_ylabel("Frequency")
    fig1.tight_layout()
    fig1.savefig(hist_path, dpi=150)
    plt.close(fig1)

    sens_path = f"{basepath}_sens.png"
    grs = np.linspace(0.05, 0.25, 5)
    avg_profits = [simulate_df(sales, g, cost_pct, tax_pct, 200)["Profit"].mean() for g in grs]
    fig2, ax2 = plt.subplots(figsize=(8,4))
    ax2.plot(grs*100, avg_profits, marker='o', color='green')
    ax2.set_title("Growth Rate vs Average Profit")
    ax2.set_xlabel("Growth Rate (%)")
    ax2.set_ylabel("Average Profit (Rs.)")
    fig2.tight_layout()
    fig2.savefig(sens_path, dpi=150)
    plt.close(fig2)

    return hist_path, sens_path

# ---------------------------
# PDF Report Class
# ---------------------------
class ReportPDF(FPDF):
    def header(self):
        self.set_fill_color(0, 102, 255)
        self.rect(0, 0, 210, 20, 'F')
        self.set_text_color(255,255,255)
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'Financial Simulation Report', ln=True, align='C')
        self.ln(8)
        self.set_text_color(0,0,0)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120,120,120)
        self.cell(0, 8, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Page {self.page_no()}', align='C')

def create_pdf_2page(student, params, metrics, insights, img_hist, img_sens, pdf_path):
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Student: {student}", ln=True)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Simulation Parameters", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for k,v in params.items():
        pdf.multi_cell(0, 7, f"- {k}: {v}")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Key Metrics", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, f"Average Profit: Rs. {metrics['avg']:,.2f}")
    pdf.multi_cell(0, 7, f"Max Profit: Rs. {metrics['max']:,.2f}")
    pdf.multi_cell(0, 7, f"Min Profit: Rs. {metrics['min']:,.2f}")
    pdf.multi_cell(0, 7, f"Std Dev: Rs. {metrics['std']:,.2f}")
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Insights", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for line in insights:
        pdf.multi_cell(0, 7, f"- {line}")

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0,8,"Charts", ln=True)
    pdf.ln(6)
    if os.path.exists(img_hist):
        pdf.image(img_hist, x=15, y=30, w=180)
    pdf.add_page()
    if os.path.exists(img_sens):
        pdf.image(img_sens, x=15, y=30, w=180)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

# ---------------------------
# Run Simulation
# ---------------------------
def run_and_save_once():
    df_sim = simulate_df(sales, growth_rate, cost_pct, tax_pct, runs)
    metrics = {
        'avg': df_sim["Profit"].mean(),
        'max': df_sim["Profit"].max(),
        'min': df_sim["Profit"].min(),
        'std': df_sim["Profit"].std()
    }
    insights = [
        f"Higher growth rate improves profits.",
        f"Standard deviation = Rs. {metrics['std']:,.2f}",
        f"Simulation runs = {runs}"
    ]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = os.path.join(save_folder, f"financial_results_{ts}.xlsx")
    pdf_path = os.path.join(save_folder, f"financial_report_{ts}.pdf")
    save_excel_with_chart(df_sim, excel_path)
    baseimg = os.path.join(save_folder, f"sim_{ts}")
    img_hist, img_sens = save_chart_images(df_sim, baseimg)
    create_pdf_2page(student_name,
                    {"Sales":sales, "GrowthRate":growth_rate, "Cost%":cost_pct, "Tax%":tax_pct, "Runs":runs},
                    metrics, insights, img_hist, img_sens, pdf_path)
    return df_sim, metrics, insights, excel_path, pdf_path, img_hist, img_sens

# ---------------------------
# Main UI Controls
# ---------------------------
if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = False

if st.button("🚀 Start Simulation"):
    st.session_state.stop_flag = False

if st.button("🛑 Stop Simulation"):
    st.session_state.stop_flag = True

placeholder = st.empty()

if auto_refresh and not st.session_state.stop_flag:
    while not st.session_state.stop_flag:
        with placeholder.container():
            st.markdown(f"**Live Update:** {datetime.now().strftime('%H:%M:%S')} | Student: {student_name}")
            df_sim, metrics, insights, excel_path, pdf_path, img1, img2 = run_and_save_once()
            st.image(img1, caption="Profit Distribution")
            st.image(img2, caption="Sensitivity Chart")
            st.success(f"Saved Excel → {excel_path} | PDF → {pdf_path}")
        time.sleep(refresh_seconds)
else:
    if st.button("Run Once (Save Outputs)"):
        with placeholder.container():
            df_sim, metrics, insights, excel_path, pdf_path, img1, img2 = run_and_save_once()
            st.image(img1, caption="Profit Distribution")
            st.image(img2, caption="Sensitivity Chart")
            st.download_button("⬇️ Download CSV", data=df_sim.to_csv(index=False).encode('utf-8'),
                               file_name="simulation_data.csv", mime="text/csv")
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download PDF Report", data=f, file_name=os.path.basename(pdf_path), mime="application/pdf")
    else:
        st.info("Adjust parameters, then click 'Run Once' or enable Auto Refresh.")
