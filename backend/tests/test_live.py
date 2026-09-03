import sys
import httpx

sys.stdout.reconfigure(encoding='utf-8')
client = httpx.Client(base_url='http://127.0.0.1:8000', timeout=10.0)

tests = [
    ('What is Equinox?', 'E-Summit'),
    ('When is Equinox?', '30–31 October'),
    ('What year is Equinox?', 'not stated'),
    ('Where is Equinox?', 'MLR Institute of Technology'),
    ('Tell me about IPL Auction', 'cricket auction'),
    ('which event is like monopoly?', 'Startup Poly'),
    ('who can i contact?', 'cie@mlrinstitutions.ac.in'),
    ('What is the registration fee for Equinox?', 'not available in the current Equinox information'),
]

print('=== LIVE HTTP EQUINOX TESTS ===')
for q, expected in tests:
    res = client.post('/api/chat', json={'bot_id':'ems', 'message': q}).json()
    ans = res.get('answer', '')
    print(f'Q: {q}')
    print(f'A: {ans[:90]}...')
    assert expected.lower() in ans.lower(), f'Failed on {q}: missing {expected}'

# Out of scope test
res_oos = client.post('/api/chat', json={'bot_id':'ems', 'message': "Who won yesterday's IPL match?"}).json()
print("\nQ: Who won yesterday's IPL match?")
print('Status:', res_oos.get('status'), 'Cooldown:', res_oos.get('cooldown_seconds'))
assert res_oos.get('status') == 'out_of_scope'

# Metrics check
metrics = client.get('/api/metrics').json()
print('\n=== GEMINI AVOIDANCE METRICS ===')
print('Total Queries:', metrics['total_queries'])
print('Gemini Queries:', metrics['gemini_queries'])
print('Gemini Avoided Queries:', metrics['gemini_avoided_queries'])
print('Gemini Avoidance Rate:', f"{metrics['gemini_avoidance_rate_pct']}%")

print('\nALL LIVE HTTP TESTS PASSED WITH 100% SUCCESS!')
