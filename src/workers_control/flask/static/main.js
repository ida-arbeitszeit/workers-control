// Toggle the mobile navbar ("burger") menu, keep aria-expanded in sync, and
// close it again when clicking outside the menu or following a navbar link.
document.addEventListener('DOMContentLoaded', () => {
  const burgers = Array.prototype.slice.call(
    document.querySelectorAll('.navbar-burger'), 0);

  function closeMenus() {
    burgers.forEach((burger) => {
      const menu = document.getElementById(burger.dataset.target);
      burger.classList.remove('is-active');
      if (menu) menu.classList.remove('is-active');
      burger.setAttribute('aria-expanded', 'false');
    });
  }

  burgers.forEach((burger) => {
    burger.addEventListener('click', (event) => {
      event.stopPropagation();
      const menu = document.getElementById(burger.dataset.target);
      const isActive = burger.classList.toggle('is-active');
      if (menu) menu.classList.toggle('is-active', isActive);
      burger.setAttribute('aria-expanded', isActive ? 'true' : 'false');
    });
  });

  document.addEventListener('click', closeMenus);
});

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

// close notification box
document.addEventListener('DOMContentLoaded', () => {
  (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
    const $notification = $delete.parentNode;

    $delete.addEventListener('click', () => {
      $notification.parentNode.removeChild($notification);
    });
  });
});


document.addEventListener('DOMContentLoaded', () => {
  // Functions to open and close an element
  function openElement($el) {
    $el.classList.add('is-active');
  }

  function closeElement($el) {
    $el.classList.remove('is-active');
  }

  function closeAllElementsByClassName($className) {
    (document.querySelectorAll($className) || []).forEach(($elem) => {
      closeElement($elem);
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
        openElement($dropdown);
      }
    });
  });

});
