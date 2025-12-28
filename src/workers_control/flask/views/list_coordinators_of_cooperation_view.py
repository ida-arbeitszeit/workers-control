from dataclasses import dataclass
from uuid import UUID

from flask import render_template

from workers_control.core.interactors.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationInteractor,
)
from workers_control.flask.types import Response
from workers_control.web.www.presenters.list_coordinations_of_cooperation_presenter import (
    ListCoordinationsOfCooperationPresenter,
)


@dataclass
class ListCoordinationsOfCooperationView:
    list_coordinations_of_cooperation: ListCoordinationsOfCooperationInteractor
    presenter: ListCoordinationsOfCooperationPresenter

    def GET(self, coop_id: UUID) -> Response:
        interactor_response = self.list_coordinations_of_cooperation.list_coordinations(
            ListCoordinationsOfCooperationInteractor.Request(cooperation=coop_id)
        )
        view_model = self.presenter.list_coordinations_of_cooperation(
            interactor_response
        )
        return render_template(
            "user/list_coordinations_of_cooperation.html",
            view_model=view_model,
        )
