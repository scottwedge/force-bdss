from traits.api import Enum, HasStrictTraits

from force_bdss.io.workflow_writer import pop_dunder_recursive
from force_bdss.local_traits import Identifier
from .verifier import VerifierError


class KPISpecification(HasStrictTraits):
    #: The user defined name of the variable containing the kpi value.
    name = Identifier()

    #: The expected outcome of the procedure relative to this KPI.
    objective = Enum("MINIMISE", "MAXIMISE")

    def __getstate__(self):
        return pop_dunder_recursive(super().__getstate__())

    def verify(self):
        """ Verify the KPI specification.

        Check that the KPI specification:
        - has a name

        Returns
        -------
        errors : list of VerifierErrors
            The list of all detected errors in the MCO model.
        """
        errors = []
        if not self.name:
            errors.append(
                VerifierError(
                    subject=self,
                    trait_name='name',
                    local_error="KPI is not named",
                    global_error="A KPI is not named",
                )
            )
        return errors
