import requests
import json

# The invoke URL for your deployed API Gateway stage
api_gateway_url = 'https://ufq4o43b7i.execute-api.ap-south-1.amazonaws.com/default/mia-query'

# Data to send with POST request, as a dictionary
data_to_send = {"query_text":"","query_filter":{"hours":{"$eq":22},"day":{"$eq":31},"month":{"$eq":12},"year":{"$eq":2023}},"query_top_k":3,"show_log":True}

# Make the POST request with JSON data
response = requests.post(api_gateway_url, json=data_to_send)

# To check if the request was successful
if response.status_code == 200:
    print('Success!')
    # You can convert the response to JSON if the endpoint returns JSON
    data = response.json()
    print(data)
else:
    print('Failed to retrieve data:', response.status_code)
