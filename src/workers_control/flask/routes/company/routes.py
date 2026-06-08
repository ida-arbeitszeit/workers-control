from workers_control.flask.class_based_view import as_flask_view
from workers_control.flask.views import (
    EndCooperationView,
    InviteWorkerToCompanyView,
    RequestCooperationView,
)
from workers_control.flask.views.accept_cooperation_request_view import (
    AcceptCooperationRequestView,
)
from workers_control.flask.views.cancel_cooperation_request_view import (
    CancelCooperationRequestView,
)
from workers_control.flask.views.company_dashboard_view import CompanyDashboardView
from workers_control.flask.views.create_cooperation_view import CreateCooperationView
from workers_control.flask.views.create_draft_from_plan_view import (
    CreateDraftFromPlanView,
)
from workers_control.flask.views.create_draft_view import CreateDraftView
from workers_control.flask.views.delete_draft_view import DeleteDraftView
from workers_control.flask.views.deny_cooperation_view import DenyCooperationView
from workers_control.flask.views.draft_details_view import DraftDetailsView
from workers_control.flask.views.end_plan_cooperation_view import (
    EndPlanCooperationView,
)
from workers_control.flask.views.file_plan_with_accounting_view import (
    FilePlanWithAccountingView,
)
from workers_control.flask.views.get_plan_details_company_view import (
    GetPlanDetailsCompanyView,
)
from workers_control.flask.views.get_productive_consumption_details import (
    GetProductiveConsumptionDetailsView,
)
from workers_control.flask.views.hide_plan_view import HidePlanView
from workers_control.flask.views.list_pending_work_invites_view import (
    ListPendingWorkInvitesView,
)
from workers_control.flask.views.list_registered_hours_worked_view import (
    ListRegisteredHoursWorkedView,
)
from workers_control.flask.views.query_company_consumptions_view import (
    QueryCompanyConsumptionsView,
)
from workers_control.flask.views.register_hours_worked_view import (
    RegisterHoursWorkedView,
)
from workers_control.flask.views.register_productive_consumption import (
    RegisterProductiveConsumptionView,
)
from workers_control.flask.views.register_productive_consumption_of_basic_service_view import (
    RegisterProductiveConsumptionOfBasicServiceView,
)
from workers_control.flask.views.remove_worker_from_company_view import (
    RemoveWorkerFromCompanyView,
)
from workers_control.flask.views.request_coordination_transfer_view import (
    RequestCoordinationTransferView,
)
from workers_control.flask.views.review_registered_consumptions_view import (
    ReviewRegisteredConsumptionsView,
)
from workers_control.flask.views.revoke_plan_filing_view import RevokePlanFilingView
from workers_control.flask.views.show_coordination_transfer_request_view import (
    ShowCoordinationTransferRequestView,
)
from workers_control.flask.views.show_my_cooperations_view import (
    ShowMyCooperationsView,
)
from workers_control.flask.views.show_my_plans_view import ShowMyPlansView

from .blueprint import CompanyRoute


@CompanyRoute("/dashboard")
@as_flask_view()
class dashboard(CompanyDashboardView): ...


@CompanyRoute("/consumptions")
@as_flask_view()
class my_consumptions(QueryCompanyConsumptionsView): ...


@CompanyRoute("/consumptions/<uuid:consumption_id>")
@as_flask_view()
class consumption_details(GetProductiveConsumptionDetailsView): ...


@CompanyRoute("/draft/delete/<uuid:draft_id>", methods=["POST"])
@as_flask_view()
class delete_draft(DeleteDraftView): ...


@CompanyRoute("/draft/from-plan/<uuid:plan_id>", methods=["POST"])
@as_flask_view()
class create_draft_from_plan(CreateDraftFromPlanView): ...


@CompanyRoute("/create_draft", methods=["GET", "POST"])
@as_flask_view()
class create_draft(CreateDraftView): ...


@CompanyRoute("/file_plan/<draft_id>", methods=["POST"])
@as_flask_view()
class file_plan(FilePlanWithAccountingView): ...


