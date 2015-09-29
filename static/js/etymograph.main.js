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

  // Hide the title when typing in the search field
  /*
  $("#search_field").on('mouseenter', function(e){
    if (e.which == 13) {
      //Move the search bar up to the top
    }
    $("#title").slideUp('slow');
  });

  // Bring back the title that was hidden away by clicking elsewhere.
  $(document).click(function(e) {
    var target = e.target;
    if (!$(target).is('#search_field')
      && !$(target).parents().is('#search_field')
      && !$(target).is('.tt-menu')) {
      $('#title').slideDown('slow');
    }
  });
  */

  // Because Jinja2 does not make this easy
  $("#search_field").attr("placeholder", "Look up the origins of a word...");

  // Submitting search field contents
  /*
  $(function() {
    $('#search_field').keypress(function(e) {
      if (e.which == 13) {
        $.getJSON($SCRIPT_ROOT + '/search', {
          q: $("input[name='q']").val()
        }, function(data) {
          $("#result").text(data.result);
        });
        return false;
      }
    });
  });

  //Won't work under the same-origin policy while using localhost
  var word = "besi"
  $.ajax({
    type: "GET",
    url: "/search?q=",
    data: word
  }).done(function(response) {
    //Do something with the response.
    console.log(response);
  });
  */


  /*
  var words = new Bloodhound({
      datumTokenizer: function (datum) {
          return Bloodhound.tokenizers.whitespace(datum.value);
      },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: 'localhost:5000/search?q=%QUERY',
        wildcard: '%QUERY'
      }
  });
  words.initialize();
  */


  // Tags is just an example to get the autocomplete working.
  // Tags will technically need a function to populate it with results from a cypher query, see above
  var tags = [
  "ActionScript",
  "AppleScript",
  "Asp",
  "BASIC",
  "C",
  "C++",
  "Clojure",
  "COBOL",
  "ColdFusion",
  "Erlang",
  "Fortran",
  "Groovy",
  "Haskell",
  "Java",
  "JavaScript",
  "Lisp",
  "Perl",
  "PHP",
  "Python",
  "Ruby",
  "Scala",
  "Scheme"
  ];

  // For bloodhound engine, doesn't work yet.
  /*
     $('.typeahead').typeahead(null, {
     displayKey: 'value',
     source: words.ttAdapter()
     });
  */

  $("#search_field").typeahead({
    hint: false,
    highlight: true,
    minLength: 3
  },
  {
    name: 'tags',
    source: substringMatcher(tags)
  });

});
