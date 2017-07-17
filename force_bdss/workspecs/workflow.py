from traits.api import HasStrictTraits, Instance, String, List

from force_bdss.workspecs.data_source import DataSource
from force_bdss.workspecs.kpi_calculator import KPICalculator
from .multi_criteria_optimizer import MultiCriteriaOptimizer


class Workflow(HasStrictTraits):
    name = String()
    multi_criteria_optimizer = Instance(MultiCriteriaOptimizer)
    data_sources = List(DataSource)
    kpi_calculators = List(KPICalculator)

    @classmethod
    def from_json(cls, json_data):
        self = cls(
            multi_criteria_optimizer=MultiCriteriaOptimizer.from_json(
                    json_data["multi_criteria_optimizer"]
            ),
            data_sources=[
                DataSource.from_json(data_source_data)
                for data_source_data in json_data["data_sources"]],
            kpi_calculators=[
                KPICalculator.from_json(kpi_calculator_data)
                for kpi_calculator_data in json_data["kpi_calculators"]]
        )

        return self
