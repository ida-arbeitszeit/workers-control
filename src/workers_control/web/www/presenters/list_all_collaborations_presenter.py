from dataclasses import dataclass
from typing import List

from workers_control.core.interactors.list_all_collaborations import (
    ListAllCollaborationsResponse,
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
    navbar_items: list[NavbarItem]


@dataclass
class ListAllCollaborationsPresenter:
    url_index: UrlIndex
    translator: Translator

    def present(
        self, response: ListAllCollaborationsResponse
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
            for collab in response.collaborations
        ]
        return ListAllCollaborationsViewModel(
            collaborations=collaborations,
            show_results=bool(collaborations),
            navbar_items=[
                NavbarItem(text=self.translator.gettext("All collaborations"), url=None)
            ],
        )
