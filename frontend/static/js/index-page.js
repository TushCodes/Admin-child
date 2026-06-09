/**
 * @file Runs home-page stats, focus treatment, and slider interactions.
 */
document.addEventListener("DOMContentLoaded", function () {
    var statsNumbers = document.querySelectorAll(".stats-number");
    if (statsNumbers.length) {
        var statsObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = "1";
                    entry.target.style.transform = "translateY(0)";
                    statsObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.5,
            rootMargin: "0px"
        });

        statsNumbers.forEach(function (number) {
            number.style.opacity = "0";
            number.style.transform = "translateY(20px)";
            number.style.transition = "opacity 0.6s ease, transform 0.6s ease";
            statsObserver.observe(number);
        });
    }

    document
        .querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])')
        .forEach(function (element) {
            element.addEventListener("focus", function () {
                this.style.outline = "2px solid rgba(130, 207, 43, 0.4)";
                this.style.outlineOffset = "2px";
            });

            element.addEventListener("blur", function () {
                this.style.outline = "";
                this.style.outlineOffset = "";
            });
        });

    var currentSlide = 1;
    var totalSlides = 3;
    var slideInterval = 7000;

    /** Moves home slider to next slide. */
    function nextSlide() {
        currentSlide = currentSlide >= totalSlides ? 1 : currentSlide + 1;
        var slideInput = document.getElementById("slides_" + currentSlide);
        if (slideInput) {
            slideInput.checked = true;
        }
    }

    var autoSlider = setInterval(nextSlide, slideInterval);
    document.querySelectorAll(".navigation label").forEach(function (label, index) {
        label.addEventListener("click", function () {
            clearInterval(autoSlider);
            currentSlide = index + 1;
            setTimeout(function () {
                autoSlider = setInterval(nextSlide, slideInterval);
            }, slideInterval);
        });
    });

    var carousel = document.getElementById("slider1");
    if (carousel) {
        carousel.addEventListener("mouseenter", function () {
            clearInterval(autoSlider);
        });

        carousel.addEventListener("mouseleave", function () {
            autoSlider = setInterval(nextSlide, slideInterval);
        });
    }
});
