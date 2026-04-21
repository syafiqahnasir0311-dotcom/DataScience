import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io 

# ================= PAGE CONFIG =================
st.set_page_config(page_title='Analyze Your Data', page_icon='💻', layout='wide')
st.title('💻 Analyze Your Data')
st.write('Upload A **CSV** Or An **Excel** File To Explore Data Interactively!')

# ================= FILE UPLOAD =================
uploaded_file = st.file_uploader('Upload A CSV Or An Excel File',type=['csv','xlsx'])

if uploaded_file is not None:
    try:
         # 🔹 Check file type
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)

        elif uploaded_file.name.endswith('.xlsx'):
            data = pd.read_excel(uploaded_file)

        else:
            st.error("Unsupported file format!")
            st.stop()

        # converting bool column [True / False] as str
        bool_cols = data.select_dtypes(include = ['bool']).columns
        data[bool_cols] = data[bool_cols].astype('str')

    except Exception as e:
        st.error('❌ Could Not Read CSV / Ecxel File. Please Check The File Format')
        st.exception(e)
        st.stop()

    st.success('✅ File Uploaded Successfully!')

    # ================= DATA PREVIEW =================
    st.write('### 🧐 Preview Of Data')
    st.dataframe(data.head())

    st.write('### 📋 Data Overview')
    st.write('Number Of Rows : ', data.shape[0])
    st.write('Number Of Columns : ', data.shape[1])
    st.write('Number Of Missing Values : ', data.isnull().sum().sum())
    st.write('Number Of Duplicate Records : ', data.duplicated().sum())

    # ================= DATA INFO =================
    st.write('### 🗂 The Complete Summary Of Dataset')
    buffer = io.StringIO()
    data.info(buf = buffer) 
    st.code(buffer.getvalue()) 

    # ================= STATISTICS =================
    # Numeric Summary
    st.write('### 📈 Statistical Summary Of Dataset')
    st.dataframe(data.describe())

    # Non-Numeric Summary Safe fix (Important)
    non_num_cols = data.select_dtypes(include=['object', 'bool', 'category'])

    if len(non_num_cols.columns) > 0: 
        st.write('### 📊 Statistical Summary For Non-Numerical Features Of Dataset')
        st.dataframe(non_num_cols.describe())
    else:
        st.info('No Non-Numerical Features Found In Dataset')

    # ================= COLUMN SELECTION =================
    st.write('### 🔎 Select Columns For Analysis')
    selected_columns = st.multiselect('Choose Columns', data.columns.tolist())

    if selected_columns:
        st.dataframe(data[selected_columns].head())
    else:
        st.info('No Columns Selected. Showing Full Dataset')
        st.dataframe(data.head())
    
    # ================= VISUALIZATION =================
    st.write('### 📊 Data Visualization')
    st.write('Select columns and generate charts interactively')

    # 🔹 Numeric columns only for safety
    numeric_cols = data.select_dtypes(include='number').columns.tolist()

    if len(numeric_cols) == 0:
        st.warning('No numeric columns available for visualization.')
    else:
        # 🔹 Selectbox for main axes
        x_axis = st.selectbox('Select X-Axis', options=numeric_cols)
        y_axis = st.selectbox('Select Y-Axis', options=numeric_cols)

        # ❗ prevent same selection
        if x_axis == y_axis:
            st.warning("⚠️ X and Y cannot be the same column!")
            st.stop()
        
        # 🔹 Multiselect for extra analysis (optional use)
        extra_cols = st.multiselect(
            'Select Extra Columns (for comparison / future use)',
            options=numeric_cols
        )

        # 🔹 Chart type selector (cleaner than many buttons)
        chart_type = st.selectbox(
            'Choose Chart Type',
            ['Line Chart', 'Scatter Plot', 'Bar Chart', 'Histogram', 'Box Plot', 'Correlation Heatmap']
        )

        # 🔹 Single generate button (IMPORTANT UX improvement)
        if st.button('🚀 Generate Chart'):
            
            fig, ax = plt.subplots()

            # ================= LINE =================
            if chart_type == 'Line Chart':
                st.write('### 📈 Line Chart')
                ax.plot(data[x_axis], data[y_axis])
                ax.set_title(f'Line Chart: {x_axis} vs {y_axis}')

            # ================= SCATTER =================
            elif chart_type == 'Scatter Plot':
                st.write('### 🔵 Scatter Plot')
                ax.scatter(data[x_axis], data[y_axis])
                ax.set_title(f'Scatter Plot: {x_axis} vs {y_axis}')

            # ================= BAR =================
            elif chart_type == 'Bar Chart':
                st.write('### 📊 Bar Chart')
                # 🔥 prevent crash for large dataset bar chart
                if len(data) > 100:
                    st.warning("Dataset too large for bar chart → showing first 100 rows only")
                    data_plot = data.head(100)
                else:
                    data_plot = data

                ax.bar(data[x_axis], data[y_axis])
                ax.set_title(f'Bar Chart: {x_axis} vs {y_axis}')

            # ================= HISTOGRAM =================
            elif chart_type == 'Histogram':
                st.write('### 📊 Histogram')
                ax.hist(data[x_axis], bins=20)
                ax.set_title(f'Histogram of {x_axis}')

            # ================= BOX PLOT =================
            elif chart_type == 'Box Plot':
                st.write('### 📦 Box Plot')
                ax.boxplot(data[x_axis])
                ax.set_title(f'Box Plot of {x_axis}')

            # ================= HEATMAP =================
            elif chart_type == 'Correlation Heatmap':
                st.write('### 🔥 Correlation Heatmap')
                corr = data[numeric_cols].corr()
                plt.figure(figsize=(10, 6))
                sns.heatmap(corr, annot=True, cmap='coolwarm')
                ax.set_title('Correlation Heatmap')

            st.pyplot(fig)

else:
    st.info("📂 Please upload a file to start analysis.")



    