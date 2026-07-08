import httpx

print('Testing API Endpoints...')

try:
    print('\n[1] POST /roadmap')
    res = httpx.post('http://127.0.0.1:8000/roadmap', json={
        'goal_title': 'Frontend Developer',
        'weekly_hours': 10,
        'known_skills': ['HTML', 'CSS']
    }, timeout=30.0)
    print(f'Status: {res.status_code}')
    data = res.json()
    roadmap_id = data.get('roadmap_id')
    print('Roadmap ID:', roadmap_id)
except Exception as e:
    print('Failed:', e)
    roadmap_id = None

if roadmap_id:
    try:
        print('\n[2] POST /project')
        res = httpx.post('http://127.0.0.1:8000/project', json={
            'roadmap_id': roadmap_id
        }, timeout=30.0)
        print(f'Status: {res.status_code}')
        print('Project Title:', res.json().get('project_title'))
    except Exception as e:
        print('Failed:', e)

if roadmap_id:
    try:
        print('\n[3] POST /chat')
        res = httpx.post('http://127.0.0.1:8000/chat', json={
            'roadmap_id': roadmap_id,
            'question': 'What should I learn next?'
        }, timeout=30.0)
        print(f'Status: {res.status_code}')
        print('Chat Response:', res.json().get('response'))
    except Exception as e:
        print('Failed:', e)
