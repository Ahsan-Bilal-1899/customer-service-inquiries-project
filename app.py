import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title = "Customer Service Dashboard", layout= "wide")
@st.cache_resource
@st.cache_data

def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


def load_data():
    cleaned_df = pd.read_csv('Data Cleaning/clean_call_center_data.csv')
    return cleaned_df

cleaned_df = load_data()

def get_unique_values(colname):
    return cleaned_df[colname].unique().tolist()


def apply_filters(colname, selection):
    return cleaned_df[cleaned_df[colname].isin(selection)]

def apply_search(colname, selection):
    return search_df[search_df[colname] == selection]


def display_dataframe(colnames):
    return search_df[colnames].reset_index(drop = True)


unique_channels = get_unique_values("channel")
unique_responses = get_unique_values("response_time")
unique_centre_states = get_unique_values("center_state")


### SIDEBAR ###
filters_side_bar = st.sidebar
filters_side_bar.title("⌛Dropdown Filters")

channel_selection = filters_side_bar.multiselect("Select a Channel", options= unique_channels, default= unique_channels)
response_selection = filters_side_bar.multiselect("Select a Response", options= unique_responses, default= unique_responses)
center_state_selection = filters_side_bar.multiselect("Select a Center Location", options= unique_centre_states, default= unique_centre_states)

final_df = cleaned_df.copy()

if channel_selection:
    final_df = apply_filters("channel", channel_selection)

if response_selection:
    final_df = apply_filters("response_time", response_selection)
        
if center_state_selection:
    final_df = apply_filters("center_state", center_state_selection)

if final_df.empty:
    st.warning("No data matches the selected filters.")

search_df = final_df.copy()


# tab1, tab2 = st.tabs(["Summary VIEW", "Detailed VIEW"])

# with tab1:

### COMPUTE METRICS ###
total_calls = "{:,}".format((len(final_df)))
average_call_duration = round(final_df['call_duration_mins'].mean(),2)
average_csat_score = round(final_df['csat_score'].mean(),2)
most_frequent_sentiment = final_df['sentiment'].mode()[0]


st.markdown('<h1 class="main-title">📊 Customer Inquiries Dashboard </h1>', unsafe_allow_html=True)

st.markdown('<h2 class="section-header">KPI Breakdown</h2>', unsafe_allow_html=True)

# st.markdown("Hover over the icon for more info", help="This is the tooltip text!")


c1, c2, c3, c4 = st.columns(4)


    
c1.metric("Total Service Inquiries", total_calls)
c2.metric("Average Contact Duration", str(average_call_duration) + " minutes")
c3.metric("Average Satisfaction Score", average_csat_score)
c4.metric("Most Frequent Sentiment", most_frequent_sentiment)
    



st.divider()

mc = st.container()

with mc:

    chart1, chart2, = st.columns(2)
    
    OKABE_ITO = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # green
    "#F0E442",  # yellow
    "#D55E00",  # vermillion
    "#CC79A7",  # purple
    "#000000"
]
    
    with chart1:
        st.markdown('<h2 class="section-header">Inquiry Frequency by Sentiment and Reason</h2>', unsafe_allow_html=True)
        grouped_data = final_df.groupby(['sentiment', 'reason']).size().reset_index()
        grouped_data.columns = ['Sentiment', 'Reason of Contact', 'Inquiry Frequency']
        
        fig2 = px.bar(
            grouped_data,
            x='Sentiment',
            y='Inquiry Frequency',
            color='Reason of Contact',
            barmode='stack', 
            text='Inquiry Frequency',
            color_discrete_sequence=OKABE_ITO
        )

        fig2.update_traces(textfont_size=16) 
        fig2.update_layout(legend_font_size=16)
        fig2.update_xaxes(tickfont=dict(size=16))
        fig2.update_yaxes(tickfont=dict(size=16))


        st.plotly_chart(fig2)
        
    with chart2:
        st.markdown('<h2 class="section-header">State Level Breakdown of Customer Inquiries</h2>', unsafe_allow_html=True)
        state_grouping = final_df.groupby('customer_state_abbrev', as_index= False).agg(\
                                    avg_csat=('csat_score', 'mean'),
                                    count = ('customer_state_abbrev', 'size')).round(2)
        
        state_grouping.columns = ['US State', 'Average Satisfaction Score', 'Inquiry Frequency']

        fig3 = px.choropleth(
                        state_grouping,
                        locations="US State",
                        locationmode="USA-states",
                        color="Inquiry Frequency",
                        color_continuous_scale="viridis",
                        scope="usa",
                        hover_data= "Average Satisfaction Score"
                        # labels={"count": "Inquiry Count"}
                    )


        fig3.update_layout(legend_font_size=16)
        fig3.update_geos(bgcolor='rgba(0,0,0,0)')


        st.plotly_chart(fig3, use_container_width=True)
        
st.divider()
            
st.markdown('<h2 class="section-header">Detailed Customer Breakdown </h1>', 
            # help="Please clear the sidebar filters to focus on an individual customer's information.",
            unsafe_allow_html=True)
# st.warning("Please clear the sidebar filters to focus on an individual customer's information.", icon="⚠️")

sc1, sc2 = st.columns(2)

# search_df = final_df.copy()

unique_names = get_unique_values("customer_name")
unique_ids = get_unique_values("id")

try:

    with sc1:
        
        name_selection = sc1.selectbox("Enter Customer Name", options = unique_names)

    # if id_selection:
    #     search_df = apply_search("id", id_selection)

    if name_selection:
        search_df = apply_search("customer_name", name_selection)


    displayed_df = display_dataframe(["id", "customer_name", "customer_city", "customer_state"])
    #   
    with sc2:
        st.dataframe(displayed_df, hide_index=True)

    st.container()

    ### COMPUTE CUSTOMER SPECIFIC METRICS ###
    customer_score = search_df.iloc[0]['csat_score']
    customer_sentiment = search_df.iloc[0]['sentiment']
    customer_channel = search_df.iloc[0]['channel']
    customer_issue = search_df.iloc[0]['reason']

    cc1, cc2, cc3, cc4 = st.columns(4)

    cc1.metric("Selected Customer's Satisfaction Score", customer_score)
    cc2.metric("Selected Customer's Sentiment", customer_sentiment)
    cc3.metric("Selected Customer's Contact Channel", customer_channel)
    cc4.metric("Selected Customer's Issue", customer_issue)
    
except Exception:
    st.error("Please clear all the sidebar filters to view specific customer's information.", icon="⚠️")

st.divider()







#     st.subheader("Line Chart")
#     st.line_chart(data['Line Data'])

# with col2:
#     st.subheader("Bar Chart")
#     st.bar_chart(data['Bar Data'])

    