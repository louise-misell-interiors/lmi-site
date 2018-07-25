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
        nextSlide($(this).parent());
    });

    var $menu = $(".nav");
    var $menuButton = $menu.find(".menu-button");
    var $menuLeft = $menu.find(".nav-left");
    var $menuRight = $menu.find(".nav-right");

    $menuButton.on("click", function () {
        $menu.toggleClass("show-menu");
        var top = $menuLeft.outerHeight();
        $menuRight.css("top", top);
        $menuButton.toggleClass("fa-bars");
        $menuButton.toggleClass("fa-times");
    });
});

window.dataLayer = window.dataLayer || [];
function gtag() {
    dataLayer.push(arguments);
}
gtag('js', new Date());

gtag('config', 'UA-122537706-1');

//# sourceMappingURL=main-compiled.js.map