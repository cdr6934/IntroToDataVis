import streamlit as st
import pandas as pd
import altair as alt

# Load data
@st.cache()
def load_state_data():
    return alt.topo_feature('https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/us-10m.json', 'states')


@st.cache()
def load_pop_data():
    pop = pd.read_csv('state_data.csv') # simply to get the ids in order to merge the data
    return pop[['state', 'id']]


@ st.cache()
def load_mental_health_data():
    return pd.read_csv(
        "Indicators_of_Anxiety_or_Depression_Based_on_Reported_Frequency_of_Symptoms_During_Last_7_Days.csv").query(
        'Group == "By State"')

@st.cache()
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

st.info("The graphs are interactive, so make sure to play!")

# Load data into page
pop_id = load_pop_data()
states_mp = load_state_data()
mental_health_data = load_mental_health_data()

# Unique lists
states = mental_health_data['State'].unique()
time_period = mental_health_data['Time Period Label'].unique()
indicator =  mental_health_data['Indicator'].unique()

# Data Manipulation
mental_health_data = mental_health_data.merge(pop_id, left_on='State', right_on='state')
mental_health_data = mental_health_data.drop(['state'], axis=1)
mental_health_data['Value'] = mental_health_data['Value'] / 100
mental_health_data['Low CI'] = mental_health_data['Low CI'] / 100
mental_health_data['High CI'] = mental_health_data['High CI'] / 100
value_label = "Prevalence"

with st.sidebar:
    time_select = st.selectbox("Time Period", time_period, index=len(time_period)-1)
    indicator_select = st.selectbox("People with", indicator)
    state_1 = st.selectbox("Current State", states, index=42)
    state_2 = st.selectbox("Compare State", states, index=15)


# For map
dataset = mental_health_data[(mental_health_data['Group'] == "By State") &
                             (mental_health_data['Time Period Label'] == time_select) &
                             (mental_health_data['Indicator'] == indicator_select)
                             ]




st.title('Comparing Symptoms of Anxiety and Depression in the US')

expander = st.expander("Instructions")
expander.write("""
    Use the left sidebar drop-down menus to explore the dataset. If not visible, there is an right facing error in the top left corner of the window. 
    By default the visualizations have been set 
    to the most recent date and two states that have some interesting patterns.
""")

st.markdown("The dataset comes from a bi-monthly survey called Indicators of "
            "Anxiety and Depression based on the Household Pulse Survey. "
            "It was designed to gauge the impact of the pandemic and conducted "
            " in conjunction with the [CDC](https://data.cdc.gov/NCHS/Indicators-of-"
            "Anxiety-or-Depression-Based-on-Repor/8pt5-q6wp) and [NCHS](https://data.cdc.gov/NCHS/Indicators-of-Anxiety-or-Depression-Based-on-Repor/8pt5-q6wp).")
st.markdown("This survey is used  to  identify symptoms of depression, symptoms of anxiety, or either. The past couple years "
            "have caused many unknowns ")
st.markdown("A few newsworthy events occured:")
st.markdown("* 02/03/2020 - US declares public health emergency\n"
            "* 05/25/2020 - Murder of George Floyd\n"
            "* 11/03/2020 - US Presidential Elections\n"
            "* 01/06/2021 -  Assault on the White House\n"
            "* 01/24/2022 - Russia invades Ukraine\n"
            )
st.markdown("Use the events as a way to understand some of the trends and the impact news events "
            "can have on the minds of Americans.")

st.subheader("Across the United States..")
mp = alt.Chart(states_mp).mark_geoshape(
   # fill='lightgray',
   # stroke='white'
).encode(
    alt.Color('Value:Q', title=value_label, legend=alt.Legend(format='.1%')),
    tooltip=['State:N',
             alt.Tooltip('Value:Q', format='.1%', title=value_label)]

).transform_lookup(
    lookup='id',
    from_=alt.LookupData(dataset, 'id', ['Value','State'])
).properties(
    width=800,
    height=400,
    title= "{0} ({1})".format(indicator_select, time_select)
).project(
    type='albersUsa'
).interactive()

st.altair_chart(mp)


# Data Aggregation
select_state1_data = mental_health_data[
    ((mental_health_data.State == state_1) | (mental_health_data.State == state_2)) & (
            mental_health_data.Indicator == indicator_select)]
select_state1_data = select_state1_data[["State", 'Time Period Label', "Time Period Start Date", "Value", "Low CI", "High CI"]]

min_value = min(dataset['Value'])
max_value = max(dataset['Value'])
max_row = dataset[dataset['Value'] == max_value]
data_start = "During **{0}** we see the survey estimates people with {1} range from {2:.2%} to {3:.2%}" \
             " or a difference of {4:.2%}".format(time_select,indicator_select.lower(), min_value, max_value, max_value-min_value)

st.markdown(data_start)
st.markdown("Above we are  given a point in time understanding of these symptoms throughout the US. "
            "However, you will find some variability between time periods, so what about two specific states? ")

# Following information
st.subheader("How does {0} and {1} compare?".format(state_1,state_2))
tab1, tab2 = st.tabs(["Chart", "Data"])
interest_col = indicator_select
with tab1:

    c = alt.Chart(select_state1_data).mark_line().encode(
        alt.X('Time Period Start Date:T', title=''),
        alt.Y('Value', title="% of Population",  axis=alt.Axis(format='%')),
        color='State'
    ) + alt.Chart(select_state1_data).mark_area(
        opacity=0.5
    ).encode(
        x='Time Period Start Date:T',
        y='Low CI',
        y2='High CI',
        color='State',
        tooltip=[alt.Tooltip('Time Period Label:N',title="Time Period"),
                 alt.Tooltip("Value:Q", format='.1%', title=value_label)]
    ).properties(
    width=800,
    height=400,
    title="{0} in {1} compared to {2}".format(interest_col, state_1, state_2)
) + alt.Chart(select_state1_data[select_state1_data['Time Period Label'] == time_select]
              ).mark_rule().encode(x='Time Period Start Date:T')

    st.altair_chart(c)
    st.caption("The transparent areas around the line are confidence intervals (CI)")
with tab2:
    st.subheader(interest_col)
    st.dataframe(data=select_state1_data)

    csv = convert_df(select_state1_data)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
    )

st.markdown("### Definitions")
st.markdown("* Prevalence - % of State Population that exhibit selected symptom(s)")
