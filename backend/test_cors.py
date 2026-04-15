import requests

r = requests.get('http://127.0.0.1:8000/api/home')
print('CORS Headers:')
cors_headers = [f'{k}: {v}' for k, v in r.headers.items() if 'access-control' in k.lower()]
if cors_headers:
    for h in cors_headers:
        print(h)
else:
    print('No CORS headers found')
    print(f'Status Code: {r.status_code}')
