from __future__ import annotations

from dataclasses import dataclass

from workers_control.core.interactors.list_coordinations_of_collaboration import (
    ListCoordinationsOfCollaborationInteractor as Interactor,
)
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class ListCoordinationsOfCollaborationPresenter:
    @dataclass
    class CoordinationInfo:
        coordinator_name: str
        coordinator_url: str
        start_time: str
        end_time: str

    @dataclass
    class ViewModel:
        collaboration_url: str
        collaboration_name: str
        has_coordinations: bool
        coordinations: list[ListCoordinationsOfCollaborationPresenter.CoordinationInfo]
        navbar_items: list[NavbarItem]

    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter
    translator: Translator

    def list_coordinations_of_collaboration(
        self, response: Interactor.Response
    ) -> ListCoordinationsOfCollaborationPresenter.ViewModel:
        return self.ViewModel(
            collaboration_url=self.url_index.get_collab_summary_url(
                collab_id=response.collaboration_id,
            ),
            collaboration_name=response.collaboration_name,
            has_coordinations=len(response.coordinations) > 0,
            coordinations=[
                self.CoordinationInfo(
                    coordinator_name=coordination.coordinator_name,
                    coordinator_url=self.url_index.get_company_summary_url(
                        company_id=coordination.coordinator_id,
                    ),
                    start_time=self.datetime_formatter.format_datetime(
                        date=coordination.start_time,
                        fmt="%d.%m.%Y %H:%M",
                    ),
                    end_time=(
                        "-"
                        if coordination.end_time is None
                        else self.datetime_formatter.format_datetime(
                            date=coordination.end_time,
                            fmt="%d.%m.%Y %H:%M",
                        )
                    ),
                )
                for coordination in response.coordinations
            ],
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Collaboration"),
                    url=self.url_index.get_collab_summary_url(
                        collab_id=response.collaboration_id,
                    ),
                ),
                NavbarItem(
                    text=self.translator.gettext("Coordinators"),
                    url=None,
                ),
            ],
        )
