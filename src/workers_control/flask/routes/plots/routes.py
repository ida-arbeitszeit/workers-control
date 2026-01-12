from decimal import Decimal
from uuid import UUID

from flask import Blueprint, Response, request
from flask_login import login_required

from workers_control.core.interactors import (
    show_a_account_details,
    show_payout_factor_details,
    show_r_account_details,
)
from workers_control.core.interactors.show_p_account_details import (
    ShowPAccountDetailsInteractor,
)
from workers_control.core.interactors.show_prd_account_details import (
    ShowPRDAccountDetailsInteractor,
)
from workers_control.flask import plotter
from workers_control.flask.dependency_injection import with_injection
from workers_control.web.colors import HexColors
from workers_control.web.translator import Translator
from workers_control.web.www.controllers.show_a_account_details_controller import (
    ShowAAccountDetailsController,
)
from workers_control.web.www.controllers.show_prd_account_details_controller import (
    ShowPRDAccountDetailsController,
)

plots = Blueprint("plots", __name__)


@plots.route("/plots/global_barplot_for_certificates")
@with_injection()
@login_required
def global_barplot_for_certificates(
    plotter: plotter.GeneralPlotter, translator: Translator, colors: HexColors
) -> Response:
    certificates_count = Decimal(request.args["certificates_count"])
    available_product = Decimal(request.args["available_product"])
    png = plotter.create_bar_plot(
        x_coordinates=[
            translator.gettext("Work certificates"),
            translator.gettext("Available product"),
        ],
        height_of_bars=[
            certificates_count,
            available_product,
        ],
        colors_of_bars=[colors.primary, colors.info],
        fig_size=(5, 4),
        y_label=translator.gettext("Hours"),
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/global_barplot_for_means_of_production")
@with_injection()
@login_required
def global_barplot_for_means_of_production(
    plotter: plotter.GeneralPlotter, translator: Translator, colors: HexColors
) -> Response:
    planned_means = Decimal(request.args["planned_means"])
    planned_resources = Decimal(request.args["planned_resources"])
    planned_work = Decimal(request.args["planned_work"])
    png = plotter.create_bar_plot(
        x_coordinates=[
            translator.pgettext("Text should be short", "Fixed means"),
            translator.pgettext("Text should be short", "Liquid means"),
            translator.gettext("Work"),
        ],
        height_of_bars=[
            planned_means,
            planned_resources,
            planned_work,
        ],
        colors_of_bars=[
            colors.primary,
            colors.info,
            colors.danger,
        ],
        fig_size=(5, 4),
        y_label=translator.gettext("Hours"),
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/global_barplot_for_plans")
@with_injection()
@login_required
def global_barplot_for_plans(
    plotter: plotter.GeneralPlotter, translator: Translator, colors: HexColors
) -> Response:
    productive_plans = Decimal(request.args["productive_plans"])
    public_plans = Decimal(request.args["public_plans"])
    png = plotter.create_bar_plot(
        x_coordinates=[
            translator.gettext("Productive plans"),
            translator.gettext("Public plans"),
        ],
        height_of_bars=[productive_plans, public_plans],
        colors_of_bars=[colors.primary, colors.info],
        fig_size=(5, 4),
        y_label=translator.gettext("Amount"),
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/line_plot_of_company_prd_account")
@with_injection()
@login_required
def line_plot_of_company_prd_account(
    controller: ShowPRDAccountDetailsController,
    plotter: plotter.GeneralPlotter,
    interactor: ShowPRDAccountDetailsInteractor,
) -> Response:
    company_id = UUID(request.args["company_id"])
    interactor_request = controller.create_request(company_id)
    interactor_response = interactor.show_details(interactor_request)
    png = plotter.create_line_plot(
        x=interactor_response.plot.timestamps,
        y=interactor_response.plot.accumulated_volumes,
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/line_plot_of_company_r_account")
@with_injection()
@login_required
def line_plot_of_company_r_account(
    plotter: plotter.GeneralPlotter,
    interactor: show_r_account_details.ShowRAccountDetailsInteractor,
) -> Response:
    interactor_request = show_r_account_details.Request(
        company=UUID(request.args["company_id"])
    )
    interactor_response = interactor.show_details(request=interactor_request)
    png = plotter.create_line_plot(
        x=interactor_response.plot.timestamps,
        y=interactor_response.plot.accumulated_volumes,
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/line_plot_of_company_p_account")
@with_injection()
@login_required
def line_plot_of_company_p_account(
    plotter: plotter.GeneralPlotter,
    interactor: ShowPAccountDetailsInteractor,
) -> Response:
    interactor_request = ShowPAccountDetailsInteractor.Request(
        company=UUID(request.args["company_id"])
    )
    interactor_response = interactor.show_details(request=interactor_request)
    png = plotter.create_line_plot(
        x=interactor_response.plot.timestamps,
        y=interactor_response.plot.accumulated_volumes,
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/line_plot_of_company_a_account")
@with_injection()
@login_required
def line_plot_of_company_a_account(
    plotter: plotter.GeneralPlotter,
    controller: ShowAAccountDetailsController,
    interactor: show_a_account_details.ShowAAccountDetailsInteractor,
) -> Response:
    company_id = UUID(request.args["company_id"])
    interactor_request = controller.create_request(company_id)
    interactor_response = interactor.show_details(request=interactor_request)
    png = plotter.create_line_plot(
        x=interactor_response.plot.timestamps,
        y=interactor_response.plot.accumulated_volumes,
    )
    return Response(png, mimetype="image/png", direct_passthrough=True)


@plots.route("/plots/payout_factor_details_bar_plot")
@with_injection()
@login_required
def payout_factor_details_bar_plot(
    interactor: show_payout_factor_details.ShowPayoutFactorDetailsInteractor,
    plotter: plotter.PayoutFactorDetailsPlotter,
) -> Response:
    interactor_response = interactor.show_payout_factor_details()
    png = plotter.plot(interactor_response)
    return Response(png, mimetype="image/png", direct_passthrough=True)
