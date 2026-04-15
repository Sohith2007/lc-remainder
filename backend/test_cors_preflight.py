import requests

# Send OPTIONS preflight request (what browsers send for CORS)
r = requests.options('http://127.0.0.1:8000/api/recipients', headers={
    'Origin': 'http://localhost:5173',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'content-type'
})

print('OPTIONS Preflight Response:')
print(f'Status Code: {r.status_code}')
print('\nCORS Headers:')
cors_headers = {k: v for k, v in r.headers.items() if 'access-control' in k.lower()}
if cors_headers:
    for k, v in cors_headers.items():
        print(f'{k}: {v}')
else:
    print('No CORS headers found')
    print('\nAll Response Headers:')
    for k, v in r.headers.items():
        print(f'{k}: {v}')
