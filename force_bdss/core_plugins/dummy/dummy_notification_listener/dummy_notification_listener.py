from force_bdss.api import BaseNotificationListener


class DummyNotificationListener(BaseNotificationListener):
    def deliver(self, model, message):
        print(message)

    def init_persistent_state(self, model):
        print("Initializing persistent state")
