import altair as alt
from vega_datasets import data
import streamlit as st


states = alt.topo_feature(data.us_10m.url, 'states')
source = data.population_engineers_hurricanes.url
variable_list = ['population', 'engineers', 'hurricanes']




st.title("Just a title")

c = alt.Chart(states).mark_geoshape().encode(
    alt.Color(alt.repeat('row'), type='quantitative')
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(source, 'id', variable_list)
).properties(
    width=500,
    height=300
).project(
    type='albersUsa'
).repeat(
    row=variable_list
).resolve_scale(
    color='independent'
)

st.altair_chart(c)



mp = alt.Chart(states_mp).mark_geoshape(
   # fill='lightgray',
   # stroke='white'
).encode(
    tooltip='Value:Q',
    color='Value:Q',
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(dataset, 'id', list(dataset.columns))
).properties(
    width=500,
    height=300
).project(
    type='albersUsa'
)

st.altair_chart(mp)