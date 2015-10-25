function makeEdgeLabel(rootID, descID) {
    if(loggedIn) {
        return '<a href="/edit/rel/'+rootID+'/'+descID+'">more...</a>';
    } else {
        return "";
    }
}

var nodes = {};
var fields = {
    'lang_name': 'Language',
    'definition': 'Definition',
    'ipa_form': 'IPA Transcription',
    'eng_form': 'Latin Transliteration'
};

function addRoot(g, root, parent) {
    var rootLabel = makeLabel(root);
    g.setNode(root.id, {
        id: root.id,
        labelType:'html',
        label: rootLabel,
        padding: 0,
        class: 'word'
    });
    nodes[root.id] = root;

    var edgeLabel = makeEdgeLabel(root.id, parent);
    g.setEdge(root.id, parent, {
        labelType:'html',
        label: edgeLabel,
        lineInterpolate: 'basis'
    });
    if (root.roots !== undefined) {
        root.roots.forEach(function(r) { addRoot(g, r, root.id) });
    }

}

function addDesc(g, desc, parent) {
    var descLabel = makeLabel(desc);
    g.setNode(desc.id, { id:
        desc.id,
        labelType:'html',
        label: descLabel,
        padding: 0,
        class: 'word'
    });
    nodes[desc.id] = desc;

    var edgeLabel = makeEdgeLabel(parent, desc.id);
    g.setEdge(parent, desc.id, {
        labelType:'html',
        label: edgeLabel,
        lineInterpolate: 'basis'
    });
    if (desc.descs !== undefined) {
        desc.descs.forEach(function(d) { addDesc(g, d, desc.id) });
    }
}
var origin = roots;

// convert roots and descs into a single dagre graph
var g = new dagreD3.graphlib.Graph()
    .setGraph({
        nodesep: 30,
        ranksep: 50,
        rankdir: "LR",
        marginx: 40,
        marginy: 80
    })
    .setDefaultEdgeLabel(function() { return {}; });

g.setNode(origin.id, {
    id: origin.id,
    labelType:'html',
    label: makeLabel(origin),
    padding: 0,
    class: 'origin word' 
});
nodes[origin.id] = origin;

roots.roots.forEach(function(r) { addRoot(g, r, origin.id) });
descs.descs.forEach(function(d) { addDesc(g, d, origin.id) });

if (loggedIn) {
    g.setNode('add_root', {
        id: 'add_root',
        labelType: 'html',
        label: '<div class="add-node">+ Add</div>',
        padding: 0,
        class: 'add add-root'
    });
    g.setEdge('add_root', origin.id, {
        lineInterpolate: 'basis',
        class: 'add-edge'
    });

    g.setNode('add_desc', {
        id: 'add_desc',
        labelType: 'html',
        label: '<div class="add-node">+ Add</div>',
        padding: 0,
        class: 'add add-desc'
    });
    g.setEdge(origin.id, 'add_desc', {
        lineInterpolate: 'basis',
        class: 'add-edge'
    });
}

g.nodes().forEach(function(v) {
  var node = g.node(v);
  // Round the corners of the nodes
  node.rx = node.ry = 5;
});

// Draw the graph
// Create the renderer
var render = new dagreD3.render();

// Set up an SVG group so that we can translate the final graph.
var svg = d3.select("svg"),
    inner = svg.append("g"),
    innerX = 0,
    innerY = 0;
// Set up click-and-drag

function translateGraph(dx, dy, e) {
    var leftBound = 0;
    var rightBound = $('svg').width() - $('.infobar').width() - $('g')[0].getBBox().width - 40;
    var topBound = 0;
    var bottomBound = $('svg').height() - $('g')[0].getBBox().height - 80;
    if (leftBound > rightBound) {
        if (innerX + dx > leftBound) {
            innerX = leftBound;
        } else if (innerX + dx < rightBound) {
            innerX = rightBound;
        } else {
            innerX += dx;
        }
    }
    if (topBound > bottomBound) {
        if (innerY + dy > topBound) {
            innerY = topBound;
        } else if (innerY + dy < bottomBound) {
            innerY = bottomBound;
        } else {
            innerY += dy;
        }
    }
    if (e !== null) {
        var smaller = (topBound < bottomBound && leftBound < rightBound);
        if (!smaller) {
            e.preventDefault();
        }
    }
    inner.attr("transform", "translate(" + [ innerX,innerY ] + ")");
}

var drag = d3.behavior.drag().on("drag", function() {
        translateGraph(d3.event.dx, d3.event.dy, null);
    });
svg.call(drag);

// Run the renderer. This is what draws the final graph.
render(inner, g);

$("g.word").click(function() {
    if ($('.selected').length !== 0) {
        $(".selected").attr("class", $(".selected").attr("class").replace('selected', ''));
    }
    $( this ).attr("class", "selected " + $(this).attr("class"));
    // Get data from the graph node
    var id = $(this).attr("id");
    var node = nodes[id];
    // Construct the html to go inside the info sidebar
    var info = "<h2><a href='/" + id + "'>" + node.orig_form + '</a></h2>';
    info += '<h3>' + node.lang_name + '</h3>';
    if ('definition' in node) {
        info += '<p>' + node.definition + '</p>';
    }
    if ('eng_form' in node && node.eng_form !== ''){
        info += "<h4>" + fields.eng_form + ":</h4> <div class='latin'>" + node.eng_form + '</div>';
    }
    if ('ipa_form' in node && node.ipa_form !== ''){
        info += "<h4>" + fields.ipa_form + ":</h4> <div class='ipa'>/" + node.ipa_form + '/</div>';
    }
    if (loggedIn) {
        info += '<div class="flag"> <form method="POST" action="flag/' + id + '?next=' + next_url + '"><button type="submit" value="flag">Flag as incorrect</button></form> - <span class="flag-count">' + node.flag_count + '</span> flags</div>';
    }
    $(".infobar").html(info);
});

if (loggedIn) {
    $('g.add-root').click(function() {
        // search, somehow
        var id = 7892; // in lieu of search
        $('body').append(form);
        $('form.add-root #word_id').val(origin.id);
        $('form.add-root #root_id').val(id);
        // data = { 'word_id': origin.id, 'root_id': id, 'source': source }
        // $.post('{{ url_for("add_root") }}', data, function() {
        //     location.reload()
        // });
    });
    $('g.add-desc').click(function() {
        // search, somehow
        var id = 7891; // in lieu of search
        $('body').append(form);
        $('form.add-root #word_id').val(id);
        $('form.add-root #root_id').val(origin.id);
        // data = { 'word_id': id, 'root_id': origin.id, 'source': source }
        // $.post('{{ url_for("add_root") }}', data, function() {
        //     location.reload()
        // });
    });
}

$('.origin').click();

$('svg').mousewheel(function(e) {
    translateGraph(-e.deltaX/e.deltaFactor, e.deltaY/e.deltaFactor, e);
});

// // Resize the top div container for this graph
// var gtag = $('g'),
//     gh = gtag[0].getBBox().height + 30; //gh is actually less than what is reported in developer tools so we pad them.
// $('.flex-content').height(gh);
