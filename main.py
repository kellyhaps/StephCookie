import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#title
st.title("StephCookies Sales Dashboard :cookie:")
#st.subheader("Sales dashboard of Stephs Cookies :cookie:")

#Get data from shopify
@st.cache_data(ttl=3600)
def get_data():
	global total_list
	# Set URL
	domain = 'https://stephs-cookies.myshopify.com'
	endpoint = '/admin/api/2024-10/orders.json'
	# Query parameters
	query_params = {
		'status': 'any',
		'limit': 200
	}
	#api connections
	
	shop_creds= {
		"api_key" : st.secrets["API_KEY"],
		"api_secret" : st.secrets["API_SECRET"],
		"api_token" : st.secrets["API_TOKEN"]
	}
	# Build URL with query parameters
	base_url = f"{domain}{endpoint}"
	header_values = {'Content-Type': 'application/json', 'X-Shopify-Access-Token': shop_creds['api_token']}
	# Make GET request
	get_orders = requests.get(base_url, headers=header_values, params=query_params)
	# Convert response to JSON
	products = get_orders.json()
	#get list
	raw_datas = products["orders"]
	#temp writing to see what is happing
	#current_date = datetime.now()
	#st.write(f"Last update at; {current_date}")


	#empty list
	total_list = []

	# for loop to get the correct data
	for raw_data in raw_datas:
		cancelled = raw_data["cancelled_at"]
		order_id = raw_data["order_number"]
		date = raw_data["created_at"]
		date = datetime.fromisoformat(date)
		total_price = raw_data["current_total_price_set"]["shop_money"]["amount"]
		#total_price = total_price.replace(".", ",")
		#total_price = total_price.replace("'", "")
		total_price = float(total_price)
		#total_price = round(total_price)
		
		# Get products
		product_list = [product["name"] for product in raw_data["line_items"]]
		product_list_str = ", ".join(product_list)
		
		# Create dictionary
		order_temp = {
			"cancelled": cancelled,
			"order_id": order_id,
			"date": date,
			"total_price": total_price,
			"product_list": product_list_str
		}
		total_list.append(order_temp)
	return total_list
#get the total list
total_list = get_data()

#get date;
a, b = st.columns(2)
startdate = a.date_input("Startdate",value=datetime(2020, 12, 2))
startdate =(f"{startdate} 00:00:00+01:00")
startdate = datetime.fromisoformat(startdate)
enddate = b.date_input("Enddate")
enddate =(f"{enddate} 00:00:00+01:00")
enddate = datetime.fromisoformat(enddate)

#horizontal line
st.divider()

#calculate total sales - orders - average order
#set values
cal_total_sales = 0
cal_total_orders = 0
cal_last_30day_total_sale = 0
cal_last_30day_total_orders = 0
#get today
#timezone = ZoneInfo("UTC")
#current_date = datetime.now(tz=timezone)
new_date_30 = enddate + timedelta(days=-30)
new_date_30 = str(new_date_30)
new_date_30 = datetime.fromisoformat(new_date_30)

#updated total list
total_list_updated = []
#loop to total list
for x in total_list:
	#check for startdate
	if x["date"] >= startdate and x["date"]<=enddate:
		cal_total_orders += 1
		cal_total_sales += x["total_price"]
		# add to new list
		total_list_updated.append(x)
		#check for last 30 days
		if new_date_30 < x["date"]:
			cal_last_30day_total_orders += 1
			cal_last_30day_total_sale += x["total_price"]

#calulate average order
try:
	cal_average_order = cal_total_sales/cal_total_orders
	cal_last_30day_average = cal_last_30day_total_sale /cal_last_30day_total_orders 
except:
	cal_average_order = 0
	cal_last_30day_average = 0
#round up to two decimeter
cal_total_sales = round(cal_total_sales,2)
cal_average_order = round(cal_average_order,2)
cal_last_30day_total_sale = round(cal_last_30day_total_sale,2)
cal_last_30day_average = round(cal_last_30day_average,2)

# standard KPI
#create 2 columns
a, b, c = st.columns(3)
a.metric("Total sales", f"€{cal_total_sales}", f"€{cal_last_30day_total_sale} last 30 days")
b.metric("Total orders", cal_total_orders, f"{cal_last_30day_total_orders} orders last 30 days")
c.metric("Average order", f"€{cal_average_order}", f"€{cal_last_30day_average} last 30 days", delta_color="off")

#horizontal line
st.divider()

#bar chart
st.bar_chart(total_list_updated, x="date", y="total_price",stack=False, color = "#b02020", y_label="Total order price")

#horizontal line
st.divider()

#table view
st.table(total_list_updated)


# // Documentation; - icons -  https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
