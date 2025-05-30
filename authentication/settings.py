MIDDLEWARE = [
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = [
    "authentication",
    "authentication.templatetags.custom_filters"
]
