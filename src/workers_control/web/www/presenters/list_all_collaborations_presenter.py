from dataclasses import dataclass
from typing import List

from workers_control.core.interactors.list_all_cooperations import (
    ListAllCooperationsResponse,
)
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem


@dataclass
class ListedCollaboration:
    id: str
    name: str
    plan_count: str
    collab_summary_url: str


@dataclass
class ListAllCollaborationsViewModel:
    collaborations: List[ListedCollaboration]
    show_results: bool


@dataclass
class ListAllCollaborationsPresenter:
    url_index: UrlIndex
    translator: Translator

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(text=self.translator.gettext("All collaborations"), url=None)
        ]

    def present(
        self, response: ListAllCooperationsResponse
    ) -> ListAllCollaborationsViewModel:
        collaborations = [
            ListedCollaboration(
                id=str(collab.id),
                name=collab.name,
                plan_count=str(collab.plan_count),
                collab_summary_url=self.url_index.get_collab_summary_url(
                    collab_id=collab.id
                ),
            )
            for collab in response.cooperations
        ]
        return ListAllCollaborationsViewModel(
            collaborations=collaborations, show_results=bool(collaborations)
        )
