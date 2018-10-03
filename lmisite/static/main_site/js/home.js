$(function () {
        const $mainSlider = $(".main-slider");
        const $testimonialsSlider = $(".testimonials");

        setInterval(function () {
            nextSlide($mainSlider);
        }, IMAGE_SLIDER_SPEED);

        setInterval(function () {
            nextSlide($testimonialsSlider);
        }, TESTIMONIALS_SLIDER_SPEED);
    });