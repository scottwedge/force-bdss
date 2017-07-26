from traits.api import HasStrictTraits, String, Instance

from force_bdss.mco.parameters.base_mco_parameter_factory import \
    BaseMCOParameterFactory


class BaseMCOParameter(HasStrictTraits):
    """The base class of all MCO Parameter models.
    Must be reimplemented by specific classes handling the specific parameter
    that MCOs understand.
    """

    #: The generating factory. Used to retrieve the ID at serialization.
    factory = Instance(BaseMCOParameterFactory, visible=False, transient=True)

    #: A user defined name for the parameter
    value_name = String()

    #: A CUBA key describing the type of the parameter
    value_type = String()

    def __init__(self, factory, *args, **kwargs):
        self.factory = factory
        super(BaseMCOParameter, self).__init__(*args, **kwargs)