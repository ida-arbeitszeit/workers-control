from workers_control.flask.class_based_view import as_flask_view
from workers_control.flask.views.accept_collaboration_request_view import (
    AcceptCollaborationRequestView,
)
from workers_control.flask.views.cancel_collaboration_request_view import (
    CancelCollaborationRequestView,
)
from workers_control.flask.views.company_dashboard_view import CompanyDashboardView
from workers_control.flask.views.create_collaboration_view import (
    CreateCollaborationView,
)
from workers_control.flask.views.create_draft_from_plan_view import (
    CreateDraftFromPlanView,
)
from workers_control.flask.views.create_draft_view import CreateDraftView
from workers_control.flask.views.delete_draft_view import DeleteDraftView
from workers_control.flask.views.deny_collaboration_view import DenyCollaborationView
from workers_control.flask.views.draft_details_view import DraftDetailsView
from workers_control.flask.views.end_collaboration_view import EndCollaborationView
from workers_control.flask.views.end_plan_collaboration_view import (
    EndPlanCollaborationView,
)
from workers_control.flask.views.file_plan_with_accounting_view import (
    FilePlanWithAccountingView,
)
from workers_control.flask.views.get_productive_consumption_details import (
    GetProductiveConsumptionDetailsView,
)
from workers_control.flask.views.hide_plan_view import HidePlanView
from workers_control.flask.views.invite_worker_to_company import (
    InviteWorkerToCompanyView,
)
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
from workers_control.flask.views.request_collaboration_view import (
    RequestCollaborationView,
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
from workers_control.flask.views.show_my_collaborations_view import (
    ShowMyCollaborationsView,
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


@CompanyRoute(
    "/collaboration_summary/<uuid:collab_id>/request_coordination_transfer",
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


@CompanyRoute("/create_collaboration", methods=["GET", "POST"])
@as_flask_view()
class create_collaboration(CreateCollaborationView): ...


@CompanyRoute("/request_collaboration", methods=["GET", "POST"])
@as_flask_view()
class request_collaboration(RequestCollaborationView): ...


@CompanyRoute("/my_collaborations", methods=["GET"])
@as_flask_view()
class my_collaborations(ShowMyCollaborationsView): ...


@CompanyRoute("/accept_collaboration_request", methods=["POST"])
@as_flask_view()
class accept_collaboration_request(AcceptCollaborationRequestView): ...


@CompanyRoute("/deny_collaboration_request", methods=["POST"])
@as_flask_view()
class deny_collaboration_request(DenyCollaborationView): ...


@CompanyRoute("/cancel_collaboration_request", methods=["POST"])
@as_flask_view()
class cancel_collaboration_request(CancelCollaborationRequestView): ...


@CompanyRoute("/invite_worker_to_company", methods=["GET", "POST"])
@as_flask_view()
class invite_worker_to_company(InviteWorkerToCompanyView): ...


@CompanyRoute("/remove_worker_from_company", methods=["GET", "POST"])
@as_flask_view()
class remove_worker_from_company(RemoveWorkerFromCompanyView): ...


@CompanyRoute("/list_pending_work_invites", methods=["GET", "POST"])
@as_flask_view()
class list_pending_work_invites(ListPendingWorkInvitesView): ...


@CompanyRoute("/end_collaboration", methods=["POST"])
@as_flask_view()
class end_collaboration(EndCollaborationView): ...


@CompanyRoute("/end_plan_collaboration", methods=["POST"])
@as_flask_view()
class end_plan_collaboration(EndPlanCollaborationView): ...


@CompanyRoute("/review_registered_consumptions")
@as_flask_view()
class review_registered_consumptions(ReviewRegisteredConsumptionsView): ...
