import streamlit as st
import pandas as pd
import hiplot as hip
import tempfile

# ──────────────────────── Page setup ────────────────────────
st.set_page_config(layout="wide")
st.title("📊 Interactive Hiplot Explorer")

# ──────────────────────── File upload ───────────────────────
uploaded_file = st.file_uploader("Upload a Parquet file")

if uploaded_file:
    df = pd.read_parquet(uploaded_file)
    st.success(f"✅ Loaded DataFrame with shape {df.shape}")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    selected_cols = st.multiselect(
        "Select columns to plot", numeric_cols, default=numeric_cols[:5]
    )

    if selected_cols:
        st.subheader("🔍 Apply filters to selected columns")
        filters = {}

        for col in selected_cols:
            col_min, col_max = float(df[col].min()), float(df[col].max())
            val_range = st.slider(
                f"{col} range",
                min_value=col_min,
                max_value=col_max,
                value=(col_min, col_max),
            )
            filters[col] = val_range

        # ─────────────── Apply filters ───────────────
        df_filtered = df.copy()
        for col, (low, high) in filters.items():
            df_filtered = df_filtered[(df_filtered[col] >= low) & (df_filtered[col] <= high)]

        st.write(f"Filtered data shape: {df_filtered.shape}")

        if df_filtered.empty:
            st.warning("❌ No data after filtering. Try adjusting the sliders.")
        else:
            # Optional color column (categorical)
            color_col = st.selectbox(
                "Color by (optional)",
                [None] + df.select_dtypes(include=["object", "category"]).columns.tolist(),
            )

            # ─────────────── Prepare dataframe for Hiplot ───────────────
            df_hip = df_filtered[selected_cols].copy()
            df_hip["uid"] = df_filtered.index  # <-- keep original index
            # Make sure uid is the first column (optional, purely cosmetic)
            df_hip = df_hip[["uid"] + selected_cols]

            if color_col:
                df_hip["color"] = df_filtered[color_col].astype(str)

            # ─────────────── Render Hiplot ───────────────
            exp = hip.Experiment.from_dataframe(df_hip)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
                exp.to_html(f.name)
                with open(f.name) as html_file:
                    st.components.v1.html(html_file.read(), height=600, scrolling=True)
    else:
        st.info("Please select at least one numeric column to continue.")

