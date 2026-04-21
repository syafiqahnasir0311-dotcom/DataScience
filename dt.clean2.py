import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Data Cleaning App", page_icon="🧹", layout="wide")

st.title("🧹 Data Cleaning Application")
st.write("Upload, clean, analyze, and download your dataset easily!")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload CSV or Excel File", type=['csv', 'xlsx'])

if uploaded_file is not None:

    # ---------------- READ FILE SAFELY ----------------
    try:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file, encoding='latin1')
        else:
            data = pd.read_excel(uploaded_file)

    except Exception as e:
        st.error("❌ Error reading file")
        st.exception(e)
        st.stop()

    st.success("✅ File uploaded successfully!")

    # ---------------- SESSION STATE ----------------
    if "cleaned_data" not in st.session_state:
        st.session_state.cleaned_data = data.copy()

    df = st.session_state.cleaned_data

    # ---------------- SIDEBAR ----------------
    st.sidebar.header("🧰 Cleaning Controls")

    if st.sidebar.button("🔄 Reset Data"):
        st.session_state.cleaned_data = data.copy()
        st.success("Data reset successfully!")

    # ---------------- DATA PREVIEW ----------------
    st.subheader("📊 Data Preview")
    st.dataframe(df)

    # ---------------- DATA INFO ----------------
    st.subheader("📋 Data Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())

    # ---------------- COLUMN INFO ----------------
    st.write("### 🧾 Column Information")
    st.dataframe(df.dtypes)

    # ---------------- CLEANING OPTIONS ----------------
    st.subheader("🧹 Cleaning Options")

    # REMOVE MISSING
    if st.button("Remove Missing Values"):
        df = df.dropna()
        st.session_state.cleaned_data = df
        st.success("Missing values removed!")

    # FILL MISSING
    if st.button("Fill Missing Values"):
        num_cols = df.select_dtypes(include=['number']).columns
        cat_cols = df.select_dtypes(include=['object']).columns

        # numeric → mean
        df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

        # categorical → mode (safe)
        for col in cat_cols:
            if df[col].mode().empty:
                df[col].fillna("Unknown", inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)

        st.session_state.cleaned_data = df
        st.success("Missing values filled!")

    # REMOVE DUPLICATES
    if st.button("Remove Duplicates"):
        df = df.drop_duplicates()
        st.session_state.cleaned_data = df
        st.success("Duplicates removed!")

    # DROP COLUMN
    st.subheader("🗑 Remove Columns")
    column_to_drop = st.selectbox("Select column to drop", df.columns)

    if st.button("Drop Column"):
        df = df.drop(columns=[column_to_drop])
        st.session_state.cleaned_data = df
        st.success(f"{column_to_drop} removed!")

    # ---------------- FILTER DATA ----------------
    st.subheader("🔍 Filter Data")

    selected_column = st.selectbox("Select column to filter", df.columns)

    if df[selected_column].dtype == 'object':
        unique_values = df[selected_column].dropna().unique()
        selected_value = st.selectbox("Select value", unique_values)

        if st.button("Apply Filter"):
            df = df[df[selected_column] == selected_value]
            st.session_state.cleaned_data = df
            st.success("Filter applied!")

    # ---------------- SIMPLE VISUALIZATION ----------------
    st.subheader("📊 Data Visualization")

    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) > 0:
        selected_num_col = st.selectbox("Select numeric column", numeric_cols)

        if st.button("Show Histogram"):
            fig, ax = plt.subplots()
            ax.hist(df[selected_num_col].dropna())
            ax.set_title(f"Distribution of {selected_num_col}")
            st.pyplot(fig)

    # ---------------- CLEANED DATA ----------------
    st.subheader("📊 Cleaned Data")
    st.dataframe(df)

    # ---------------- DOWNLOAD ----------------
    st.subheader("📥 Download Cleaned Data")

    file_type = st.selectbox(
        "Choose file format",
        ["CSV", "Excel"]
    )

    if file_type == "CSV":
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

    elif file_type == "Excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Cleaned Data')

        st.download_button(
            label="Download Excel",
            data=output.getvalue(),
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("👆 Please upload a file to start")