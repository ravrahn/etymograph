/* start jQuery */
$(document).ready(function(){
  // Because Jinja2 does not make this easy
  $("#search_field").attr("placeholder", "Look up the origins of a word...");
  $("#upleft-search").attr("placeholder", "Look up the origins of a word...");

  // Start Bloodhound search engine
  var words = new Bloodhound({
      datumTokenizer: function (datum) {
          return Bloodhound.tokenizers.whitespace(datum.value);
      },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: '/search?q=^%QUERY',
        wildcard: '%QUERY'
      },
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

  /*
   Steal highlight back; workaround for latest typeahead highlight issue
   between .tt-suggestion and .tt-cursor. Without this, both highlighting (from
   keyboard and from mouse) can coexist.

   DOESN'T WORK WHEN KEYBOARD STEALS FOCUS, APPARENTLY
  */
  $('.twitter-typeahead')
   .on('mouseenter', '.tt-suggestion', function(e){
      $('.tt-cursor', $(this).closest('.tt-menu')).removeClass('tt-cursor');
      $(this).addClass('tt-cursor');
   })
   .on('mouseleave', '.tt-menu', function(e){
      $('.tt-cursor', $(this).closest('.tt-menu')).removeClass('tt-cursor');
   });
});
