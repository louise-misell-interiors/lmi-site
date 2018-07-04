"use strict";

$(function () {
    var $sliders = $(".content .row:first");
    var $leftSlider = $sliders.find(".slider:first");
    var $rightSlider = $sliders.find(".slider:last");

    $leftSlider.find(".arrow:first").on("click", function () {
        prevSlide($rightSlider);
    });
    $leftSlider.find(".arrow:last").on("click", function () {
        nextSlide($rightSlider);
    });

    $rightSlider.find(".arrow:first").on("click", function () {
        prevSlide($leftSlider);
    });
    $rightSlider.find(".arrow:last").on("click", function () {
        nextSlide($leftSlider);
    });
});

//# sourceMappingURL=project-compiled.js.map