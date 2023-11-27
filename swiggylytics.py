import streamlit as st 
import matplotlib.pyplot as plt
import altair as alt
import numpy as np
import pandas as pd
import calendar
from datetime import datetime
from io import StringIO
import requests 
import json
from streamlit_lottie import st_lottie
from rich import print

#---STYLES----
st.markdown("""
<style>
    .code-headers {
        font-size: 1rem;
        font-weight: 600;
    }
    .warning {
        font-size: 0l8rem;
        color: rgb(255, 165, 0);
        font-weight:600;
    }
</style>
""",unsafe_allow_html=True)

#----LOTTIE JSON----
#get lottie json file 
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    else:
        return r.json()
#display lottie json file 
lottie_swiggy = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_RpEYm8FTGt.json")

#-----LOAD AS JSON (using cache for lower latency)----
@st.cache_data
def load_order_history(data):
    order_history = json.loads(data)
    return order_history 

st.sidebar.title("🙌 Coming Soon!")
st.sidebar.write("Upload and visualize your own tasty data. Bon appétit! 🍽️")

#----DATA ANLYSIS FUNCTIONS----
#total orders 
def calc_total_orders(order_history):
    totalOrders = 0
    for my_dict in order_history:
        order_items = my_dict.get("order_items", [])  # Get the order_items array from the dictionary
        totalOrders += len(order_items)
    return totalOrders

#total amount spen
def calc_total_spent(order_history):
    totalAmt = 0.00
    for i in range(len(order_history)):
        totalAmt += float(order_history[i]["net_total"])
    return totalAmt

def calc_totalGST(order_history):
    totalGst = 0.00
    for i in range(len(order_history)):
        totalGst += float(order_history[i]["order_items"][0]["item_charges"]["GST"])
    return totalGst

def calc_totalDelivery(order_history):
    totalDelivery = 0.00
    for i in range(len(order_history)):
        totalDelivery += float(order_history[i]["charges"]["Delivery Charges"])
    return totalDelivery

def calc_totalPacking(order_history):
    totalPacking = 0.00
    for i in range(len(order_history)):
     totalPacking += float(order_history[i]["charges"]["Packing Charges"])
    return totalPacking

def extract_restaurant_names(order_history):
    restaurant_names = []
    for order in order_history:
        restaurant_name = order.get("restaurant_name")
        if restaurant_name:
            restaurant_names.append(restaurant_name)
    return restaurant_names

def extract_restaurant_order_count(order_history):
    names = extract_restaurant_names(order_history)
    restaurant_counts = {}
    for name in names:
        if name in restaurant_counts:
            restaurant_counts[name] += 1
        else:
            restaurant_counts[name] = 1
    return restaurant_counts

def dishes_order_count(order_history):
    items = []
    # traverse through all entries ie:total orders
    for i in range(len(order_history)):
    #for each order instance, extract the order name
        for j in range (len(order_history[i]['order_items'])):
            items.append((order_history[i]['order_items'][j]['name']))
    # Create a pandas Series from the list
    series = pd.Series(items)
    # Count the occurrences of each value in the Series
    value_counts = series.value_counts()
    # Sort the value_counts Series by values in descending order
    sorted_counts = value_counts.sort_values(ascending=False)
    return sorted_counts

# def food_type_count(order_history):
#     foodType = []
#     nonvegCount = 0
#     vegCount = 0
#     for my_dict in order_history:
#         order_items = my_dict.get("order_items", [])  # Get the order_items array from the dictionary
#         for item in order_items:
#             item_type = item.get("is_veg")
#             if item_type == "1":
#                 vegCount+=1
#             else:
#                 nonvegCount+=1
#     foodType.append(vegCount)
#     foodType.append(nonvegCount)
#     return foodType

def food_type_count(order_history):
    foodType = {}
    nonvegCount = 0
    vegCount = 0
    for my_dict in order_history:
        order_items = my_dict.get("order_items", [])  # Get the order_items array from the dictionary
        for item in order_items:
            item_type = item.get("is_veg")
            if item_type == "1":
                vegCount+=1
                foodType["veg"] = vegCount
            else:
                nonvegCount+=1
                foodType["nonVeg"] = nonvegCount 
    return foodType

def extract_cuisine_names(order_history):
    cuisine_names = []
    for i in range(len(order_history)):
        for j in range(len(order_history[i]["restaurant_cuisine"])):
            cuisine_names.append(order_history[i]["restaurant_cuisine"][j])
    return cuisine_names

# Compute occurrence of each cuisine name
def compute_cuisine_count(order_history):
    cuisine_count = {}
    cuisine_names = extract_cuisine_names(order_history)
    for cuisine in cuisine_names:
        if cuisine in cuisine_count:
            cuisine_count[cuisine] += 1
        else:
            cuisine_count[cuisine] = 1
    return cuisine_count

