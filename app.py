from __future__ import annotations

import pandas as pd
import streamlit as st

from config import HORIZONS
from storage import load_latest


st.set_page_config(page_title="Temel Eaverse", layout="wide")
st.title("Temel Eaverse")
st.caption("Global Capital Radar temel akışı × Tier-1 kısa vadeli zamanlama kanıtı")

payload = load_latest()
cells = payload.get("cells", [])
meta = payload.get("metadata", {})
if not cells:
    st.warning("Henüz gözlem yok. `python run.py` çalıştırılmalı.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam hücre", meta.get("cell_count", 0))
c2.metric("Radar gözlemi", meta.get("radar_observed", 0))
c3.metric("Tier-1 gözlemi", meta.get("tier1_observed", 0))
c4.metric("Kanıtlanmış hücre", meta.get("proven_cells", 0))

df = pd.DataFrame(cells)
labels = {key: item["label"] for key, item in HORIZONS.items()}
selected_horizon = st.selectbox("Vade", list(HORIZONS), format_func=labels.get)
view = df[df.horizon == selected_horizon].copy()
view["Akış (mn USD)"] = view.flow_usd_m
view["Akış yüzdeliği"] = view.flow_percentile
view["Referans dönem"] = view.reference_count
view["Tier-1 N"] = view.tier1_n
view["Sonuç"] = view.combined_status
st.dataframe(
    view[["asset", "label", "Akış (mn USD)", "Akış yüzdeliği", "Referans dönem", "Tier-1 N", "Sonuç"]],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Tüm varlık × vade matrisi")
matrix = df.pivot(index="asset", columns="horizon", values="combined_status")
matrix = matrix.reindex(columns=list(HORIZONS))
st.dataframe(matrix, use_container_width=True)

st.subheader("Yöntem keşfi ve model karşılaştırması")
st.caption("İleri örnek oluşmadan yöntem seçilmez. Tüm adaylar aynı anda gölge olarak izlenir.")
st.dataframe(pd.DataFrame(payload.get("methods", [])), use_container_width=True, hide_index=True)

with st.expander("Kaynak ve kanıt ayrıntıları"):
    asset = st.selectbox("Varlık", sorted(df.asset.unique()))
    row = df[(df.asset == asset) & (df.horizon == selected_horizon)].iloc[0]
    st.json(row.evidence)

