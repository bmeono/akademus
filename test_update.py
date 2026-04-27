import requests

r = requests.post('http://localhost:8001/auth/login', json={'email':'admin@akademus.com','password':'admin123'})
token = r.json()['access_token']

print('Test 1 - JSON body:')
resp = requests.put('http://localhost:8001/admin/opciones/101',
    headers={'Authorization': f'Bearer {token}'},
    json={'texto': 'nuevo texto'}
)
print(f'  Status: {resp.status_code}, Body: {resp.text}')

print('Test 2 - Form data:')
resp = requests.put('http://localhost:8001/admin/opciones/102',
    headers={'Authorization': f'Bearer {token}'},
    data={'es_correcta': 'true'}
)
print(f'  Status: {resp.status_code}, Body: {resp.text}')