def extract_order_day_counts(data):
    order_day_count = {}

    for i in range(len(data)):
        datetime_obj = datetime.strptime(data[i]["order_time"], '%Y-%m-%d %H:%M:%S')
        day_of_week = calendar.day_name[datetime_obj.weekday()]

        if day_of_week in order_day_count:
            order_day_count[day_of_week] += 1
        else:
            order_day_count[day_of_week] = 1

    # Define the desired order of the days of the week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
   
    # Extract the days and order day_counts as separate dictionaries in the desired order
    day_counts = {day: order_day_count[day] for day in day_order if day in order_day_count}

    return day_counts

def extract_order_month_counts(data):
    order_month_count = {}

    for i in range(len(data)):
        datetime_obj = datetime.strptime(data[i]["order_time"], '%Y-%m-%d %H:%M:%S')
        month_of_year = calendar.month_name[datetime_obj.month]

        if month_of_year in order_month_count:
            order_month_count[month_of_year] += 1
        else:
            order_month_count[month_of_year] = 1

    # Define the desired order of months in a year
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Extract the months and order month_counts as separate dictionaries in the desired order
    month_counts = {month: order_month_count[month] for month in month_order if month in order_month_count}

    return month_counts
 
def extract_order_time(order_history):
    orderTime = []
    orderTimeFreq = {}
    for i in range(len(order_history)):
        datetime_str = order_history[i]["order_time"]
        datetime_obj = datetime.strptime(datetime_str,"%Y-%m-%d %H:%M:%S")
        time = datetime_obj.time()
        hour = time.hour
        orderTime.append(hour)  
    for time in orderTime:
        if(time in orderTimeFreq):
            orderTimeFreq[time] += 1
        else:
            orderTimeFreq[time] = 1
    return orderTimeFreq

st.title("Analyzing my Swiggy order history")
st.caption("👩‍💻 Abigail Anna Smith")
st.subheader("The motivation")

with st.container():
    left_column, right_column = st.columns(2)

    with left_column:
        st.write("""
        Being a college student, I always strive to be prudent with finances. 
        That being said, I often find myself splurging a little too much 
        than I should...especially on food🤤.
        
        I wanted to come up with some pocket friendly stratergies to curb my cravings, which led me to dive deeper into my Swiggy order data.
        """)
        
    with right_column:
        st_lottie(lottie_swiggy, height=200, key="swiggy")
st.write("---")

