import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
#from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (DateRange,Dimension,Metric,RunReportRequest)
from google.analytics.data_v1beta import BetaAnalyticsDataClient, RunReportRequest, DateRange, Metric


#title
st.title("StephCookies Sales Dashboard :cookie:")
#st.subheader("Sales dashboard of Stephs Cookies :cookie:")

# --- Get data from shopify ------------------------------------------------
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
	#st.secrets["API_KEY"]
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

# --- Get data from google analytics --------------------------------------
#get creds
creds = {
  "type": "service_account",
  "project_id": "cookieapi-1735661883108",
  "private_key_id": "e62f67dfd75c1543f14b82c7dc43aaa598f292af",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQD1BT/kB3mCQcR+\nyzxRY5WsHiSpMqlRB9Q3Xdv8sFFCPqDzP+8myE1HJJfKBAC+J3shecvemigTUnuD\nt3kmZNPzD3hhFLRyQBH6/syWgIK4lIaxPekuZa7d4gKueV4NIzSWtfeh0OGauQ4Q\ndQvGUpbTtBIy5Nw2h5b/cHapQ1cW8z7y73K5CFLX+4r+kLqo8LpcacC+MjD1f9bd\nAKQ5xDBA/emN/ivyN6ANW5Wxq3OFGcXA66lt2U501JI2oEV8wLhbMStZ2uUuuQrM\nmbGxYaUa4sLnZysD6YzQugKGmV/DCR7lJvEHtyZMYFe/f1W/whXbT//Z8UzP12Sr\njObv/h9lAgMBAAECggEAEMoVDHBJrngIuaJ+Bdqzzxk6rGBlE0Ec1NVo5VoEm2w0\nta5gGhF4ICOdBhH7pgwJByx0IJMCI37PqWEpW0zl7B4Xgtl7GugSg1cx2C9CpdjB\nmQQTxiLgFmKuCdwVqoNKz3f1GcC5MNO058JJdgPDQ4rvg07E2zSzz1mau/L6FP+g\nMaroaZAXd5BtA87CgSg/4HMiSRP0etrbmKX5G46XMJRYCzQKJB/552o18kw8R7Oc\nbik8v4EEYqRd8nVJu2AZrGVJrSvzyU5+8shLgNSrheADMt9dMML+kfXN21j6iwN3\nWQaBx+kSpiA3x3eDeSt5UwGkgmPhzDVSUsJJvfkBeQKBgQD86PgSGpZWi/c+SZ1U\nmZrUaMF1BZuVH3S9XTxkwfKxfO+PkovXO+1jrKVif2F1EqGxOrcNbemHRX0OKurI\nUWu87C0CoEibRZ1isg2HdLG3JSc5arbtGzFPaKvMftXyq1PaUuyV91G5zedFRbHw\nFjrX+/vBkZlSlsiNgKPAki3RzQKBgQD4A5q1oYJUj9ww/ROIRK3BxSPM3tcFtQvM\n+3rlID7nfZSUWo51QM7b28RcEb4RbwpoQCn7oL/4dSVJ0vIs4ZNfXZMZAf2E/zIw\nIgBerOwblzbogiv0pis3aL8rFzxT97aAW1biUM6gB8s80h3WCgrlxUd5GMOYHDwP\nCxEGis5L+QKBgC33DXcE3AP4xkPMz0pb7HbkXxysmz08DVSJSHurgDdf1I5MfRvu\nKVPvQdOoAQdtDnQOjsxjCIlsSLE1fZxQp/sbFYcfqHKH8XXJlInk3JPDreBSk9J+\nGbUr+eVdu/axyrioT5Vl8LWLRZgidZeEAsfUZUol8y6+ds647YoHR0qVAoGAC7df\n36S5m3UQWeAaxB06eCTwBAWi8soSvKREsf5L+nOcSUXd5PwiyZAgPpk3+Wrdev9M\n/G4jo4ElOc+VUTl21NJ+2HeXmmjT3iI9EjvpC4ShO2qq2OvgrsVsAoUefHj/TiEC\ngb5/hF/Z4g2rCyl+Skx/i+D3nH/49lz3eO+lv0ECgYAOf9+VhiOJeUidYIlEE146\ntYzQrq8VjSYllM67j0zE7O5ESqPtD+wC50BH1ocPdZF7wr/459asH40maeGQiOsf\ni68Vyw8uYvPyQ55lZCEQQISToF0EB3hQWk8o2F9FRz9kqXr8no7UPsn38bR86hE8\nzXN6wjx+1tBf2SwC2hNn5w==\n-----END PRIVATE KEY-----\n",
  "client_email": "starting-account-ocw0gvoq7g2p@cookieapi-1735661883108.iam.gserviceaccount.com",
  "client_id": "103336209348539171987",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/starting-account-ocw0gvoq7g2p%40cookieapi-1735661883108.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

"""Runs a simple report on a Google Analytics 4 property."""
# TODO(developer): Uncomment this variable and replace with your
#  Google Analytics 4 property ID before running the sample.
property_id = "405961528"

# Using a default constructor instructs the client to use the credentials
# specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
#client = BetaAnalyticsDataClient()
client = BetaAnalyticsDataClient.from_service_account_info(creds)

# get last 30 days
today = datetime.now()
minus_30_days = today - timedelta(days=30)
minus_30_days = str(minus_30_days)
minus_30_days = minus_30_days[:10]

# === Bounce rate ====
#total bounce rate;
request = RunReportRequest(
	property=f"properties/{property_id}",
	metrics=[Metric(name="bounceRate")],
	date_ranges=[DateRange(start_date="2019-03-31", end_date="today")],
)
bounce_total = client.run_report(request)
bounce_total = bounce_total.rows[0].metric_values[0].value
bounce_total = float(bounce_total)
bounce_total = bounce_total * 100
bounce_total = round(bounce_total,1)
#print(f"Bounce rate; {bounce_total}%")

# last 30 days
request = RunReportRequest(
	property=f"properties/{property_id}",
	metrics=[Metric(name="bounceRate")],
	date_ranges=[DateRange(start_date=minus_30_days, end_date="today")],
)
bounce_30 = client.run_report(request)
bounce_30 = bounce_30.rows[0].metric_values[0].value
bounce_30 = float(bounce_30)
bounce_30 = bounce_30 * 100
bounce_30 = round(bounce_30,1)
#print(f"Bounce rate last 30 days; {bounce_30} %")

# === City visit + total visit ===
#total
request = RunReportRequest(
	property=f"properties/{property_id}",
	dimensions=[Dimension(name="city")],
	metrics=[Metric(name="activeUsers")],
	date_ranges=[DateRange(start_date="2019-03-31", end_date="today")],
)
city_total = client.run_report(request)

#put result in list
city_total_list = []
total_visiters = 0

for x in city_total.rows:
	city={
		"City":x.dimension_values[0].value,
		"Amount":x.metric_values[0].value
	}
	city_total_list.append(city)
	#update total amount
	total_visiters += int(x.metric_values[0].value)


#30 days
request = RunReportRequest(
	property=f"properties/{property_id}",
	dimensions=[Dimension(name="city")],
	metrics=[Metric(name="activeUsers")],
	date_ranges=[DateRange(start_date=minus_30_days, end_date="today")],
)
city_total = client.run_report(request)

#put result in list
city_30_list = []
day30_visiters = 0

for x in city_total.rows:
	city={
		"City":x.dimension_values[0].value,
		"Amount":x.metric_values[0].value
	}
	city_30_list.append(city)
	#update total amount
	day30_visiters += int(x.metric_values[0].value)

# === total bounce rate ===
request = RunReportRequest(
	property=f"properties/{property_id}",
	metrics=[Metric(name="averageSessionDuration")],
	date_ranges=[DateRange(start_date="2019-03-31", end_date="today")],
)
duration_total = client.run_report(request)
duration_total = duration_total.rows[0].metric_values[0].value
duration_total = float(duration_total)
duration_total = round(duration_total,1)
#print(f"Duration in sec; {duration_total}")

#30 days bounce rate;
request = RunReportRequest(
	property=f"properties/{property_id}",
	metrics=[Metric(name="averageSessionDuration")],
	date_ranges=[DateRange(start_date=minus_30_days, end_date="today")],
)
duration_30 = client.run_report(request)
duration_30 = duration_30.rows[0].metric_values[0].value
duration_30 = float(duration_30)
duration_30 = round(duration_30,1)
#print(f"Duration in sec last 30 days; {duration_30}")


# --- get date -------------------------------------------------------------
a, b = st.columns(2)
startdate = a.date_input("Startdate",value=datetime(2020, 12, 2))
startdate =(f"{startdate} 00:00:00+01:00")
startdate = datetime.fromisoformat(startdate)
enddate = b.date_input("Enddate")
enddate =(f"{enddate} 00:00:00+01:00")
enddate = datetime.fromisoformat(enddate)

#horizontal line
st.divider()

# --- calculate total sales - orders - average order ----------------------
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

# -- updated total list ---------------------------------------------------
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
	cal_last_30day_average = cal_last_30day_total_sale /cal_last_30day_total_orders 
except:	
	cal_last_30day_average = 0

try:
	cal_average_order = cal_total_sales/cal_total_orders
except:
	cal_average_order = 0


#round up to two decimeter
cal_total_sales = round(cal_total_sales,2)
cal_average_order = round(cal_average_order,2)
cal_last_30day_total_sale = round(cal_last_30day_total_sale,2)
cal_last_30day_average = round(cal_last_30day_average,2)

# --- standard KPI ----------------------------------------------------------------------------------------
# --- google analytics ---
a,b,c = st.columns(3)
a.metric("Total visiters",f"{total_visiters}",f"{day30_visiters} last 30 days")
b.metric("Bounce rate", f"{bounce_total}%", f"{bounce_30}% last 30 days",delta_color="off")
c.metric("Session time", f"{duration_total} sec", f"{duration_30} sec last 30 days",delta_color="off")
# --- Total sales ----
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
