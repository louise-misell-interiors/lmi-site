function nextSlide(slider) {
    const $slide = slider.find(".slide.is-active");
    let $nextSlide = $slide.next(".slide");

    if ($nextSlide.length === 0) {
        $nextSlide = slider.find(".slide:first");
    }

    $slide.removeClass("is-active");
    $nextSlide.addClass("is-active");
}

function prevSlide(slider) {
    const $slide = slider.find(".slide.is-active");
    let $prevSlide = $slide.prev(".slide");

    if ($prevSlide.length === 0) {
        $prevSlide = slider.find(".slide:last");
    }

    $slide.removeClass("is-active");
    $prevSlide.addClass("is-active");
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
    const $menuLeft = $menu.find(".nav-left");
    const $menuRight = $menu.find(".nav-right");

    $menuButton.on("click", function () {
        $menu.toggleClass("show-menu");
        let top = $menuLeft.outerHeight();
        $menuRight.css("top", top);
        $menuButton.toggleClass("fa-bars");
        $menuButton.toggleClass("fa-times");
    });
});