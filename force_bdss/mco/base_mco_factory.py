#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import logging

from traits.api import provides, Type, List, Instance

from force_bdss.core.base_factory import BaseFactory
from force_bdss.mco.base_mco import BaseMCO
from force_bdss.mco.base_mco_communicator import BaseMCOCommunicator
from force_bdss.mco.base_mco_model import BaseMCOModel
from force_bdss.mco.parameters.i_mco_parameter_factory import (
    IMCOParameterFactory,
)

from .i_mco_factory import IMCOFactory

log = logging.getLogger(__name__)


@provides(IMCOFactory)
class BaseMCOFactory(BaseFactory):
    """Base class for the MultiCriteria Optimizer factory.
    """

    # NOTE: any changes to the interface of this class must be replicated
    # in the IMCOFactory interface class.

    #: The optimizer class to instantiate. Define this to your MCO class.
    optimizer_class = Type(BaseMCO, allow_none=False)

    #: The model associated to the MCO. Define this to your MCO model class.
    model_class = Type(BaseMCOModel, allow_none=False)

    #: The communicator associated to the MCO. Define this to your MCO comm.
    communicator_class = Type(BaseMCOCommunicator, allow_none=False)

    #: The list of parameter factory classes this MCO supports.
    parameter_factory_classes = List(Type(IMCOParameterFactory))

    #: The instantiated parameter factories.
    parameter_factories = List(Instance(IMCOParameterFactory))

    def __init__(self, plugin, *args, **kwargs):
        super(BaseMCOFactory, self).__init__(plugin=plugin, *args, **kwargs)

        self.optimizer_class = self.get_optimizer_class()
        self.model_class = self.get_model_class()
        self.communicator_class = self.get_communicator_class()
        self.parameter_factory_classes = self.get_parameter_factory_classes()
        self.parameter_factories = self._create_parameter_factories()

    def get_optimizer_class(self):
        raise NotImplementedError(
            f"get_optimizer_class was not implemented "
            f"in factory {self.__class__}"
        )

    def get_model_class(self):
        raise NotImplementedError(
            "get_model_class was not implemented "
            f"in factory {self.__class__}"
        )

    def get_communicator_class(self):
        raise NotImplementedError(
            "get_communicator_class was not implemented "
            f"in factory {self.__class__}"
        )

    def get_parameter_factory_classes(self):
        raise NotImplementedError(
            "get_parameter_factory_classes was not implemented "
            f"in factory {self.__class__}"
        )

    def create_optimizer(self):
        """Factory method.
        Creates the optimizer with the given application
        and model and returns it to the caller.

        Returns
        -------
        BaseMCO
            The optimizer
        """
        return self.optimizer_class(self)

    def create_model(self, model_data=None):
        """Factory method.
        Creates the model object (or network of model objects) of the MCO.
        The model can provide a traits UI View according to traitsui
        specifications, so that a UI can be provided automatically.

        Parameters
        ----------
        model_data: dict or None
            A dictionary of data that can be interpreted appropriately to
            recreate the model. If None, an empty (with defaults) model will
            be created and returned.

        Returns
        -------
        BaseMCOModel
            The MCOModel
        """
        if model_data is None:
            model_data = {}

        return self.model_class(self, **model_data)

    def create_communicator(self):
        """Factory method. Returns the communicator class that allows
        exchange between the MCO and the evaluator code.

        Returns
        -------
        BaseMCOCommunicator
            An instance of the communicator
        """
        return self.communicator_class(self)

    def _create_parameter_factories(self):
        """Returns the parameter factories supported by this MCO

        Returns
        -------
        List of BaseMCOParameterFactory
        """
        return [
            factory_cls(self) for factory_cls in self.parameter_factory_classes
        ]

    def parameter_factory_by_id(self, parameter_id):
        for factory in self.parameter_factories:
            if factory.id == parameter_id:
                return factory

        raise KeyError(
            f"Invalid Parameter Factory id {parameter_id} for "
            f"the specified MCO Factory {self.__class__}. "
            "No plugin responsible for the id is found."
        )
