from dataclasses import dataclass
from uuid import UUID

from flask import render_template

from workers_control.core.interactors.list_coordinations_of_collaboration import (
    ListCoordinationsOfCollaborationInteractor,
)
from workers_control.flask.types import Response
from workers_control.web.www.presenters.list_coordinations_of_collaboration_presenter import (
    ListCoordinationsOfCollaborationPresenter,
)


@dataclass
class ListCoordinationsOfCollaborationView:
    list_coordinations_of_collaboration: ListCoordinationsOfCollaborationInteractor
    presenter: ListCoordinationsOfCollaborationPresenter

    def GET(self, collab_id: UUID) -> Response:
        interactor_response = (
            self.list_coordinations_of_collaboration.list_coordinations(
                ListCoordinationsOfCollaborationInteractor.Request(
                    collaboration=collab_id
                )
            )
        )
        view_model = self.presenter.list_coordinations_of_collaboration(
            interactor_response
        )
        return render_template(
            "user/list_coordinations_of_collaboration.html",
            view_model=view_model,
        )
