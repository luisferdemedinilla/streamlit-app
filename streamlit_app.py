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

@st.cache_data
def load_store(df,store):
    return df[df["store_nbr"] == store]

@st.cache_data
def load_state(df,state):
    return df[df["state"] == state]

st.set_page_config(page_title="Dashboard Ventas", page_icon="📊", layout="wide",initial_sidebar_state="expanded")
st.markdown("""
<style>
.block-container {
    padding-top: 2.5rem;
}
</style>
""", unsafe_allow_html=True)

st.title("Dashboard de Ventas")
st.caption("📊 Panel interactivo de análisis de ventas")
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
    st.subheader("Visión global")

    # KPIs
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tiendas", int(df["store_nbr"].nunique()))
        c2.metric("Productos", int(df["family"].nunique()))
        c3.metric("Estados", int(df["state"].nunique()))
        c4.metric("Meses", int(df[["year","month"]].drop_duplicates().shape[0]))

    st.divider()

    # Primera fila (2 tarjetas)
    col1, col2 = st.columns(2)

    with col1.container(border=True):
        st.subheader("Top productos más vendidos")
        top_prod = (
            df.groupby("family", as_index=False)["sales"]
              .sum()
              .sort_values("sales", ascending=True)
              .tail(10)
        )
        fig = px.bar(top_prod, x="sales", y="family", orientation="h")
        #fig = style_fig(fig)
        #fig.update_traces(marker_color="#4F46E5")
        st.plotly_chart(fig, use_container_width=True)

    with col2.container(border=True):
        st.subheader("Distribución ventas por tienda")
        by_store = df.groupby("store_nbr", as_index=False)["sales"].sum()
        fig = px.histogram(by_store, x="sales",nbins=20)
        #fig.update_traces(marker_color="#4F46E5")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Segunda fila (2 tarjetas)
    col3, col4 = st.columns(2)

    with col3.container(border=True):
        st.subheader("Top tiendas con ventas en promoción")
        promo = (
            df[df["onpromotion"] > 0]
              .groupby("store_nbr", as_index=False)["sales"]
              .sum()
              .sort_values("sales", ascending=True)
              .head(10)
        )
        #promo["store_nbr"] = promo["store_nbr"].astype(str)
        fig = px.bar(promo, x="sales", y="store_nbr", orientation="h")
        fig.update_yaxes(type="category")
        st.plotly_chart(fig, use_container_width=True)

    with col4.container(border=True):
        st.subheader("Estacionalidad: día con mayor venta media")
        dow = (
            df.groupby("day_of_week", as_index=False)["sales"]
              .mean()
              .sort_values("sales", ascending=False)
        )
        fig = px.bar(dow, x="day_of_week", y="sales")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Tercera fila: 2 tarjetas para semana y mes
    col5, col6 = st.columns(2)

    with col5.container(border=True):
        st.subheader("Estacionalidad: venta media por semana")
        wk = (
            df.groupby("week", as_index=False)["sales"]
              .mean()
              .sort_values("week")
        )
        fig = px.line(wk, x="week", y="sales",markers=True)
        #fig.update_traces(line=dict(color="#4F46E5", width=3))
        #color_discrete_sequence=["#4F46E5", "#22C55E", "#F59E0B"])
        st.plotly_chart(fig, use_container_width=True)
        
    with col6.container(border=True):
        st.subheader("Estacionalidad: venta media por mes")
        mo = (
            df.groupby("month", as_index=False)["sales"]
              .mean()
              .sort_values("month")
        )
        fig = px.line(mo, x="month", y="sales",markers=True)
        st.plotly_chart(fig, use_container_width=True)


with tab2:
    st.subheader("Análisis por tienda")
    store = st.selectbox("Selecciona tienda", sorted(df["store_nbr"].dropna().unique()))
    d = load_store(df,store)

    with st.container(border=True):
        c1, c2 = st.columns(2)
        total_sales = d["sales"].sum()
        promo_sales = d[d["onpromotion"] > 0]["sales"].sum()
        c1.metric("Ventas totales (sales)", f"{total_sales:,.2f}")
        c2.metric("Ventas en promoción (sales)", f"{promo_sales:,.2f}")

    with st.container(border=True):
        st.subheader("Ventas por año")
        sales_year = d.groupby("year", as_index=False)["sales"].sum().sort_values("year")
        sales_year["year"] = sales_year["year"].astype(str)
        fig = px.bar(sales_year, x="year", y="sales")
        fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside")
        fig.update_traces(width=0.4)
        fig.update_yaxes(title="Ventas", tickformat=",.0f")
        fig.update_xaxes(type="category")
        st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.subheader("Análisis por estado")
    state = st.selectbox("Selecciona estado", sorted(df["state"].dropna().unique()))
    d = load_state(df,state)

    col1, col2 = st.columns(2)   #[3, 2]

    with col1.container(border=True):
        st.subheader("Transacciones por año")
        transactions_year = d.groupby("year", as_index=False)["transactions"].sum().sort_values("year")
        transactions_year["year"] = transactions_year["year"].astype(str)
        fig = px.bar(transactions_year, x="year", y="transactions")
        fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside")
        fig.update_yaxes(title="Transacciones", tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

    with col2.container(border=True):
        st.subheader("Ranking de tiendas con más ventas")
        top_store = d.groupby("store_nbr", as_index=False)["sales"].sum().sort_values("sales", ascending=True)
        #top_store = top_store[top_store["sales"] > 0]
        fig = px.bar(top_store, x="sales", y="store_nbr", orientation="h")
        fig.update_xaxes(title="Ventas", tickformat=",.0f")
        fig.update_yaxes(type="category")
        st.plotly_chart(fig, use_container_width=True)

    top_family = d.groupby("family", as_index=False)["sales"].sum().sort_values("sales", ascending=False)
    st.success(f"Producto más vendido en {state}: {top_family.iloc[0]['family']}")

    
with tab4:
    st.subheader("Extra: impacto de promociones")

    with st.container(border=True):
        d0 = df[df["onpromotion"] == 0]["sales"].mean()
        d1 = df[df["onpromotion"] > 0]["sales"].mean()
        c1, c2 = st.columns(2) 
        c1.metric("Sales media sin promo", f"{d0:,.2f}")
        c2.metric("Sales media con promo", f"{d1:,.2f}")

    dtemp = df.dropna(subset=["date"]).copy()
    dtemp["promo"] = dtemp["onpromotion"].gt(0).map({True: "Con promo", False: "Sin promo"})
    
    series = (
    dtemp.groupby([pd.Grouper(key="date", freq="W-MON"), "promo"], as_index=False)["sales"]
         .sum()
         .sort_values("date")
)

    fig = px.line(series, x="date", y="sales", color="promo", markers=True,
                title="Ventas semanales: con vs sin promo")

    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(dtick="M12", tickformat="%Y")  # ← solo años
    fig.update_xaxes(range=[series["date"].min() - pd.Timedelta(days=7), series["date"].max() + pd.Timedelta(days=7)])
    st.plotly_chart(fig, use_container_width=True)