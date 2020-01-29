import importlib

from traits.api import HasStrictTraits, List, Instance, Float, Unicode

from force_bdss.core.data_value import DataValue
from force_bdss.core.base_model import pop_dunder_recursive, nested_getstate


class DriverEventTypeError(TypeError):
    """Raised when a BaseDriverEvent is attempted to be instantiated with a
     class that is not a subclass of BaseDriverEvent."""


class BaseDriverEvent(HasStrictTraits):
    """ Base event for the MCO driver."""

    def __getstate__(self):
        """ Returns state dictionary of the object. For a nested dict,
        __getstate__ is applied to zero level items and first level items.
        """
        state = pop_dunder_recursive(super().__getstate__())
        state = nested_getstate(state)
        id = ".".join((self.__class__.__module__, self.__class__.__name__))
        state = {"model_data": state, "id": id}
        return state

    @staticmethod
    def get_event_class(id_string):
        class_module, class_name = id_string.rsplit(".", 1)
        module = importlib.import_module(class_module)
        try:
            cls = getattr(module, class_name)
        except AttributeError:
            error_message = (
                f"Unable to locate the class definition {class_name} "
                f"in module {module} requested by the event with "
                f"id {id_string}"
            )
            raise ImportError(error_message)
        if not issubclass(cls, BaseDriverEvent):
            raise DriverEventTypeError(
                f"Class {cls} must be a subclass of BaseDriverEvent"
            )
        return cls

    @classmethod
    def from_json(cls, data):
        klass = cls.get_event_class(data["id"])
        return klass(**data["model_data"])


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
        >>>
        >>>     def serialize(self):
        >>>         custom_data = [f"{name} data" for name in self.kpi_names]
        >>>         return super().serialize() + custom_data
        >>>

        Returns:
            List(Unicode): event parameters names and kpi names
        """
        return self.parameter_names + self.kpi_names


class WeightedMCOStartEvent(MCOStartEvent):
    """Initializes reporting of weights generated during an MCO by a
    WeightedOptimizerEngine"""

    def serialize(self):
        """Overloaded method to provide weights alongside each
        reported KPI"""
        value_names = self.parameter_names
        for kpi_name in self.kpi_names:
            value_names.extend([kpi_name, kpi_name + " weight"])
        return value_names


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

    def serialize(self):
        """ Provides serialized form of MCOProgressEvent for further data storage
        (e.g. in csv format) or processing.

        Usage example:
        For a custom MCOProgressEvent subclass, this method can be overloaded.
        An example of a custom `serialize` method would be:
        >>> class CustomMCOProgressEvent(MCOProgressEvent):
        >>>     metadata = List(Float)
        >>>     def serialize(self):
        >>>         return super().serialize() + self.metadata
        >>>

        Returns:
            List(Datavalue.value): values of the event optimal points and kpis
        """
        event_datavalues = self.optimal_point + self.optimal_kpis
        return [entry.value for entry in event_datavalues]


class WeightedMCOProgressEvent(MCOProgressEvent):
    """Allows reporting of weights generated during an MCO by a
    WeightedOptimizerEngine"""

    #: Weights assigned to each KPI during the MCO optimization
    weights = List(Float())

    def _weights_default(self):
        """Default weights are normalised and uniform for each KPI"""
        if self.optimal_kpis:
            return [1 / len(self.optimal_kpis)] * len(self.optimal_kpis)
        return []

    def serialize(self):
        """Overloaded method to provide weights alongside each
        reported KPI"""
        event_datavalues = [entry.value for entry in self.optimal_point]
        for kpi, weight in zip(self.optimal_kpis, self.weights):
            event_datavalues.extend([kpi.value, weight])
        return event_datavalues
