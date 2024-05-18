/*!

=========================================================
* Black Dashboard Pro - v1.1.1
=========================================================

* Product Page: https://themes.getbootstrap.com/product/black-dashboard-pro-premium-bootstrap-4-admin/
* Copyright 2019 Creative Tim (https://www.creative-tim.com)
* Coded by Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/

"use strict";
var transparent = !0, transparentDemo = !0, fixedTop = !1, navbar_initialized = !1, backgroundOrange = !1,
    sidebar_mini_active = !1, toggle_initialized = !1, $html = $("html"), $body = $("body"),
    $navbar_minimize_fixed = $(".navbar-minimize-fixed"), $collapse = $(".collapse"), $navbar = $(".navbar"),
    $tagsinput = $(".tagsinput"), $selectpicker = $(".selectpicker"), $navbar_color = $(".navbar[color-on-scroll]"),
    $full_screen_map = $(".full-screen-map"), $datetimepicker = $(".datetimepicker"), $datepicker = $(".datepicker"),
    $timepicker = $(".timepicker"), seq = 0, delays = 80, durations = 500, seq2 = 0, delays2 = 80, durations2 = 500;

function debounce(a, e, i) {
    var n;
    return function () {
        var t = this, o = arguments;
        clearTimeout(n), n = setTimeout(function () {
            n = null, i || a.apply(t, o)
        }, e), i && !n && a.apply(t, o)
    }
}

!function () {
    if (navigator.platform.indexOf("Win") > -1) {
        if (0 != $(".main-panel").length) new PerfectScrollbar(".main-panel", {
            wheelSpeed: 2, wheelPropagation: !0, minScrollbarLength: 20, suppressScrollX: !0
        });
        if (0 != $(".sidebar .sidebar-wrapper").length) {
            new PerfectScrollbar(".sidebar .sidebar-wrapper");
            $(".table-responsive").each(function () {
                new PerfectScrollbar($(this)[0])
            })
        }
        $html.addClass("perfect-scrollbar-on")
    } else $html.addClass("perfect-scrollbar-off")
}(), $(document).ready(function () {
    $(".row").offset();
    (navigator.platform.indexOf("Win") > -1 ? $(".ps") : $(window)).scroll(function () {
        $(this).scrollTop() > 50 ? $navbar_minimize_fixed.css("opacity", "1") : $navbar_minimize_fixed.css("opacity", "0")
    }), $collapse.on("show.bs.collapse", function () {
        $(this).parent().siblings().children(".collapse").each(function () {
            $(this).collapse("hide")
        })
    }), $('[data-toggle="tooltip"], [rel="tooltip"]').tooltip(), $('[data-toggle="popover"]').each(function () {
        color_class = $(this).data("color"), $(this).popover({template: '<div class="popover popover-' + color_class + '" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'})
    });
    var a = $tagsinput.data("color");
    0 != $tagsinput.length && $tagsinput.tagsinput(), $(".bootstrap-tagsinput").find(".tag").addClass("badge-" + a), 0 != $selectpicker.length && $selectpicker.selectpicker({
        iconBase: "tim-icons", tickIcon: "icon-check-2"
    }), $("#search-button").click(function () {
        $(this).closest(".navbar-collapse").removeClass("show"), $navbar.addClass("navbar-transparent").removeClass("bg-white")
    }), blackDashboard.initMinimizeSidebar();
    $navbar_color.attr("color-on-scroll");
    0 != $navbar_color.length && (blackDashboard.checkScrollForTransparentNavbar(), $(window).on("scroll", blackDashboard.checkScrollForTransparentNavbar)), 0 == $full_screen_map.length && 0 == $(".bd-docs").length && $(".navbar-toggler").click(function () {
        $collapse.on("show.bs.collapse", function () {
            $(this).closest(".navbar").removeClass("navbar-transparent").addClass("bg-white")
        }).on("hide.bs.collapse", function () {
            $(this).closest(".navbar").addClass("navbar-transparent").removeClass("bg-white")
        }), $navbar.css("transition", "")
    }), $navbar.css({top: "0", transition: "all .5s linear"}), $(".form-control").on("focus", function () {
        $(this).parent(".input-group").addClass("input-group-focus")
    }).on("blur", function () {
        $(this).parent(".input-group").removeClass("input-group-focus")
    }), $(".bootstrap-switch").each(function () {
        var a = $(this).data("on-label") || "", e = $(this).data("off-label") || "";
        $(this).bootstrapSwitch({onText: a, offText: e})
    })
}), $(document).on("click", ".navbar-toggle", function () {
    var a = $(this);
    if (1 == blackDashboard.misc.navbar_menu_visible) $html.removeClass("nav-open"), blackDashboard.misc.navbar_menu_visible = 0, setTimeout(function () {
        a.removeClass("toggled"), $(".bodyClick").remove()
    }, 550); else {
        setTimeout(function () {
            a.addClass("toggled")
        }, 580);
        $('<div class="bodyClick"></div>').appendTo("body").click(function () {
            $html.removeClass("nav-open"), blackDashboard.misc.navbar_menu_visible = 0, setTimeout(function () {
                a.removeClass("toggled"), $(".bodyClick").remove()
            }, 550)
        }), $html.addClass("nav-open"), blackDashboard.misc.navbar_menu_visible = 1
    }
}), $(window).resize(function () {
    if (seq = seq2 = 0, 0 == $full_screen_map.length && 0 == $(".bd-docs").length) {
        var a = $navbar.find('[data-toggle="collapse"]').attr("aria-expanded");
        $navbar.hasClass("bg-white") && $(window).width() > 991 ? $navbar.removeClass("bg-white").addClass("navbar-transparent") : $navbar.hasClass("navbar-transparent") && $(window).width() < 991 && "false" != a && $navbar.addClass("bg-white").removeClass("navbar-transparent")
    }
});
var blackDashboard = {
    misc: {navbar_menu_visible: 0}, checkScrollForTransparentNavbar: debounce(function () {
        $(document).scrollTop() > scroll_distance ? transparent && (transparent = !1, $navbar_color.removeClass("navbar-transparent")) : transparent || (transparent = !0, $navbar_color.addClass("navbar-transparent"))
    }, 17), initDateTimePicker: function () {
        0 != $datetimepicker.length && $datetimepicker.datetimepicker({
            icons: {
                time: "tim-icons icon-watch-time",
                date: "tim-icons icon-calendar-60",
                up: "fa fa-chevron-up",
                down: "fa fa-chevron-down",
                previous: "tim-icons icon-minimal-left",
                next: "tim-icons icon-minimal-right",
                today: "fa fa-screenshot",
                clear: "fa fa-trash",
                close: "fa fa-remove"
            }
        }), 0 != $datepicker.length && $datepicker.datetimepicker({
            format: "MM/DD/YYYY", icons: {
                time: "tim-icons icon-watch-time",
                date: "tim-icons icon-calendar-60",
                up: "fa fa-chevron-up",
                down: "fa fa-chevron-down",
                previous: "tim-icons icon-minimal-left",
                next: "tim-icons icon-minimal-right",
                today: "fa fa-screenshot",
                clear: "fa fa-trash",
                close: "fa fa-remove"
            }
        }), 0 != $timepicker.length && $timepicker.datetimepicker({
            format: "h:mm A", icons: {
                time: "tim-icons icon-watch-time",
                date: "tim-icons icon-calendar-60",
                up: "fa fa-chevron-up",
                down: "fa fa-chevron-down",
                previous: "tim-icons icon-minimal-left",
                next: "tim-icons icon-minimal-right",
                today: "fa fa-screenshot",
                clear: "fa fa-trash",
                close: "fa fa-remove"
            }
        })
    }, initMinimizeSidebar: function () {
        0 != $(".sidebar-mini").length && (sidebar_mini_active = !0),
            $(".minimize-sidebar").click(function () {
                1 == sidebar_mini_active ? ($body.removeClass("sidebar-mini"),
                    sidebar_mini_active = !1,
                    blackDashboard) : ($body.addClass("sidebar-mini"),
                    sidebar_mini_active = !0,
                    blackDashboard);
                var a = setInterval(function () {
                    window.dispatchEvent(new Event("resize"))
                }, 180);
                setTimeout(function () {
                    clearInterval(a)
                }, 1e3)
            })
    }, startAnimationForLineChart: function (a) {
        a.on("draw", function (a) {
            "line" === a.type || "area" === a.type ? a.element.animate({
                d: {
                    begin: 600,
                    dur: 700,
                    from: a.path.clone().scale(1, 0).translate(0, a.chartRect.height()).stringify(),
                    to: a.path.clone().stringify(),
                    easing: Chartist.Svg.Easing.easeOutQuint
                }
            }) : "point" === a.type && (seq++, a.element.animate({
                opacity: {
                    begin: seq * delays, dur: durations, from: 0, to: 1, easing: "ease"
                }
            }))
        }), seq = 0
    }, startAnimationForBarChart: function (a) {
        a.on("draw", function (a) {
            "bar" === a.type && (seq2++, a.element.animate({
                opacity: {
                    begin: seq2 * delays2, dur: durations2, from: 0, to: 1, easing: "ease"
                }
            }))
        }), seq2 = 0
    }, showSidebarMessage: function (a) {
        try {
            $.notify({icon: "tim-icons icon-bell-55", message: a}, {
                type: "primary", timer: 4e3, placement: {from: "top", align: "right"}
            })
        } catch (a) {
            console.log("Notify library is missing, please make sure you have the notifications library added.")
        }
    }
};

function hexToRGB(a, e) {
    var i = parseInt(a.slice(1, 3), 16), n = parseInt(a.slice(3, 5), 16), t = parseInt(a.slice(5, 7), 16);
    return e ? "rgba(" + i + ", " + n + ", " + t + ", " + e + ")" : "rgb(" + i + ", " + n + ", " + t + ")"
}
