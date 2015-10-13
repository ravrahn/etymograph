var substringMatcher = function(strs) {
  return function findMatches(q, cb) {
    var matches, substringRegex;
    matches = [];
    substrRegex = new RegExp('^' + q, 'i');
    $.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
        matches.push(str);
      }
    });
    cb(matches);
  };
};

// jQuery

$(document).ready(function(){

  // Because Jinja2 does not make this easy
  $("#search_field").attr("placeholder", "Look up the origins of a word...");

  var words = new Bloodhound({
      datumTokenizer: function (datum) {
          return Bloodhound.tokenizers.whitespace(datum.value);
      },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: '/search?q=%QUERY',
        wildcard: '%QUERY'
      }
  });

  words.initialize();

  $("#search_field").typeahead({
	  hint: false,
	  highlight: true,
	  minLength: 3,
  },
  {
	  name: 'words',
	  displayKey: 'orig_form',
	  source: words,
	  limit: 5
  });

});
