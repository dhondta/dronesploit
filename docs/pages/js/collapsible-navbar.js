String.prototype.format = function() {
  a = this;
  for (k in arguments) {
    a = a.replace("{" + k + "}", arguments[k])
  }
  return a
}

$(document).ready(function () {
  $('li.toctree-l1').each(function () {
    var parent  = $(this);
    var span    = parent.find('span:first');
    var sibling = null;
    var remove  = true;
    $('li.toctree-l1').each(function() {
      var a = $(this).find('a:first');
      if (a.text() != '' && a.text() == span.text()) {
        parent.prepend(a);
        span.remove();
        span = a;
        if ($(this).hasClass('current')) parent.addClass('current');
        sibling = $(this);
        return false
      }
    });
    if (sibling === null && parent.find('ul.subnav:not(li.toctree-l2)').children('li').length) {
      sibling = parent;
      remove  = false;
    }
    if (sibling !== null) {
      var ul = parent.find('ul.subnav:not(li.toctree-l2)');
      var new_a = '<a class="fa fa-caret-{0} collapse-navbar" href="#" style="display: inline-block; position: absolute; width: auto; right: 0; margin-right: 2px; padding-left: 2px; padding-right: 2px; z-index: 1001;"></a>';
      if (!ul.children('li.current').length && !parent.hasClass('current')) {
        ul.hide();
        $(new_a.format("left")).insertBefore(span);
      } else {
        $(new_a.format("down")).insertBefore(span);
      }
      if (remove) sibling.remove();
    }
  });
  $('a.collapse-navbar').click(function () {
    var parent = $(this).closest('li.toctree-l1');
    var subnav = parent.find('ul.subnav:not(li.toctree-l2)');
    if ($(this).hasClass('fa-caret-left')) {
      subnav.show();
      $(this).removeClass('fa-caret-left');
      $(this).addClass('fa-caret-down');
    } else {
      subnav.hide();
      $(this).addClass('fa-caret-left');
      $(this).removeClass('fa-caret-down');
    }
});});
