import streamlit as st
import pandas as pd
import json
import pydeck as pdk

st.set_page_config(page_title="Property Map", layout="wide")

try:
    with open("data.json", "r") as f:
        raw_data = json.load(f)

    
    data = raw_data.get("data", [])
    length = raw_data.get("length", len(data)) 
    df = pd.DataFrame(data)

    st.title(f"🗺️ Property Map with Tooltips - {length} listings")
    st.markdown("Streamlit + PyDeck")
    st.markdown("FastAPI + SQLAlchemy + Alembic + PostgreSQL")
    st.markdown("SQL data clean up, transformation, and loading into PostgreSQL")
    
    
    if not df.empty and "latitude" in df.columns and "longitude" in df.columns:
        st.success("✅ Properties loaded successfully!")

        
        with st.expander("📋 Property Data"):
            st.dataframe(df)

        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[longitude, latitude]',
            get_radius=70,
            get_fill_color=[255, 140, 0],
            pickable=True,
        )

        tooltip = {
            "html": "<b>{title}</b><br/>💶 {price_per_meter} €/m²<br/>🛏️ {room_category} rooms <br/> {pt_category}",
            "style": {
                "backgroundColor": "white",
                "color": "black"
            }
        }

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=df["latitude"].mean(),
                longitude=df["longitude"].mean(),
                zoom=11,
                pitch=40,
            ),
            layers=[layer],
            tooltip=tooltip
        ))

    else:
        st.warning("⚠️ No data with valid coordinates.")

except Exception as e:
    st.error("❌ Could not load property data.")
    st.exception(e)
