/**
 * @file Menu popup and nav behavior.
 */
document.addEventListener("DOMContentLoaded", function () {
	var openBtn = document.getElementById("openMenuModal");
	var modal = document.getElementById("menuModal");
	var closeButton = modal ? modal.querySelector(".site-nav__dialog-close, .menu-modal-close") : null;

	/** Opens the menu popup. */
	function openSidebar() {
		if (!modal || !openBtn) {
			return;
		}
		modal.classList.add("active", "site-nav__dialog--active");
		openBtn.setAttribute("aria-expanded", "true");
		modal.focus();
		document.body.style.overflow = "hidden";
	}

	/** Closes the menu popup. */
	function closeSidebar() {
		if (!modal || !openBtn) {
			return;
		}
		modal.classList.remove("active", "site-nav__dialog--active");
		openBtn.setAttribute("aria-expanded", "false");
		openBtn.focus();
		document.body.style.overflow = "";
	}

	if (openBtn && modal && closeButton) {
		openBtn.addEventListener("click", openSidebar);
		closeButton.addEventListener("click", closeSidebar);

		modal.addEventListener("keydown", function (event) {
			if (event.key === "Escape") {
				closeSidebar();
			}
		});

		modal.addEventListener("click", function (event) {
			if (event.target === modal) {
				closeSidebar();
			}
		});

		modal.addEventListener("keydown", function (event) {
			if (event.key !== "Tab") {
				return;
			}

			var focusable = modal.querySelectorAll("a,button,[tabindex]:not([tabindex='-1'])");
			if (!focusable.length) {
				return;
			}

			var first = focusable[0];
			var last = focusable[focusable.length - 1];

			if (event.shiftKey && document.activeElement === first) {
				event.preventDefault();
				last.focus();
			} else if (!event.shiftKey && document.activeElement === last) {
				event.preventDefault();
				first.focus();
			}
		});
	}

	document.querySelectorAll(".dropdown-toggle").forEach(function (toggle) {
		toggle.addEventListener("mouseenter", function () {
			var dropdown = this.closest(".dropdown");
			if (dropdown) {
				dropdown.classList.add("show");
			}
		});

		var dropdown = toggle.closest(".dropdown");
		if (dropdown) {
			dropdown.addEventListener("mouseleave", function () {
				this.classList.remove("show");
			});
		}

		toggle.addEventListener("click", function (event) {
			event.preventDefault();
			var dropdownOnClick = this.closest(".dropdown");
			if (dropdownOnClick) {
				dropdownOnClick.classList.toggle("show");
			}
		});
	});

	var mainMenu = document.querySelector(".site-nav, .main-menu");
	if (!mainMenu) {
		return;
	}

	var lastScrollTop = 0;
	window.addEventListener("scroll", function () {
		var scrollTop = window.pageYOffset || document.documentElement.scrollTop;

		if (scrollTop > 100) {
			mainMenu.classList.add("scrolled", "site-nav--scrolled");
		} else {
			mainMenu.classList.remove("scrolled", "site-nav--scrolled");
		}

		if (scrollTop > lastScrollTop && scrollTop > 200) {
			mainMenu.classList.add("nav-up", "site-nav--hidden");
		} else {
			mainMenu.classList.remove("nav-up", "site-nav--hidden");
		}

		lastScrollTop = scrollTop;
	});
});
