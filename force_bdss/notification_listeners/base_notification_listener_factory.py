import logging
from traits.api import (
    HasStrictTraits, Instance, Str, provides, Type, Bool
)
from envisage.plugin import Plugin

from force_bdss.ids import factory_id
from force_bdss.notification_listeners.base_notification_listener import \
    BaseNotificationListener
from force_bdss.notification_listeners.base_notification_listener_model \
    import \
    BaseNotificationListenerModel
from .i_notification_listener_factory import INotificationListenerFactory

log = logging.getLogger(__name__)


@provides(INotificationListenerFactory)
class BaseNotificationListenerFactory(HasStrictTraits):
    """Base class for notification listeners.
    Notification listeners are extensions that receive event notifications
    from the MCO and perform an associated action.
    """
    #: identifier of the factory
    id = Str()

    #: Name of the factory. User friendly for UI
    name = Str()

    #: If the factor should be visible in the UI. Set to false to make it
    #: invisible. This is normally useful for notification systems that are
    #: not supposed to be configured by the user.
    ui_visible = Bool(True)

    #: The listener class that must be instantiated. Define this to your
    #: listener class.
    listener_class = Type(BaseNotificationListener, allow_none=False)

    #: The associated model to the listener. Define this to your
    #: listener model class.
    model_class = Type(BaseNotificationListenerModel, allow_none=False)

    #: A reference to the containing plugin
    plugin = Instance(Plugin)

    def __init__(self, plugin, *args, **kwargs):
        """Initializes the instance.

        Parameters
        ----------
        plugin: Plugin
            The plugin that holds this factory.
        """
        self.plugin = plugin
        super(BaseNotificationListenerFactory, self).__init__(*args, **kwargs)

        self.listener_class = self.get_listener_class()
        self.model_class = self.get_model_class()
        self.name = self.get_name()
        identifier = self.get_identifier()
        try:
            id = factory_id(self.plugin.id, identifier)
        except ValueError:
            raise ValueError(
                "Invalid identifier {} returned by "
                "{}.get_identifier()".format(
                    identifier,
                    self.__class__.__name__
                )
            )

        self.id = id

    def get_listener_class(self):
        raise NotImplementedError(
            "get_listener_class was not implemented in factory {}".format(
                self.__class__))

    def get_model_class(self):
        raise NotImplementedError(
            "get_model_class was not implemented in factory {}".format(
                self.__class__))

    def get_identifier(self):
        raise NotImplementedError(
            "get_identifier was not implemented in factory {}".format(
                self.__class__))

    def get_name(self):
        raise NotImplementedError(
            "get_name was not implemented in factory {}".format(
                self.__class__))

    def create_listener(self):
        """
        Creates an instance of the listener.
        """
        return self.listener_class(self)

    def create_model(self, model_data=None):
        """
        Creates an instance of the model.

        Parameters
        ----------
        model_data: dict
            Data to use to fill the model.
        """
        if model_data is None:
            model_data = {}

        return self.model_class(self, **model_data)
