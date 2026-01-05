import streamlit as st
import pandas as pd
import plotly.express as px
def style_fig(fig, title: str | None = None):
    if title is not None:
        fig.update_layout(title=title)

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",   # fondo exterior transparente
        plot_bgcolor="rgba(0,0,0,0)",    # fondo interior transparente
        title=dict(x=0.0, xanchor="left"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
    )

    # Grid suave
    fig.update_xaxes(showgrid=True, gridcolor="rgba(15, 23, 42, 0.08)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(15, 23, 42, 0.08)", zeroline=False)

    return fig

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    # Tipos básicos
    for col in ["store_nbr", "year", "month", "quarter"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df

st.set_page_config(page_title="Dashboard Ventas", page_icon="📊", layout="wide",initial_sidebar_state="expanded")

st.title("📊 Dashboard de Ventas")
st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
div[data-testid="stMetric"] {
    background: rgba(245, 247, 251, 0.9);
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(15, 23, 42, 0.08);
}
</style>
""", unsafe_allow_html=True)
# Carga de datos: si lo vas a subir a Streamlit Cloud, mejor permitir upload
uploaded = st.file_uploader("Sube el dataset (CSV)", type=["csv"])
if not uploaded:
    st.info("Sube el CSV para empezar.")
    st.stop()

df = load_data(uploaded)

tab1, tab2, tab3, tab4 = st.tabs(["🌍 Global", "🏪 Tienda", "🗺️ Estado", "✨ Extra"])

with tab1:
    st.subheader("Conteo general")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tiendas", int(df["store_nbr"].nunique()))
    c2.metric("Productos",int(df["family"].nunique()))
    c3.metric("Estados",int(df["state"].nunique()))
    c4.metric("Meses",int(df[["year","month"]].drop_duplicates().shape[0]))

    st.subheader("Top productos más vendidos")
    top_prod = df.groupby("family",as_index=False)["sales"].sum().sort_values("sales",ascending=False).head(10)
    fig = px.bar(top_prod, x="sales", y="family", orientation="h")
    fig = style_fig(fig, "Top productos más vendidos")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Distribución ventas por tienda")
    by_store = df.groupby("store_nbr",as_index=False)["sales"].sum()
    fig = px.histogram(by_store, x="sales")
    fig = style_fig(fig,"Distribución ventas por tienda")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top tiendas con ventas en promoción")
    promo  = df[df["onpromotion"]>0].groupby("store_nbr",as_index=False)["sales"].sum().sort_values("sales",ascending=False).head(10)
    fig = px.bar(promo , x="sales",y="store_nbr", orientation="h")
    fig = style_fig(fig,"Top tiendas con ventas en promoción")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Estacionalidad")
    colA, colB, colC = st.columns(3)
    dow = df.groupby("day_of_week",as_index=False)["sales"].mean().sort_values("sales", ascending=False)
    fig = px.bar(dow, x="day_of_week", y="sales")
    fig = style_fig(fig,"Venta media por días de la semana")
    colA.plotly_chart(fig, use_container_width=True)

    wk = df.groupby("week",as_index=False)["sales"].mean().sort_values("sales", ascending=False)
    fig = px.line(wk, x="week", y="sales")
    fig = style_fig(fig,"Ventas media por semana")
    colB.plotly_chart(fig, use_container_width=True)

    mo = df.groupby("month",as_index=False)["sales"].mean().sort_values("sales", ascending=False)
    fig = px.line(mo, x="month", y="sales")
    fig = style_fig(fig,"Ventas media por mes")
    colC.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Análisis por tienda")
    store = st.selectbox("Selecciona tienda",sorted(df["store_nbr"].dropna().unique()))
    d = df[df["store_nbr"] == store]

    c1, c2 = st.columns(2)
    c1.metric("Productos vendidos",int(d["sales"].sum()))
    #c2.metric("Productos vendidos",d["family"].count())
    c2.metric("Productos vendidos en promoción",int(d[d["onpromotion"]>0]["sales"].sum()))


    sales_year = d.groupby("year",as_index=False)["sales"].sum().sort_values("year")
    fig = px.bar(sales_year, x="year", y="sales")
    fig = style_fig(fig,"Ventas por año")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Análisis por estado")
    state = st.selectbox("Selecciona estado",sorted(df["state"].dropna().unique()))
    d = df[df["state"] == state]

    transactions_year = d.groupby("year",as_index=False)["transactions"].sum().sort_values("year")
    fig = px.bar(transactions_year, x="year", y="transactions")
    fig = style_fig(fig,"Transacciones por año")
    st.plotly_chart(fig, use_container_width=True)

    top_store = d.groupby("store_nbr",as_index=False)["sales"].sum().sort_values("sales",ascending=False)
    fig = px.bar(top_store, x="store_nbr", y="sales")
    fig = style_fig(fig,"Ranking de tiendas con más ventas")
    st.plotly_chart(fig, use_container_width=True)

    top_family = d.groupby("family",as_index=False)["sales"].sum().sort_values("sales",ascending=False)
    st.success(f"Producto más vendido en {state}: {top_family.iloc[0]['family']}")
    
with tab4:
    st.subheader("Extra: impacto de promociones")
    d0 = df[df["onpromotion"] == 0]["sales"].mean()
    d1 = df[df["onpromotion"] > 0]["sales"].mean()
    st.metric("Sales media sin promo", float(d0))
    st.metric("Sales media con promo", float(d1))

    #daily = df.dropna(subset=["date"]).groupby("date", as_index=False)
    
    daily_no_prom = df[df["onpromotion"] == 0].groupby("date", as_index=False)["sales"].sum()
    fig = px.line(daily_no_prom, x="date", y="sales")
    fig = style_fig(fig,"Distribución de ventas sin promo")
    st.plotly_chart(fig, use_container_width=True)

    daily_prom = df[df["onpromotion"] > 0].groupby("date", as_index=False)["sales"].sum()
    fig = px.line(daily_prom, x="date", y="sales")
    fig = style_fig(fig,"Distribución de ventas con promo")
    st.plotly_chart(fig, use_container_width=True)