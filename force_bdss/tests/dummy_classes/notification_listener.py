from force_bdss.notification_listeners.base_notification_listener import \
    BaseNotificationListener
from force_bdss.notification_listeners.base_notification_listener_factory \
    import \
    BaseNotificationListenerFactory
from force_bdss.notification_listeners.base_notification_listener_model \
    import \
    BaseNotificationListenerModel


class DummyNotificationListener(BaseNotificationListener):
    def deliver(self, event):
        pass


class DummyNotificationListenerModel(BaseNotificationListenerModel):
    pass


class DummyNotificationListenerFactory(BaseNotificationListenerFactory):
    def get_name(self):
        return "bar"

    def get_identifier(self):
        return "foo"

    def get_listener_class(self):
        return DummyNotificationListener

    def get_model_class(self):
        return DummyNotificationListenerModel


