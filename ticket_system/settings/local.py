DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ticket_system',
        'USER': 'ticket_system_user',
        'PASSWORD': 'geheim',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'OPTIONS': {
        }
    }
}


EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
