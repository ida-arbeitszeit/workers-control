from dataclasses import dataclass
from uuid import UUID

from flask import render_template

from workers_control.core.interactors.get_collab_summary import (
    GetCollabSummaryInteractor,
    GetCollabSummaryRequest,
)
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.presenters.get_collab_summary_presenter import (
    GetCollabSummarySuccessPresenter,
)


@dataclass
class CollabSummaryView:
    get_collab_summary: GetCollabSummaryInteractor
    presenter: GetCollabSummarySuccessPresenter
    flask_session: FlaskSession

    def GET(self, collab_id: UUID) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        interactor_response = self.get_collab_summary.execute(
            GetCollabSummaryRequest(current_user, collab_id)
        )
        if interactor_response:
            view_model = self.presenter.present(interactor_response)
            return render_template(
                "user/collab_summary.html",
                view_model=view_model,
                navbar_items=self.presenter.create_navbar_items(),
            )
        else:
            return http_404()
