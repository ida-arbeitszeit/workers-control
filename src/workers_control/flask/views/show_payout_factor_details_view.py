from dataclasses import dataclass

from flask import Response, render_template

from workers_control.core.interactors import show_payout_factor_details
from workers_control.web.www.presenters import show_payout_factor_details_presenter


@dataclass
class ShowPayoutFactorDetailsView:
    interactor: show_payout_factor_details.ShowPayoutFactorDetailsInteractor
    presenter: show_payout_factor_details_presenter.ShowPayoutFactorDetailsPresenter

    def GET(self) -> Response:
        response = self.interactor.show_payout_factor_details()
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/show_payout_factor_details.html",
                view_model=view_model,
            )
        )
