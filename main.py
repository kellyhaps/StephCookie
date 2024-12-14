import requests
import json

# Get creds
shop_creds = 'creds.json'
with open(shop_creds) as f:
	shop_creds = json.load(f)

# Set URL
domain = 'https://stephs-cookies.myshopify.com'
endpoint = '/admin/api/2024-10/orders.json'

# Query parameters
query_params = {
	'status': 'any',
	'limit': 200
}

# Build URL with query parameters
base_url = f"{domain}{endpoint}"
header_values = {'Content-Type': 'application/json', 'X-Shopify-Access-Token': shop_creds['api_token']}

# Make GET request
get_orders = requests.get(base_url, headers=header_values, params=query_params)

# Convert response to JSON
products = get_orders.json()

# Total list
order_list = []

# Get orders data
if 'orders' in products:
	raw_datas = products["orders"]
	print(len(raw_datas))
	for raw_data in raw_datas:
		cancelled = raw_data["cancelled_at"]
		checkout_id = raw_data["checkout_id"]
		date = raw_data["created_at"]
		total_price = raw_data["current_total_price_set"]["shop_money"]["amount"]
		total_price = total_price.replace(".", ",")
		
		# Get products
		product_list = [product["name"] for product in raw_data["line_items"]]
		product_list_str = ", ".join(product_list)
		
		# Create dictionary
		order_temp = {
			"cancelled": cancelled,
			"checkout_id": checkout_id,
			"date": date,
			"total_price": total_price,
			"product_list": product_list_str
		}
		order_list.append(order_temp)
else:
	print("No orders found or API response error")

# Save total list
#with open('StephsOrders.json', 'w') as f:
#    json.dump(order_list, f)
