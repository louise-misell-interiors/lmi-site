$(function () {
    const $mainSlider = $(".main-slider");

    setInterval(function () {
        nextSlide($mainSlider);
    }, IMAGE_SLIDER_SPEED);
});