with st.container():
    file_path = "orders.json"  
    with open(file_path, "r") as file:
        data = file.read()
    order_history = load_order_history(data)

    st.subheader("🔍Let's gather some basic info")
    # st.markdown('<p class="code-headers">How many orders have I placed?</p>', unsafe_allow_html=True)
    totalOrders = calc_total_orders(order_history)
    totalAmt = calc_total_spent(order_history)
    # st.write("###")
    # st.markdown('<p class="code-headers">How much have I spent in total?</p>', unsafe_allow_html=True)
    
    # UNCOMMENT FOR TABLE VIEW
    fnCalls = [
        [totalOrders, totalAmt, round((totalAmt/12), 2)]
    ]
    # Convert the list to a NumPy array
    array = np.array(fnCalls)
    # Create a DataFrame with column names
    columns = ['Total Orders', 'Total amount spent(₹)', 'Avg amount spent per month(₹)']
    df = pd.DataFrame(data=array, columns=columns)
    df = df.style.set_properties(**{'color': 'rgb(9 171 59)', 'font-size':'0.5rem'})
    st.dataframe(df)
        
    st.write("###")
    st.subheader("🎨Data visualization")
    
    
    st.markdown('<p class="code-headers">1. Frequently Ordered Restaurants</p>', unsafe_allow_html=True)
    restaurantOrderCount = extract_restaurant_order_count(order_history)
    
    
    # Convert data to a Pandas DataFrame
    df = pd.DataFrame(restaurantOrderCount.items(), columns=['Restaurant Names', 'Frequency'])

    # Create the chart using Altair
    restaurantChart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.X("Restaurant Names"),
            alt.Y("Frequency"),
            alt.Color("Restaurant Names:N", scale=alt.Scale(scheme='viridis')),
            tooltip=["Restaurant Names", "Frequency"],
        )
        .properties(
            width=700, 
            height=400 
        )
        .interactive()
    )
    # Display the chart using Streamlit
    st.altair_chart(restaurantChart)
    st.write("###")
    st.markdown('<p class="code-headers">2. Frequently Ordered Dishes</p>', unsafe_allow_html=True)
    dishesCount = dishes_order_count(order_history)
    # Convert data to a Pandas DataFrame
    df = pd.DataFrame(dishesCount.items(), columns=['Dish Names', 'Frequency'])

    # Create the chart using Altair
    dishChart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.X("Dish Names"),
            alt.Y("Frequency"),
            alt.Color("Dish Names:N", scale=alt.Scale(scheme='magma')),
            tooltip=["Dish Names", "Frequency"],
        )
        .properties(
            width=700, 
            height=400 
        )
        .interactive()
    )
    st.altair_chart(dishChart)

    with st.container():
        # Define the width ratios for the columns
        left_column_width = 2
        right_column_width = 3

        # Create the columns
        left_column, right_column = st.columns([left_column_width, right_column_width])
        with left_column:
            st.write("###")
            st.markdown('<p class="code-headers">3. Food Type</p>', unsafe_allow_html=True)
            foodType = food_type_count(order_history)
            foodTypedf = pd.DataFrame(foodType.items(), columns=['Type', 'Count']) 

            foodTypePie = alt.Chart(foodTypedf).mark_arc(innerRadius=20).encode(
            theta="Count:Q",
            color="Type:N",
            ).properties(
                height=200,
                width=200
            )
            st.altair_chart(foodTypePie)
        with right_column:
            st.write("###")
            st.markdown('<p class="code-headers">4. Favourite Cuisines</p>', unsafe_allow_html=True)
            cuisineCount = compute_cuisine_count(order_history)
            cusineDf = pd.DataFrame(cuisineCount.items(), columns=['Cuisine Names', 'Frequency'])
            # st.write(cusineDf)

            cusinePie = alt.Chart(cusineDf).mark_arc(innerRadius=0).encode(
            theta="Frequency:Q",
            color="Cuisine Names:N",
            )
            st.altair_chart(cusinePie)
    st.markdown('<p class="code-headers">5. Orders Timeline</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Weekly Orders", "Monthly Orders", "Time of placing Orders(GMT"])
    with tab1:
        dayOrders = extract_order_day_counts(order_history)
        daydf = pd.DataFrame(list(dayOrders.items()), columns=['Day', 'Count'])
        # Convert 'Day' column to ordered categorical variable
        daydf['Day'] = pd.Categorical(daydf['Day'], categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], ordered=True)
    
        # Create Altair chart with 'Day' on the x-axis as Nominal data type
        chart = alt.Chart(daydf).mark_line().encode(
            x='Day:N',  # Specify the x-axis as Nominal
            y='Count'
        ).properties(
            width=600,  # Adjust the width as needed
            height=400  # Adjust the height as needed
        )
    
        # Display Altair chart using Streamlit
        st.altair_chart(chart, use_container_width=True)
    with tab2:
        monthOrders = extract_order_month_counts(order_history)
        monthdf = pd.DataFrame(list(monthOrders.items()), columns=['Month', 'Count'])
        monthdf['Month'] = pd.Categorical(monthdf['Month'], categories=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], ordered=True)

        st.line_chart(monthdf.set_index('Month'))
    with tab3:
        orderTime = extract_order_time(order_history)
        orderTimedf = pd.DataFrame(list(orderTime.items()),columns=['Time', 'Count'])
        st.write("Time of ordering ranges from: ",min(orderTime), "hours to",  max(orderTime),"hours")
        orderTimeLineChart = alt.Chart(orderTimedf).mark_bar().encode(
            x='Time:N',
            y='Count:Q',
            tooltip = ['Count']
        ).properties(
                height=400,
                width=700
            )
        st.altair_chart(orderTimeLineChart)
        

        # fig, ax = plt.subplots(figsize =(6, 3))
        # ax.hist(orderTime, bins = 10 ,color='steelblue', edgecolor='black')
        # # Show plot
        # st.pyplot(fig)
    st.write("###")
    st.markdown('<p class="code-headers">6. Cost Breakdown</p>', unsafe_allow_html=True)

    with st.container():
        left_column, right_column = st.columns(2)
    with left_column:
        tab1, tab2, tab3, tab4 = st.tabs(["Total charges", "GST", "Delivery", "Packing"])
        with tab1:
            totalSpent = calc_total_spent(order_history),
            totalGST = calc_totalGST(order_history),
            totalDelivery = calc_totalDelivery(order_history),
            totalParking = calc_totalPacking(order_history),

            st.write("₹%.2f" % totalSpent)
        with tab2:
            st.write("₹%.2f" % totalGST)
        with tab3:
            st.write("₹%.2f" % totalDelivery)
        with tab4:
            st.write("₹%.2f" % totalParking)

    with right_column:
        costData = pd.DataFrame({
            'Category':["Total charges", "GST Charges", "Delivery Charges", "Packing Charges"],
            'Value':[calc_total_spent(order_history), calc_totalGST(order_history), calc_totalDelivery(order_history), calc_totalPacking(order_history)]
        })
        # Create the pie chart
        alt.renderers.enable('mimetype')
        pie_chart = alt.Chart(costData).mark_arc().encode(
            color='Category:N',
            theta='Value:Q'
        ).properties(
            width=330,
            height=330
        )
        # Display the pie chart
        st.altair_chart(pie_chart)





    
