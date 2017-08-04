from traits.api import Interface, String, Instance
from envisage.plugin import Plugin


class INotificationListenerBundle(Interface):
    """Envisage required interface for the BaseNotificationListenerBundle.
    You should not need to use this directly.

    Refer to the BaseNotificationListenerBundle for documentation.
    """
    id = String()

    name = String()

    plugin = Instance(Plugin)

    def create_object(self):
        """"""

    def create_model(self, model_data=None):
        """"""
