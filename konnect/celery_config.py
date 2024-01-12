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
        'schedule':1250,
        'args': ('htrbucket',),
    },
    'check_and_alert_task_rmm': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1260,
        'args': ('RMM',),
    },
    'check_and_alert_task_lsm': {
        'task': 'konnect_admin.tasks.lark_post',
        'schedule': 1270,
        'args': ('LsmBucket',),
    },


    ####PoP Power Monitoring Tasks



    'check_and_alert_task_lsmp': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 35, 
        'args': ('LsmBucket',),
    },
    'check_and_alert_task_zmmp': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 40,
        'args': ('zmmbucket',),
    },
    'check_and_alert_task_g44p': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 45,
        'args': ('g44bucket',),
    },
    'check_and_alert_task_g45sp': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 50,
        'args': ('G45SBucket',),
    },
    'check_and_alert_task_stn': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 55,
        'args': ('STNOnu',),
    },
    'check_and_alert_task_kwd': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 60,
        'args': ('KWDOnu',),
    },
    'check_and_alert_task_mwkn': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 65,
        'args': ('MWKn',),
    },
    'check_and_alert_task_ksn': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 70,
        'args': ('KSNOnu',),
    },
    'check_and_alert_task_kwtp': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 75,
        'args': ('kwtbucket',),
    },
    'check_and_alert_task_g45np': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 80,
        'args': ('G45N1Bucket',),
    },
    'check_and_alert_task_mwksp': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 85,
        'args': ('MWKs',),
    },
    'check_and_alert_task_rmmp': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 87,
        'args': ('RMM',),
    },
    'check_and_alert_task_krbs': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 87,
        'args': ('KRBSOnu',),
    },
    'check_and_alert_task_htrss': {
        'task': 'konnect_admin.tasks.lark_post_pop',
        'schedule': 87,
        'args': ('HTROnu',),
    },
}
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

LARK_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/93f0c87b-bf6b-4c66-a377-26d1ce036800'

POP_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/93f0c87b-bf6b-4c66-a377-26d1ce036800'

#POP_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/c6ee370c-2257-4960-b076-4543c7e454e4'

GPON_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/93f0c87b-bf6b-4c66-a377-26d1ce036800'


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
POP_BUCKET_LABELS = {
    'g44bucket': 'Power Outage in G44 PoP',
    'zmmbucket': 'Power Outage in ZMM PoP',
    'LsmBucket': 'Power Outage in LSM PoP',
    'G45SBucket': 'Power Outage in G45S PoP',
    'STNOnu': 'Power Outage in STN PoP',
    'KWDOnu': 'Power Outage in KWD PoP',
    'MWKn': 'Power Outage in MWKn PoP',
    'KSNOnu': 'Power Outage in KSN PoP',
    'kwtbucket': 'Power Outage in KWT PoP',
    'G45N1Bucket': 'Power Outage in G45N PoP',
    'MWKs': 'Power Outage in MWKs PoP',
    'RMM': 'Power Outage in ROY PoP',
    'KRBSOnu': 'Power Outage in KRBS PoP',
    'HTROnu': 'Power Outage in HTR PoP',
    # Add more mappings as needed for other PoP buckets
}
GPON_BUCKET_LABELS = {
    'stn': 'High Offline ONU Count in STN',
    'kwd': 'High Offline ONU Count in KWD',
    'mwkn': 'High Offline ONU Count in MWKn',
    'ksn': 'High Offline ONU Count in KSN',
    'mwks': 'High Offline ONU Count in MWKs',
}