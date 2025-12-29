from dataclasses import dataclass

from workers_control.core.interactors import get_user_account_details as interactor
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    user_id: str
    email_address: str
    current_user_time: str
    request_email_address_change_url: str


@dataclass
class UserAccountDetailsPresenter:
    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter

    def render_user_account_details(self, response: interactor.Response) -> ViewModel:
        assert response.user_info
        return ViewModel(
            user_id=str(response.user_info.id),
            email_address=response.user_info.email_address,
            current_user_time=self.datetime_formatter.format_datetime(
                response.user_info.current_time, fmt="%Y-%m-%d %H:%M:%S %z (%Z)"
            ),
            request_email_address_change_url=self.url_index.get_request_change_email_url(),
        )
