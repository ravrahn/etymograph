var rootResults = {}

function makeWordList(words, isRoot) {
    var html = '<ul>'
    for (var i=0; i < words.length; i++) {
        html += '<li><svg id="graph-' + words[i].id + '" width="116" height="46"></svg></li>'
    }
    html += '</ul>'
    $('.results-container').html(html);
    for (var i=0; i < words.length; i++) {
    	var word = words[i];
        rootResults[word.id] = word;

    	var g = new dagreD3.graphlib.Graph()
    	    .setGraph({
    	        nodesep: 70,
    	        ranksep: 50,
    	        marginx: 2,
    	        marginy: 2
    	    })
    	    .setDefaultEdgeLabel(function() { return {}; });

        g.setNode(word.id, {
            id: word.id,
            labelType:'html',
            label: makeLabel(word),
            padding: 0,
            class: 'word' 
        });

        g.nodes().forEach(function(v) {
          var node = g.node(v);
          // Round the corners of the nodes
          node.rx = node.ry = 5;
        });

    	var render = new dagreD3.render();

        var svg = d3.select('#graph-' + word.id),
            svgGroup = svg.append("g");

        render(d3.select('#graph-' + word.id + " g"), g);

        $('#graph-' + word.id + ' .node').click(function() {
            var word = rootResults[$(this).attr('id')]
            console.log(word, $(this).attr('id'));
            buildGraph(word, isRoot);
        });
    }
}