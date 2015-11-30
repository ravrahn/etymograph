for (var i=0; i < rels.length; i++) {
	var root = rels[i].root;
	var desc = rels[i].desc;

	var g = new dagreD3.graphlib.Graph()
	    .setGraph({
	        nodesep: 70,
	        ranksep: 50,
	        rankdir: "LR",
	        marginx: 2,
	        marginy: 2
	    })
	    .setDefaultEdgeLabel(function() { return {}; });

    g.setNode(root.id, {
        id: root.id,
        labelType:'html',
        label: makeLinkLabel(root),
        padding: 0,
        class: 'word' 
    });

    g.setNode(desc.id, {
        id: desc.id,
        labelType:'html',
        label: makeLinkLabel(desc),
        padding: 0,
        class: 'word' 
    });

    g.setEdge(root.id, desc.id, {
        labelType:'html',
        label: rels[i].flag_count + ' flag' + (rels[i].flag_count === 1 ? '' : 's')
    });

    g.nodes().forEach(function(v) {
      var node = g.node(v);
      // Round the corners of the nodes
      node.rx = node.ry = 5;
    });

	var render = new dagreD3.render();

    var svg = d3.select('#graph-' + root.id + '-' + desc.id),
        svgGroup = svg.append("g");

    render(d3.select('#graph-' + root.id + '-' + desc.id + " g"), g);
}
