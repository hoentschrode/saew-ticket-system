from django.apps import AppConfig


class BookingConfig(AppConfig):
    name = 'booking'

    # Feature switch: QR codes
    use_qr_codes = True
