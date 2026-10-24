// Mobile menu and the before/after slider.
(function () {
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("site-nav");
  if (btn && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("open", open);
      document.body.classList.toggle("menu-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    };
    btn.addEventListener("click", function () { setOpen(!nav.classList.contains("open")); });
    // Close after choosing a link, on Escape, or when the screen grows past the menu breakpoint.
    nav.addEventListener("click", function (ev) { if (ev.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && nav.classList.contains("open")) { setOpen(false); btn.focus(); }
    });
    window.matchMedia("(min-width: 1061px)").addEventListener("change", function (mq) { if (mq.matches) setOpen(false); });
  }

  document.querySelectorAll(".compare").forEach(function (box) {
    var range = box.querySelector(".compare-range");
    var set = function (v) { box.style.setProperty("--pos", v + "%"); };
    var touched = false;
    range.addEventListener("input", function () { touched = true; set(range.value); });
    set(range.value);

    // On load, sweep once from "before" to the middle so visitors see it move.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var from = 94, to = Number(range.value), dur = 1600, t0 = null;
    var ease = function (x) { return 1 - Math.pow(1 - x, 3); };
    var step = function (now) {
      if (touched) return;
      if (t0 === null) t0 = now;
      var k = Math.min(1, (now - t0) / dur);
      set(from + (to - from) * ease(k));
      if (k < 1) requestAnimationFrame(step);
    };
    set(from);
    setTimeout(function () { requestAnimationFrame(step); }, 450);
  });
})();
