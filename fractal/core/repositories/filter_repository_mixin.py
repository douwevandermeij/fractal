from abc import ABC
from typing import Callable, Generic, Iterator, List, Optional

from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification


def filter_results(
    q: str,
    *,
    fields: List[str],
    data: Iterator[Entity],
    pre_processor: Optional[Callable[[str], str]] = None,
):
    return filter(
        lambda i: any(
            [
                q in (pre_processor(getattr(i, f)) if pre_processor else getattr(i, f))
                for f in fields
            ]
        ),
        data,
    )


class FilterRepositoryMixin(Repository[Entity], Generic[Entity], ABC):
    def find_filter(
        self,
        q: str,
        *,
        fields: List[str],
        specification: Specification = None,
        pre_processor: Optional[Callable[[str], str]] = None,
    ) -> Iterator[Entity]:
        if not q:
            return self.find(specification)
        return filter_results(
            q,
            fields=fields,
            data=self.find(specification),
            pre_processor=pre_processor,
        )
