from traits.api import ABCHasStrictTraits, Instance

from .i_multi_criteria_optimizer_bundle import IMultiCriteriaOptimizerBundle


class BaseMCOModel(ABCHasStrictTraits):
    bundle = Instance(IMultiCriteriaOptimizerBundle,
                      visible=False, transient=True)

    def __init__(self, bundle, *args, **kwargs):
        self.bundle = bundle
        super(BaseMCOModel, self).__init__(*args, **kwargs)
