$(function () {
    const $mainSlider = $(".main-slider");
    const $testimonialsSlider = $(".testimonials");

    setInterval(function () {
        nextSlide($mainSlider);
        nextSlide($testimonialsSlider);
    }, 5000);
});