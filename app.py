import os
import requests

# Set your Bearer Token here
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAALDZuwEAAAAAgAVUAZwzMxjlfBlyJcA6EOoYpHY%3DknXx3QSamfMHoVcOs8wfE9fPchcObnLxkyFeo5UlRZ6IiLnU24'

# Define the endpoint URL
url = 'https://api.twitter.com/2/tweets/search/recent'

# Set up the query parameters
params = {
    'query': 'from:twitterdev',
    'max_results': 10  # Adjust as needed
}

# Set up the headers including the Authorization header
headers = {
    'Authorization': f'Bearer {AAAAAAAAAAAAAAAAAAAAALDZuwEAAAAAgAVUAZwzMxjlfBlyJcA6EOoYpHY%3DknXx3QSamfMHoVcOs8wfE9fPchcObnLxkyFeo5UlRZ6IiLnU24}',
}

# Make the GET request
response = requests.get(url, headers=headers, params=params)

# Check if the request was successful
if response.status_code == 200:
    print('Request successful!')
    tweets = response.json()
    print(tweets)
else:
    print(f'Error: {response.status_code}')
    print(response.json())
