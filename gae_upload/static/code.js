function $new(tagName, attrs) {
  return jQuery(document.createElement(tagName)).attr(attrs || {});
}

var Hagglebot = {};

Hagglebot.ajaxError = function (xhr, textStatus) {
  alert(textStatus + ': ' + xhr.status + ': ' + xhr.responseText); // TODO
}

Hagglebot.ajaxSubmit = function (form, fn) {
  var action = form.attr('action'), method = form.attr('method');

  jQuery.ajax({
    url: action
  , type: method
  , data: form.serialize()
  , dataType: 'json'
  , error: Hagglebot.ajaxError
  , success: fn
  });
}

Hagglebot.ajaxGetOffer = function (url, fn) {
  jQuery.ajax({url: url, dataType: 'html', error: Hagglebot.ajaxError, success: fn});
}

Hagglebot.labelText = function (node) {
  if (node.nodeType == 1) { /* ELEMENT_NODE */
    if (node.childNodes.length == 0) {
      return jQuery(node).val();
    } else {
      var values = jQuery.map(node.childNodes, Hagglebot.labelText);

      return values.join('');
    }
  } else { /* Assume TEXT_NODE */
    return node.nodeValue;
  }
}

Hagglebot.LabelingUI = function (form, fn) {
  var start = new Date();

  var submitted = false;

  var input = form.find('input[type=text]');

  form.find('input[type=button]').click(function () {
    var value = jQuery.trim(input.val());

    if (value.length > 0) {
      input.addClass('block');

      input = $new('input', {'type': 'text', 'name': 'label'}).insertAfter(input);
    }
  });

  form.submit(function () {
    if (!submitted) {
      submitted = true;

      form.find(':submit').attr('disabled', true);

      form.find('input[name=time]').val(new Date() - start);

      fn(form);
    }

    return false;
  });
}

Hagglebot.Negotiation = function (url, chatWindow) {
  var self = this;

  this.chatWindow = chatWindow;

  this.chatMessages = chatWindow.find('.messages');

  this.chatControls = chatWindow.find('.controls');

  this.chatWindow.slideDown('slow');

  Hagglebot.ajaxGetOffer(url, function (data, _textStatus, _xhr) {
    self.handleOffer(jQuery(data));
  });
}

Hagglebot.Negotiation.prototype.handleOffer = function (response) {
  var self = this;

  var form = response.find('form');

  var submitted = false;

  form.submit(function () {
    if (!submitted) {
      submitted = true;

      self.handleSubmit(form);
    }

    return false;
  });

  this.chatMessages.append(response.find('p'));

  this.chatControls.fadeOut(function () {
    self.chatControls.html(form);

    self.chatControls.fadeIn();
  });
}

Hagglebot.Negotiation.prototype.handleSubmit = function (form) {
  var self = this;

  var input = form.find('input[type=radio]:checked');

  var label = form.find('label[for=' + input.attr('id') + ']').closest('span').get(0);

  form.find(':submit').attr('disabled', true);

  self.chatMessages.append($new('p').text(Hagglebot.labelText(label)));

  Hagglebot.ajaxSubmit(form, function (replyData, _textStatus, _xhr) {
    if (replyData.redirect) {
      window.location.href = replyData.redirect;
    } else if (replyData.message) {
      Hagglebot.ajaxGetOffer(replyData.message, function (offerData, _textStatus, _xhr) {
        self.handleOffer(jQuery(offerData));
      });
    } else {
      // TODO: error
    }
  });
}
