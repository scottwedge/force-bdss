from traits.api import HasStrictTraits, List, Instance, Float, Unicode

from force_bdss.core.data_value import DataValue
from force_bdss.io.workflow_writer import pop_dunder_recursive


def nested_getstate(state_dict):
    # We safely attempt to __getstate__ of the nested objects in `state_dict`
    # on the zero and first levels.
    # If the `state_dict` item is an iterable, we __getstate__ of the iterable
    # elements. Otherwise, we __getstate__ the item itself.
    # If we can't __getstate__ of the item, we leave it as it is.
    for key in state_dict:
        try:
            if isinstance(state_dict[key], (tuple, list)):
                state_dict[key] = [el.__getstate__() for el in state_dict[key]]
            else:
                state_dict[key] = state_dict[key].__getstate__()
        except AttributeError:
            pass
    return state_dict


class BaseDriverEvent(HasStrictTraits):
    """ Base event for the MCO driver."""

    def __getstate__(self):
        """ Returns state dictionary of the object. For a nested dict,
        __getstate__ is applied to zero level items and first level items.
        """
        state = pop_dunder_recursive(super().__getstate__())
        state = nested_getstate(state)
        return state


class MCOStartEvent(BaseDriverEvent):
    """ The MCO driver should emit this event when the evaluation starts."""

    #: The names assigned to the parameters.
    parameter_names = List(Unicode())

    #: The names associated to the KPIs
    kpi_names = List(Unicode())

    def serialize(self):
        """ Provides serialized form of MCOStartEvent for further data storage
        (e.g. in csv format) or processing.


        Usage example:
        For a custom MCOStartEvent subclass, this method can be overloaded.
        An example of a custom `serialize` method would be:
        >>> class CustomMCOStartEvent(MCOStartEvent):
        >>>     weights = List(Float())
        >>>     def serialize(self):
        >>>         custom_data = [f"{name}_weight" for name in self.kpi_names]
        >>>         return super().serialize() + custom_data
        >>>

        Returns:
            List(Unicode): event parameters names and kpi names
        """
        return self.parameter_names + self.kpi_names


class MCOFinishEvent(BaseDriverEvent):
    """ The MCO driver should emit this event when the evaluation ends."""


class MCOProgressEvent(BaseDriverEvent):
    """ The MCO driver should emit this event for every new point that is
    evaluated during the MCO run.
    """

    #: The point in parameter space resulting from the pareto
    #: front optimization
    optimal_point = List(Instance(DataValue))

    #: The associated KPIs to the above point
    optimal_kpis = List(Instance(DataValue))

    #: The weights assigned to the KPIs
    weights = List(Float())

    def serialize(self):
        """ Provides serialized form of MCOProgressEvent for further data storage
        (e.g. in csv format) or processing.

        Note: this code duplicates the MCOProgressEvent handler in
        `force_wfmanager.wfmanager_setup_task._server_event_mainthread`
        Can we refactor this?

        Warning: `weights` attribute is NOT serialized here. We expect it to be
        refactored to custom MCOProgressEvent class.

        Usage example:
        For a custom MCOProgressEvent subclass, this method can be overloaded.
        An example of a custom `serialize` method would be:
        >>> class CustomMCOProgressEvent(MCOProgressEvent):
        >>>     weights = List(Float())
        >>>     def serialize(self):
        >>>         return super().serialize() + self.weights
        >>>

        Returns:
            List(Datavalue.value): values of the event optimal points and kpis
        """
        event_datavalues = self.optimal_point + self.optimal_kpis
        return [entry.value for entry in event_datavalues]
