from dataclasses import dataclass

from flask import render_template

from workers_control.core.interactors.list_all_cooperations import (
    ListAllCooperationsInteractor,
)
from workers_control.flask.types import Response
from workers_control.web.www.presenters.list_all_collaborations_presenter import (
    ListAllCollaborationsPresenter,
)


@dataclass
class ListAllCollaborationsView:
    interactor: ListAllCooperationsInteractor
    presenter: ListAllCollaborationsPresenter

    def GET(self) -> Response:
        response = self.interactor.execute()
        view_model = self.presenter.present(response)
        return render_template(
            "user/list_all_collaborations.html",
            view_model=view_model,
            navbar_items=self.presenter.create_navbar_items(),
        )
