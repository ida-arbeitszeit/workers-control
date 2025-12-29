from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from workers_control.core.interactors.get_company_summary import (
    GetCompanySummaryInteractor,
    GetCompanySummarySuccess,
)
from workers_control.core.interactors.get_user_account_details import (
    GetUserAccountDetailsInteractor,
)
from workers_control.core.interactors.request_email_address_change import (
    RequestEmailAddressChangeInteractor,
)
from workers_control.flask.class_based_view import as_flask_view
from workers_control.flask.forms import RequestEmailAddressChangeForm
from workers_control.flask.types import Response
from workers_control.flask.views import QueryCompaniesView, QueryPlansView
from workers_control.flask.views.change_email_address_view import ChangeEmailAddressView
from workers_control.flask.views.coop_summary_view import CoopSummaryView
from workers_control.flask.views.get_statistics_view import GetStatisticsView
from workers_control.flask.views.http_error_view import http_404
from workers_control.flask.views.list_all_cooperations_view import (
    ListAllCooperationsView,
)
from workers_control.flask.views.list_coordinators_of_cooperation_view import (
    ListCoordinationsOfCooperationView,
)
from workers_control.flask.views.list_transfers import ListTransfersView
from workers_control.flask.views.show_a_account_details_view import (
    ShowAAccountDetailsView,
)
from workers_control.flask.views.show_company_accounts_view import CompanyAccountsView
from workers_control.flask.views.show_p_account_details_view import (
    ShowPAccountDetailsView,
)
from workers_control.flask.views.show_prd_account_details_view import (
    ShowPRDAccountDetailsView,
)
from workers_control.flask.views.show_r_account_details_view import (
    ShowRAccountDetailsView,
)
from workers_control.web.www.controllers.request_email_address_change_controller import (
    RequestEmailAddressChangeController,
)
from workers_control.web.www.controllers.user_account_details_controller import (
    UserAccountDetailsController,
)
from workers_control.web.www.presenters.get_company_summary_presenter import (
    GetCompanySummarySuccessPresenter,
)
from workers_control.web.www.presenters.request_email_address_change_presenter import (
    RequestEmailAddressChangePresenter,
)
from workers_control.web.www.presenters.user_account_details_presenter import (
    UserAccountDetailsPresenter,
)

from .blueprint import AuthenticatedUserRoute


@AuthenticatedUserRoute("/account")
def account_details(
    controller: UserAccountDetailsController,
    interactor: GetUserAccountDetailsInteractor,
    presenter: UserAccountDetailsPresenter,
) -> Response:
    uc_request = controller.parse_web_request()
    uc_response = interactor.get_user_account_details(uc_request)
    view_model = presenter.render_user_account_details(uc_response)
    return render_template("user/account_details.html", view_model=view_model)


@AuthenticatedUserRoute("/company_summary/<uuid:company_id>")
def company_summary(
    company_id: UUID,
    get_company_summary: GetCompanySummaryInteractor,
    presenter: GetCompanySummarySuccessPresenter,
):
    interactor_response = get_company_summary.execute(company_id)
    if isinstance(interactor_response, GetCompanySummarySuccess):
        view_model = presenter.present(interactor_response)
        return render_template(
            "user/company_summary.html",
            view_model=view_model,
        )
    else:
        return http_404()


@AuthenticatedUserRoute("/request-email-change", methods=["GET", "POST"])
def request_email_change(
    controller: RequestEmailAddressChangeController,
    presenter: RequestEmailAddressChangePresenter,
    interactor: RequestEmailAddressChangeInteractor,
) -> Response:
    template_name = "user/request_email_address_change.html"
    form = RequestEmailAddressChangeForm(request.form)
    match request.method:
        case "POST":
            if not form.validate():
                return FlaskResponse(
                    render_template(template_name, form=form), status=400
                )
            uc_request = controller.process_email_address_change_request(form)
            uc_response = interactor.request_email_address_change(uc_request)
            view_model = presenter.render_response(uc_response, form)
            if view_model.redirect_url:
                return redirect(view_model.redirect_url)
            else:
                return FlaskResponse(
                    render_template(template_name, form=form), status=400
                )
        case _:
            return FlaskResponse(render_template(template_name, form=form), status=200)


@AuthenticatedUserRoute("/change-email/<token>", methods=["GET", "POST"])
@as_flask_view()
class change_email_address(ChangeEmailAddressView): ...


@AuthenticatedUserRoute("/query_plans", methods=["GET"])
@as_flask_view()
class query_plans(QueryPlansView): ...


@AuthenticatedUserRoute("/query_companies", methods=["GET"])
@as_flask_view()
class query_companies(QueryCompaniesView): ...


@AuthenticatedUserRoute("/statistics")
@as_flask_view()
class statistics(GetStatisticsView): ...


@AuthenticatedUserRoute("/cooperation_summary/<uuid:coop_id>")
@as_flask_view()
class coop_summary(CoopSummaryView): ...


@AuthenticatedUserRoute(
    "/cooperation_summary/<uuid:coop_id>/coordinators", methods=["GET"]
)
@as_flask_view()
class list_coordinators_of_cooperation(ListCoordinationsOfCooperationView): ...


@AuthenticatedUserRoute("/list_all_cooperations")
@as_flask_view()
class list_all_cooperations(ListAllCooperationsView): ...


@AuthenticatedUserRoute("/company/<uuid:company_id>/accounts")
@as_flask_view()
class company_accounts(CompanyAccountsView): ...


@AuthenticatedUserRoute("/company/<uuid:company_id>/account_p")
@as_flask_view()
class company_account_p(ShowPAccountDetailsView): ...


@AuthenticatedUserRoute("/company/<uuid:company_id>/account_r")
@as_flask_view()
class company_account_r(ShowRAccountDetailsView): ...


@AuthenticatedUserRoute("/company/<uuid:company_id>/account_a")
@as_flask_view()
class company_account_a(ShowAAccountDetailsView): ...


@AuthenticatedUserRoute("/company/<uuid:company_id>/account_prd")
@as_flask_view()
class company_account_prd(ShowPRDAccountDetailsView): ...


@AuthenticatedUserRoute("/transfers")
@as_flask_view()
class list_transfers(ListTransfersView): ...
