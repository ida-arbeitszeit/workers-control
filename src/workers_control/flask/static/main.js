// Detect browser timezone and store in cookie for server-side use
(function() {
  var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  if (tz && document.cookie.indexOf("user_timezone=" + tz) === -1) {
    document.cookie = "user_timezone=" + tz + ";path=/;max-age=31536000;SameSite=Lax";
  }
})();

function togglePasswordVisibility(clickedElement) {
  let input = clickedElement.parentElement.firstElementChild
  let eye = input.nextElementSibling.nextElementSibling
  if (input.type === "password") {
    input.type = "text"
    eye.classList.add("is-hidden")
    eye.nextElementSibling.classList.remove("is-hidden")
  } else {
    input.type = "password"
    eye.classList.remove("is-hidden")
    eye.nextElementSibling.classList.add("is-hidden")
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-type="password-toggle"]').forEach((toggle) => {
    toggle.addEventListener('click', () => togglePasswordVisibility(toggle));
  });
});

// close notification box
document.addEventListener('DOMContentLoaded', () => {
  (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
    const $notification = $delete.parentNode;

    $delete.addEventListener('click', () => {
      const $box = $notification.closest('.notification_box');
      $notification.remove();
      if ($box && !$box.querySelector('.notification')) {
        $box.remove();
      }
    });
  });
});


document.addEventListener('DOMContentLoaded', () => {
  function setElementOpen($el, isOpen) {
    $el.classList.toggle('is-active', isOpen);
    const $trigger = $el.querySelector('.dropdown-trigger [aria-expanded]');
    if ($trigger) {
      $trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }
  }

  function closeAllElementsByClassName($className) {
    (document.querySelectorAll($className) || []).forEach(($elem) => {
      setElementOpen($elem, false);
    });
  }

  document.addEventListener('click', function () {
    closeAllElementsByClassName('.dropdown');
  });

  (document.querySelectorAll('.dropdown') || []).forEach(($dropdown) => {
    $dropdown.addEventListener('click', function (event) {
      event.stopPropagation();
      let isOpen = $dropdown.classList.contains('is-active')
      closeAllElementsByClassName('.dropdown')
      if (!isOpen) {
        setElementOpen($dropdown, true);
      }
    });
  });

});
