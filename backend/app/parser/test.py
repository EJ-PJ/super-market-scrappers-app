import requests

url = "https://www.maxidespensa.com.gt/_v/segment/graphql/v1"

querystring = {
               "workspace": "master",
               "maxAge": "short",
               "appsEtag": "remove",
               "domain": "store",
               "locale": "es-GT",
               "__bindingId": "2eab5118-732b-4a29-a073-d03cd10aa581",
               "operationName": "productSearchV3",
               "variables": "{}",
               "extensions": "{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"a96c5ed03ef513568c34b63a4bf8da055ea6296293ee02eadb56e2e895eaffbc\",\"sender\":\"vtex.store-resources@0.x\",\"provider\":\"vtex.search-graphql@0.x\"},\"variables\":\"eyJza3VzRmlsdGVyIjoiQUxMIiwic2ltdWxhdGlvbkJlaGF2aW9yIjoiZGVmYXVsdCIsImluc3RhbGxtZW50Q3JpdGVyaWEiOiJNQVhfV0lUSE9VVF9JTlRFUkVTVCIsInByb2R1Y3RPcmlnaW5WdGV4IjpmYWxzZSwibWFwIjoiZnQiLCJxdWVyeSI6ImxlY2hlIiwib3JkZXJCeSI6Ik9yZGVyQnlTY29yZURFU0MiLCJmcm9tIjowLCJ0byI6MjAsInNlbGVjdGVkRmFjZXRzIjpbeyJrZXkiOiJmdCIsInZhbHVlIjoibGVjaGUifV0sImZ1bGxUZXh0IjoibGVjaGUiLCJmYWNldHNCZWhhdmlvciI6IlN0YXRpYyIsImNhdGVnb3J5VHJlZUJlaGF2aW9yIjoiZGVmYXVsdCIsIndpdGhGYWNldHMiOmZhbHNlLCJ2YXJpYW50IjoiNmFhMDUwOWYyYjBhNTc5ZjhiZWIwMmFjLXZhcmlhbnROdWxsIn0=\"}"
             }

payload = ""
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "content-type": "application/json",
    "Cookie": "_fbp=fb.2.1789756533164.597123932474423788.AQYCAQMC; vtex-search-anonymous=c3fe894f3cfd46fcbab40049012cd0ab; checkout.vtex.com=__ofid=734153c92c8d499694b574ec72f6e3fe; CheckoutOrderFormOwnership=Yk%2B%2B9nmcYtx3Y%2BWzzDD1EwZRmUdIC9%2BhXXy%2B0wlcscw2y2YcyrSzgIyhyXHj91H%2FYnmMQhHkK9fpqpru57HoJecyD5fXRJS8UVtEtCGBx%2Fi35H5eR2BpVmEPyoykZobX0VMIctvbj4uBKtheDUZZcw%3D%3D; vtex_binding_address=bodegagt.myvtex.com/; VtexWorkspace=master%3A-; vtex_session=eyJhbGciOiJFUzI1NiIsImtpZCI6IjYwNWUxZmZhLTY1OGMtNGIzZC1hMDFmLWJmOWQyZTExMGJjZiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiJhOGEzMmU0Mi0xOWI2LTQzYzItYjdkYi0yMmNjZGU2MTQ1MWIiLCJ2ZXJzaW9uIjo2LCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6ImJvZGVnYWd0IiwiZXhwIjoxNzkwNzk2MjUwLCJpYXQiOjE3OTAzNjQyNTAsImp0aSI6ImJmNjcyZGJhLTY2NTItNDE5YS1hYWJlLTM3ZTY4MzNlMzllMSIsImlzcyI6InNlc3Npb24vZGF0YS1zaWduZXIifQ.c1ST3EsrBi4Fy-CmEZnfQ-N6R1SAaN5pRrvTJYiEtUe0r92qyigFntCeTaP3J9UcpseHfUrmBAW_wff98Prpag; vtex_segment=eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIzIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjoiVTFjamQyRnNiV0Z5ZEdkMFltODBPVEk9IiwidXRtX2NhbXBhaWduIjpudWxsLCJ1dG1fc291cmNlIjpudWxsLCJ1dG1pX2NhbXBhaWduIjpudWxsLCJjdXJyZW5jeUNvZGUiOiJHVFEiLCJjdXJyZW5jeVN5bWJvbCI6IlEiLCJjb3VudHJ5Q29kZSI6IkdUTSIsImN1bHR1cmVJbmZvIjoiZXMtR1QiLCJjaGFubmVsUHJpdmFjeSI6InB1YmxpYyIsImZhY2V0cyI6ImFjY2Vzc2NvbnRyb2xsaXN0PXdhbG1hcnRndGJvNDkyOyJ9; vtex-search-session=65cec2f34cba424dbc40c63ce116f561; sp-variant=6aa0509f2b0a579f8beb02ac-variantNull; CheckoutLocale=es-GT; biggy-search-history=Leche%2CMonster",
    "Referer": "https://www.maxidespensa.com.gt/leche?_q=Leche&map=ft",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
}

response = requests.get(url, data=payload, headers=headers, params=querystring)

print(response.json())

res = eval(querystring["extensions"])
print("coded base64 json: \n", res["variables"])


import base64

coded_string = res["variables"]

print()
print("decoded base64 json: \n", base64.b64decode(coded_string))

import json

json_data = base64.b64decode(coded_string)

# Decode bytes to string and parse JSON
decoded_data = json_data.decode('utf-8')

parsed_json = json.loads(decoded_data)

# Print parsed JSON
print("json decoded: \n", parsed_json)
