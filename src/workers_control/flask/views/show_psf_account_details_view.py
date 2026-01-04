from dataclasses import dataclass

from flask import Response, render_template

from workers_control.core.interactors.show_psf_account_details import (
    ShowPSFAccountDetailsInteractor,
)
from workers_control.web.www.presenters.show_psf_account_details_presenter import (
    ShowPSFAccountDetailsPresenter,
)


@dataclass
class ShowPSFAccountDetailsView:
    interactor: ShowPSFAccountDetailsInteractor
    presenter: ShowPSFAccountDetailsPresenter

    def GET(self) -> Response:
        response = self.interactor.show_details()
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/account_psf.html",
                view_model=view_model,
            )
        )
