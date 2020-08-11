"use strict";

function nextSlide(slider) {
    var $slide = slider.find(".slide.is-active");
    var $nextSlide = $slide.next(".slide");
    var $prevSlide = $slide.prev(".slide");

    if ($nextSlide.length === 0) {
        $nextSlide = slider.find(".slide:first");
    }
    if ($prevSlide.length === 0) {
        $prevSlide = slider.find(".slide:last");
    }
    var $nextNextSlide = $nextSlide.next(".slide");
    if ($nextNextSlide.length === 0) {
        $nextNextSlide = slider.find(".slide:first");
    }
    var $nextNextNextSlide = $nextNextSlide.next(".slide");
    if ($nextNextNextSlide.length === 0) {
        $nextNextNextSlide = slider.find(".slide:first");
    }
    $prevSlide.removeClass("is-prev");
    $slide.removeClass("is-active").addClass("is-prev");
    $nextSlide.addClass("is-active").removeClass("is-next");
    $nextNextSlide.addClass("is-next").removeClass("is-next-next");
    $nextNextNextSlide.addClass("is-next-next");
}

function prevSlide(slider) {
    var $slide = slider.find(".slide.is-active");
    var $nextSlide = $slide.next(".slide");
    var $prevSlide = $slide.prev(".slide");

    if ($nextSlide.length === 0) {
        $nextSlide = slider.find(".slide:first");
    }
    if ($prevSlide.length === 0) {
        $prevSlide = slider.find(".slide:last");
    }
    var $prevPrevSlide = $prevSlide.prev(".slide");
    if ($prevPrevSlide.length === 0) {
        $prevPrevSlide = slider.find(".slide:last");
    }
    var $nextNextNextSlide = $nextNextSlide.next(".slide");
    if ($nextNextNextSlide.length === 0) {
        $nextNextNextSlide = slider.find(".slide:first");
    }

    $nextNextNextSlide.removeClass("is-next-next");
    $nextSlide.removeClass("is-next").addClass("is-next-next");
    $slide.removeClass("is-active").addClass("is-next");
    $prevSlide.addClass("is-active").removeClass("is-prev");
    $prevPrevSlide.addClass("is-prev");
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

    $menuButton.on("click", function () {
        $menu.toggleClass("show-menu");
        $menuButton.toggleClass("open");
    });

    [].forEach.call(document.querySelectorAll('img[data-src]'), function (img) {
        img.setAttribute('src', img.getAttribute('data-src'));
        img.onload = function () {
            img.removeAttribute('data-src');
        };
    });
});

window.dataLayer = window.dataLayer || [];

function gtag() {
    dataLayer.push(arguments);
}

gtag('js', new Date());

gtag('config', 'UA-122537706-1');

//# sourceMappingURL=main-compiled.js.map