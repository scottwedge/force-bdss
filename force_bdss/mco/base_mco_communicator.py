import abc

from traits.api import ABCHasStrictTraits, Instance

from .i_mco_bundle import IMCOBundle


class BaseMCOCommunicator(ABCHasStrictTraits):
    """Communicator class that defines how the MCO communicates
    with the evaluator program that does the actual heavylifting of the
    calculation.

    The model assumes that the MCO spawns a process to perform the evaluation,
    and passes data to this process that define the parameters for the
    evaluation. Once completed, the evaluation will return a set of results,
    that we interpret as KPIs. These KPIs are encoded in some form, which is
    again specified by the MCO.
    """
    #: A reference to the bundle
    bundle = Instance(IMCOBundle)

    def __init__(self, bundle):
        self.bundle = bundle

    @abc.abstractmethod
    def receive_from_mco(self, model):
        """
        Receives the parameters from the MCO.
        The conversion is specific to the format of the communication
        between the MCO and its evaluator program.

        Must return a single DataSourceParameters object, containing
        the parameters as passed by the MCO.

        Parameters
        ----------
        model: BaseMCOModel
            The model of the optimizer, instantiated through create_model()

        Returns
        -------
        DataSourceParameters
            An instance of the DataSourceParameters with the appropriate
            information filled in.
        """

    @abc.abstractmethod
    def send_to_mco(self, model, kpi_results):
        """Send the KPI results from the evaluation to the MCO
        Must be reimplemented to perform the conversion between the
        two formats. This is of course dependent on the specifics of the
        MCO and how it interacts with the external evaluator program.

        Parameters
        ----------
        model: BaseMCOModel
            The model of the optimizer, instantiated through create_model()

        kpi_results: List(KPICalculatorResult)
            A list of KPI calculator results, one per each KPI calculator.
        """
