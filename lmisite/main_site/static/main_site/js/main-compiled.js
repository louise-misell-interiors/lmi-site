"use strict";

function nextSlide(slider) {
    var $slide = slider.find(".slide.is-active");
    var $nextSlide = $slide.next(".slide");

    if ($nextSlide.length === 0) {
        $nextSlide = slider.find(".slide:first");
    }

    $slide.removeClass("is-active");
    $nextSlide.addClass("is-active");
}

function prevSlide(slider) {
    var $slide = slider.find(".slide.is-active");
    var $prevSlide = $slide.prev(".slide");

    if ($prevSlide.length === 0) {
        $prevSlide = slider.find(".slide:last");
    }

    $slide.removeClass("is-active");
    $prevSlide.addClass("is-active");
}

$(function () {
    var $slider = $(".slider");

    $slider.find(".arrow:first").on("click", function () {
        prevSlide($(this).parent());
    });

    $slider.find(".arrow:last").on("click", function () {
        console.log($(this));
        nextSlide($(this).parent());
    });

    var $menu = $(".nav");
    var $menuButton = $menu.find(".menu-button");
    var $menuLeft = $menu.find(".nav-left > :not(.logos)");
    var $menuRight = $menu.find(".nav-right > :not(.socials)");

    $menuButton.on("click", function () {
        $menu.toggleClass("show-menu");
        var top = $menuLeft.outerHeight();
        $menuRight.css("top", top);
        $menuButton.toggleClass("fa-bars");
        $menuButton.toggleClass("fa-times");
    });
});

//# sourceMappingURL=main-compiled.js.map