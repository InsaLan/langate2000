from django.apps import AppConfig

"""
class PortalConfig(AppConfig):
    name = 'portal'

    def ready(self):
        # Reconnecting devices registered in the Device set but not in the Ipset
        # This is important when for example the Ipset is flushed, you want the users that are already
        # registered on the gate to be automatically reconnected when the gate restarts.

        # This is important to maintain the consistency between the device state from django's point of view and
        # and the device state from the Ipset's point of view.

        from portal.models import Device
        from django.conf import settings

        all_registered_devices = Device.objects.all()
        all_connected_devices = settings.NETWORK.get_all_connected().keys()

        for dev in all_registered_devices:
            if dev.mac not in all_connected_devices:
                settings.NETWORK.connect_user(dev.mac)
"""
