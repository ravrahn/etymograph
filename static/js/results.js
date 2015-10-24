for (var i=0; i < words.length; i++) {
	var word = words[i];

	var g = new dagreD3.graphlib.Graph()
	    .setGraph({
	        nodesep: 70,
	        ranksep: 50,
	        rankdir: "LR",
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

	var render = new dagreD3.render();

    var svg = d3.select('#graph-' + word.id),
        svgGroup = svg.append("g");

    render(d3.select('#graph-' + word.id + " g"), g);
}