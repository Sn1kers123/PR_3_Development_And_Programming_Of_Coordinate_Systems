import streamlit as st

from gps.config import MAX_SPREAD_MS, REFRESH_S
from gps.plot import build_figure
from gps.receiver import start_receiver
from gps.stats import summary

st.set_page_config(page_title="Візуалізація вимірювань GPS", layout="wide",
                   initial_sidebar_state="collapsed")


@st.cache_resource
def get_store():
    return start_receiver()


store = get_store()

with st.sidebar:
    st.header("Налаштування")
    st.slider("Поріг розкиду часу, мс", 50, 3000, MAX_SPREAD_MS, 50, key="threshold")
    st.checkbox("Показувати слід руху", True, key="show_trail")
    st.slider("Довжина сліду, точок", 5, 300, 60, key="trail_len")
    if st.button("Скинути історію"):
        store.reset()

store.max_spread_ms = st.session_state["threshold"]

st.title("Візуалізація вимірювань GPS")


def fmt(p):
    return f"({p[0]:.2f}, {p[1]:.2f})" if p else "—"


@st.fragment(run_every=REFRESH_S)
def live_view():
    snap = store.snapshot()
    if not snap["connected"]:
        st.warning("Немає з'єднання з емулятором (ws://localhost:21701). Чи запущено Docker-контейнер?")

    last = snap["history"][-1] if snap["history"] else {"analytic": None, "numeric": None}
    spread = f"{snap['spread']:.0f} мс" if snap["spread"] is not None else "—"
    st.markdown(
        f"Супутників: {len(snap['sats'])} | розкид часу {spread} (поріг {snap['max_spread']} мс) | "
        f"аналітичний: {fmt(last['analytic'])} км | МНК: {fmt(last['numeric'])} км"
    )

    st.plotly_chart(build_figure(snap["sats"], snap["history"],
                                 st.session_state["trail_len"], st.session_state["show_trail"]))

    st.subheader("Порівняння методів")
    st.table(summary(snap["history"]))
    st.caption(f"Пропущено розрахунків (великий розкид часу або виродження): {snap['skipped']}. "
               "Стрибок — відстань між двома послідовними розрахунками одного методу.")


live_view()
