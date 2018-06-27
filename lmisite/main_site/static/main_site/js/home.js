$(function () {
    const $mainSlider = $(".main-slider");
    const $testimonialsSlider = $(".testimonials");

    setInterval(function () {
        nextSlide($mainSlider);
    }, 5000);

    setInterval(function () {
        nextSlide($testimonialsSlider);
    }, 10000);
});