function nextSlide(slider) {
    const $slide = slider.find(".slide.is-active");
    let $nextSlide = $slide.next(".slide");
    let $prevSlide = $slide.prev(".slide");

    if ($nextSlide.length === 0) {
        $nextSlide = slider.find(".slide:first");
    }
    if ($prevSlide.length === 0) {
        $prevSlide = slider.find(".slide:last");
    }
    let $nextNextSlide = $nextSlide.next(".slide");
    if ($nextNextSlide.length === 0) {
        $nextNextSlide = slider.find(".slide:first");
    }
    let $nextNextNextSlide = $nextNextSlide.next(".slide");
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
    const $slide = slider.find(".slide.is-active");
    let $nextSlide = $slide.next(".slide");
    let $prevSlide = $slide.prev(".slide");

    if ($nextSlide.length === 0) {
        $nextSlide = slider.find(".slide:first");
    }
    if ($prevSlide.length === 0) {
        $prevSlide = slider.find(".slide:last");
    }
    let $prevPrevSlide = $prevSlide.prev(".slide");
    if ($prevPrevSlide.length === 0) {
        $prevPrevSlide = slider.find(".slide:last");
    }
    let $nextNextSlide = $nextSlide.next(".slide");
    if ($nextNextSlide.length === 0) {
        $nextNextSlide = slider.find(".slide:first");
    }

    $nextNextSlide.removeClass("is-next-next");
    $nextSlide.removeClass("is-next").addClass("is-next-next");
    $slide.removeClass("is-active").addClass("is-next");
    $prevSlide.addClass("is-active").removeClass("is-prev");
    $prevPrevSlide.addClass("is-prev");
}

$(function () {
    const $slider = $(".slider");

    $slider.find(".arrow:first").on("click", function () {
        prevSlide($(this).parent());
    });

    $slider.find(".arrow:last").on("click", function () {
        nextSlide($(this).parent());
    });

    const $menu = $(".nav");
    const $menuButton = $menu.find(".menu-button");

    $menuButton.on("click", function () {
        $menu.toggleClass("show-menu");
        $menuButton.toggleClass("open");
    });

    [].forEach.call(document.querySelectorAll('img[data-src]'),
        function (img) {
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