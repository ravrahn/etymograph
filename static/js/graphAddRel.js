var rootResults = {}

function makeWordList(words, isRoot) {
    var html = '<ul>'
    for (var i=0; i < words.length; i++) {
        word = words[i];
        html += '<li><div class="node-html add-rel-node" id="' + word.id + '"><div class="node-container"><span class="node-lang-name">' + word.lang_name +
        '</span><span class="node-label">' + word.orig_form +
        '</span><div style="clear: none;"></div></div></div></li>';
        rootResults[word.id] = word;
    }
    html += '</ul>'
    $('.results-container').html(html);

    $('.add-rel-node').click(function() {
        var word = rootResults[$(this).attr('id')]
        buildGraph(word, isRoot);
    });

}