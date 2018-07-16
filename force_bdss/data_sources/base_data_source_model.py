from traits.api import (
    Instance, List, Event, on_trait_change
)

from force_bdss.core.base_model import BaseModel
from force_bdss.core.input_slot_info import InputSlotInfo
from force_bdss.core.output_slot_info import OutputSlotInfo
from force_bdss.data_sources.i_data_source_factory import IDataSourceFactory


class BaseDataSourceModel(BaseModel):
    """Base class for the factory specific DataSource models.
    This model will also provide, through traits/traitsui magic the View
    that will appear in the workflow manager UI.

    In your factory definition, your factory-specific model must reimplement
    this class.
    """
    #: A reference to the creating factory, so that we can
    #: retrieve it as the originating factory.
    factory = Instance(IDataSourceFactory, visible=False, transient=True)

    #: Specifies binding between input slots and source for that value.
    #: Each InputSlotMap instance specifies this information for each of the
    #: slots.
    input_slot_info = List(Instance(InputSlotInfo), visible=False)

    #: Allows to assign names and KPI status to the output slots, so that
    #: they can be referenced somewhere else (e.g. another layer's
    #: DataSources).
    #: If the name is the empty string, it means that the user is not
    #: interested in preserving the information, and should therefore be
    #: discarded and not propagated further.
    output_slot_info = List(Instance(OutputSlotInfo), visible=False)

    #: This event claims that a change in the model influences the slots
    #: (either input or output). It must be triggered every time a specific
    #: option in your model implies a change in the slots. The UI will detect
    #: this and adapt the visual entries.
    changes_slots = Event()

    def __getstate__(self):
        state = super(BaseDataSourceModel, self).__getstate__()
        state["input_slot_info"] = [
            x.__getstate__() for x in self.input_slot_info
        ]
        state["output_slot_info"] = [
            x.__getstate__() for x in self.output_slot_info
        ]
        return state

    @on_trait_change("+changes_slots")
    def _trigger_changes_slots(self, obj, name, new):
        changes_slots = self.traits()[name].changes_slots

        if changes_slots:
            self.changes_slots = True
