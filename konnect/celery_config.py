# celery_config.py

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_BEAT_SCHEDULE = {
    'check_and_alert_task_kwt': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1200,
        'args': ('kwtbucket',),
    },
    'check_and_alert_task_g44': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1210,
        'args': ('g44bucket',),
    },
    'check_and_alert_task_zmm': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1220,
        'args': ('zmmbucket',),
    },
    'check_and_alert_task_g45n': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1230,
        'args': ('G45N1Bucket',),
    },
    'check_and_alert_task_g45s': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1240,
        'args': ('G45SBucket',),
    },
    'check_and_alert_task_htr': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1250,
        'args': ('htrbucket',),
    },
    'check_and_alert_task_htr': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1260,
        'args': ('RMM',),
    },
    'check_and_alert_task_htr': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1270,
        'args': ('LsmBucket',),
    },
}
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

LARK_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/93f0c87b-bf6b-4c66-a377-26d1ce036800'

LARK_BUCKET_LABELS = {
    'kwtbucket': 'Offline Buildings in KWT',
    'g44bucket': 'Offline Buildings in G44',
    'zmmbucket': 'Offline Buildings in ZMM',
    'G45N1Bucket': 'Offline Buildings in G45N',
    'G45SBucket': 'Offline Buildings in G45S',
    'htrbucket': 'Offline Buildings in HTR',
    'RMM': 'Offline Buildings in ROY',
    'LsmBucket': 'Offline Buildings in LSM',
    # Add more mappings as needed
}
