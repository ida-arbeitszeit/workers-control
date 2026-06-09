from workers_control.flask.class_based_view import as_flask_view
from workers_control.flask.views import (
    CompanyWorkInviteView,
    RegisterPrivateConsumptionOfBasicServiceView,
    RegisterPrivateConsumptionView,
)
from workers_control.flask.views.create_basic_service_view import (
    CreateBasicServiceView,
)
from workers_control.flask.views.deactivate_basic_service_view import (
    DeactivateBasicServiceView,
)
from workers_control.flask.views.get_private_consumption_details import (
    GetPrivateConsumptionDetailsView,
)
from workers_control.flask.views.list_basic_services_of_worker_view import (
    ListBasicServicesOfWorkerView,
)
from workers_control.flask.views.member_dashboard_view import MemberDashboardView
from workers_control.flask.views.query_private_consumptions import (
    QueryPrivateConsumptionsView,
)
from workers_control.flask.views.show_member_account_details_view import (
    ShowMemberAccountDetailsView,
)

from .blueprint import MemberRoute


@MemberRoute("/consumptions")
@as_flask_view()
class consumptions(QueryPrivateConsumptionsView): ...


@MemberRoute("/consumptions/<uuid:consumption_id>")
@as_flask_view()
class consumption_details(GetPrivateConsumptionDetailsView): ...


@MemberRoute("/basic_services")
@as_flask_view()
class basic_services(ListBasicServicesOfWorkerView): ...


@MemberRoute("/basic_services/<uuid:basic_service_id>/deactivate", methods=["POST"])
@as_flask_view()
class deactivate_basic_service(DeactivateBasicServiceView): ...


@MemberRoute("/create_basic_service", methods=["GET", "POST"])
@as_flask_view()
class create_basic_service(CreateBasicServiceView): ...


@MemberRoute("/register_private_consumption", methods=["GET", "POST"])
@as_flask_view()
class register_private_consumption(RegisterPrivateConsumptionView): ...


@MemberRoute("/register_private_consumption_of_basic_service", methods=["GET", "POST"])
@as_flask_view()
class register_private_consumption_of_basic_service(
    RegisterPrivateConsumptionOfBasicServiceView
): ...


@MemberRoute("/dashboard")
@as_flask_view()
class dashboard(MemberDashboardView): ...


@MemberRoute("/my_account")
@as_flask_view()
class my_account(ShowMemberAccountDetailsView): ...


@MemberRoute("/invite_details/<uuid:invite_id>", methods=["GET", "POST"])
@as_flask_view()
class show_company_work_invite(CompanyWorkInviteView): ...
