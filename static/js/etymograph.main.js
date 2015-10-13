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

/* start jQuery */
$(document).ready(function(){
  // Because Jinja2 does not make this easy
  $("#search_field").attr("placeholder", "Look up the origins of a word...");

  // Start Bloodhound search engine
  var words = new Bloodhound({
      datumTokenizer: function (datum) {
			console.log(datum.value);
          return Bloodhound.tokenizers.whitespace(datum.value);
      },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: '/search?q=^%QUERY',
        wildcard: '%QUERY'
      },
      sorter: function(itemA, itemB) {
		console.log(itemA);
		console.log(itemB);
      }
  });
  words.initialize();

  // Set options for typehead and for which form it is attached
  $("#search_field").typeahead({
	  hint: false,
	  highlight: true,
	  minLength: 3,
  },
  {
	  name: 'words',
	  displayKey: 'orig_form',
      source: words.ttAdapter(),
	  limit: 5
  });
});
