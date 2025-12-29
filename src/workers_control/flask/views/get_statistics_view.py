from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import render_template

from workers_control.core.interactors.get_statistics import GetStatisticsInteractor
from workers_control.flask.types import Response
from workers_control.web.www.presenters.get_statistics_presenter import (
    GetStatisticsPresenter,
)


@dataclass
class GetStatisticsView:
    get_statistics_interactor: GetStatisticsInteractor
    presenter: GetStatisticsPresenter

    def GET(self) -> Response:
        interactor_response = self.get_statistics_interactor.get_statistics()
        view_model = self.presenter.present(interactor_response)
        return FlaskResponse(
            render_template("user/statistics.html", view_model=view_model)
        )
