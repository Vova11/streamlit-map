import streamlit as st
import pandas as pd
import json
import pydeck as pdk

st.set_page_config(page_title="Property Map", layout="wide")

# Load data
try:
    with open("data_v2.json", "r") as f:
        raw_data = json.load(f)

    data = raw_data.get("data", [])
    length = raw_data.get("length", len(data))
    df = pd.DataFrame(data)

    st.title(f"🗺️ Property Map with Tooltips - {length} listings")
    st.markdown("Streamlit + PyDeck")
    st.markdown("FastAPI + SQLAlchemy + Alembic + PostgreSQL")

    if not df.empty and "latitude" in df.columns and "longitude" in df.columns:
        st.success("✅ Properties loaded successfully!")

        # Sidebar filters
        st.sidebar.header("🔍 Search Filters")

        cities = sorted(df["city"].dropna().unique().tolist())
        selected_cities = st.sidebar.multiselect("Cities", options=cities)

        deal_options = ["🟢 Deal", "🟡 Normal", "🔴 Pricey"]
        selected_deals = st.sidebar.multiselect("Price Categories", options=deal_options)

        room_categories = sorted(df["room_category"].dropna().unique().tolist())
        selected_rooms = st.sidebar.multiselect("Room Categories", options=room_categories)

        # Filter data
        filtered_df = df.copy()
        if selected_cities:
            filtered_df = filtered_df[filtered_df["city"].isin(selected_cities)]
        if selected_deals:
            filtered_df = filtered_df[filtered_df["pt_category"].isin(selected_deals)]
        if selected_rooms:
            filtered_df = filtered_df[filtered_df["room_category"].isin(selected_rooms)]

        st.subheader(f"Filtered Properties: {len(filtered_df)}")

        with st.expander("📋 Property Data"):
            st.dataframe(filtered_df)

        if not filtered_df.empty:
            # PyDeck map layer
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position='[longitude, latitude]',
                get_radius=70,
                get_fill_color=[255, 140, 0],
                pickable=True,
                auto_highlight=True
            )

            # Static tooltip (not clickable)
            tooltip = {
                "html": """
                    <b>{title}</b><br/>
                    💶 {price_per_meter} €/m²<br/>
                    🛏️ {room_category} rooms <br/>
                    {pt_category}
                """,
                "style": {
                    "backgroundColor": "white",
                    "color": "black"
                }
            }

            # Render map
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=pdk.ViewState(
                    latitude=filtered_df["latitude"].mean(),
                    longitude=filtered_df["longitude"].mean(),
                    zoom=11,
                    pitch=40,
                ),
                layers=[layer],
                tooltip=tooltip
            ))

            st.subheader("🏡 Selected Property Preview")

            selected_title = st.selectbox("Choose a property to preview:", options=filtered_df["title"])

            selected_property = filtered_df[filtered_df["title"] == selected_title].iloc[0]

            st.markdown(f"### {selected_property['title']}")
            st.markdown(f"**City:** {selected_property['city']}")
            st.markdown(f"**District:** {selected_property['district']}")
            st.markdown(f"**Price per m²:** {selected_property['price_per_meter']} €")
            st.markdown(f"**Rooms:** {selected_property['room_category']}")
            st.markdown(f"**Deal Type:** {selected_property['pt_category']}")
            st.markdown(f"[🔗 Open Listing]({selected_property['url']})")

            # Show image if available
            image_url = selected_property.get("url", "")
            if image_url and image_url.lower() != "none":
                st.image(image_url, use_container_width=True)
            else:
                st.info("ℹ️ No image available for this property.")
        else:
            st.warning("⚠️ No properties match the selected filters.")

    else:
        st.warning("⚠️ No data with valid coordinates.")

except Exception as e:
    st.error("❌ Could not load property data.")
    st.exception(e)