@CompanyRoute("/draft/<uuid:draft_id>", methods=["GET", "POST"])
@as_flask_view()
class get_draft_details(DraftDetailsView): ...


@CompanyRoute("/my_plans", methods=["GET"])
@as_flask_view()
class my_plans(ShowMyPlansView): ...


@CompanyRoute("/plan/revoke/<uuid:plan_id>", methods=["POST"])
@as_flask_view()
class revoke_plan_filing(RevokePlanFilingView): ...


@CompanyRoute("/hide_plan/<uuid:plan_id>", methods=["GET", "POST"])
@as_flask_view()
class hide_plan(HidePlanView): ...


@CompanyRoute("/register_hours_worked", methods=["GET", "POST"])
@as_flask_view()
class register_hours_worked(RegisterHoursWorkedView): ...


@CompanyRoute("/registered_hours_worked")
@as_flask_view()
class registered_hours_worked(ListRegisteredHoursWorkedView): ...


@CompanyRoute("/register_productive_consumption", methods=["GET", "POST"])
@as_flask_view()
class register_productive_consumption(RegisterProductiveConsumptionView): ...


@CompanyRoute(
    "/register_productive_consumption_of_basic_service", methods=["GET", "POST"]
)
@as_flask_view()
class register_productive_consumption_of_basic_service(
    RegisterProductiveConsumptionOfBasicServiceView
): ...


@CompanyRoute("/plan_details/<uuid:plan_id>")
@as_flask_view()
class plan_details(GetPlanDetailsCompanyView): ...


@CompanyRoute(
    "/cooperation_summary/<uuid:coop_id>/request_coordination_transfer",
    methods=["GET", "POST"],
)
@as_flask_view()
class request_coordination_transfer(RequestCoordinationTransferView): ...


@CompanyRoute(
    "/show_coordination_transfer_request/<uuid:transfer_request>",
    methods=["GET", "POST"],
)
@as_flask_view()
class show_coordination_transfer_request(ShowCoordinationTransferRequestView): ...


@CompanyRoute("/create_cooperation", methods=["GET", "POST"])
@as_flask_view()
class create_cooperation(CreateCooperationView): ...


@CompanyRoute("/request_cooperation", methods=["GET", "POST"])
@as_flask_view()
class request_cooperation(RequestCooperationView): ...


@CompanyRoute("/my_cooperations", methods=["GET"])
@as_flask_view()
class my_cooperations(ShowMyCooperationsView): ...


@CompanyRoute("/accept_cooperation_request", methods=["POST"])
@as_flask_view()
class accept_cooperation_request(AcceptCooperationRequestView): ...


@CompanyRoute("/deny_cooperation_request", methods=["POST"])
@as_flask_view()
class deny_cooperation_request(DenyCooperationView): ...


@CompanyRoute("/cancel_cooperation_request", methods=["POST"])
@as_flask_view()
class cancel_cooperation_request(CancelCooperationRequestView): ...


@CompanyRoute("/invite_worker_to_company", methods=["GET", "POST"])
@as_flask_view()
class invite_worker_to_company(InviteWorkerToCompanyView): ...


@CompanyRoute("/remove_worker_from_company", methods=["GET", "POST"])
@as_flask_view()
class remove_worker_from_company(RemoveWorkerFromCompanyView): ...


@CompanyRoute("/list_pending_work_invites", methods=["GET", "POST"])
@as_flask_view()
class list_pending_work_invites(ListPendingWorkInvitesView): ...


@CompanyRoute("/end_cooperation", methods=["POST"])
@as_flask_view()
class end_cooperation(EndCooperationView): ...


@CompanyRoute("/end_plan_cooperation", methods=["POST"])
@as_flask_view()
class end_plan_cooperation(EndPlanCooperationView): ...


@CompanyRoute("/review_registered_consumptions")
@as_flask_view()
class review_registered_consumptions(ReviewRegisteredConsumptionsView): ...
