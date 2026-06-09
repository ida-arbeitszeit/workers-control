from flask import render_template

from workers_control.core.interactors.get_accountant_dashboard import (
    GetAccountantDashboardInteractor,
)
from workers_control.core.interactors.list_plans_with_pending_review import (
    ListPlansWithPendingReviewInteractor,
)
from workers_control.flask.class_based_view import as_flask_view
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.flask.views.review_plan_view import ReviewPlanView
from workers_control.web.www.presenters.get_accountant_dashboard_presenter import (
    GetAccountantDashboardPresenter,
)
from workers_control.web.www.presenters.list_plans_with_pending_review_presenter import (
    ListPlansWithPendingReviewPresenter,
)

from .blueprint import AccountantRoute


@AccountantRoute("/accountant/dashboard")
def dashboard(
    flask_session: FlaskSession,
    interactor: GetAccountantDashboardInteractor,
    presenter: GetAccountantDashboardPresenter,
) -> Response:
    current_user = flask_session.get_current_user()
    assert current_user
    response = interactor.get_dashboard(current_user)
    view_model = presenter.create_dashboard_view_model(response)
    return render_template(
        "accountant/dashboard.html",
        view_model=view_model,
    )


@AccountantRoute("/accountant/plans/unreviewed")
def list_plans_with_pending_review(
    interactor: ListPlansWithPendingReviewInteractor,
    presenter: ListPlansWithPendingReviewPresenter,
) -> Response:
    response = interactor.list_plans_with_pending_review(request=interactor.Request())
    view_model = presenter.list_plans_with_pending_review(response)
    return render_template(
        "accountant/plans-to-review-list.html",
        view_model=view_model,
        navbar_items=presenter.create_navbar_items(),
    )


@AccountantRoute("/accountant/plans/<uuid:plan_id>/review", methods=["GET", "POST"])
@as_flask_view()
class review_plan(ReviewPlanView): ...
