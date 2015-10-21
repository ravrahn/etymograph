function makeLabel(word) {
    return hiddenInfo(word)+'<div class="lang-name">' + word.lang_name + '</div><div><a href="/'+word.id+'">' + word.orig_form + '</a></div>';
}

function hiddenInfo(word){
    var info = '<div class="data"';
    info += 'id='+word.id+' ';
    info += 'data-orig_form="'+word.orig_form+'" ';

    if(word.eng_form !== undefined){
        info += 'data-eng_form="'+word.eng_form+'" ';
    }
    if(word.lang_name !== undefined){
        info += 'data-lang_name="'+word.lang_name+'" ';
    }
    if(word.ipa_form !== undefined){
        info += 'data-ipa_form="'+word.ipa_form+'" ';
    }
    if(word.definition !== undefined){
        info += 'data-definition="'+word.definition+'" ';
    }
    info +='></div>';
    return info;
}

function makeEdgeLabel(rootID, descID) {
    if(loggedIn) {
        return '<a href="/edit/rel/'+rootID+'/'+descID+'">more...</a>';
    } else {
        return "";
    }
}

function addRoot(g, root, parent) {
    var rootLabel = makeLabel(root);
    g.setNode(root.id, { id: root.id, labelType:'html', label: rootLabel, class: 'word' });
    var edgeLabel = makeEdgeLabel(root.id, parent);
    g.setEdge(root.id, parent, { lineInterpolate: "bundle", labelType:'html', label: edgeLabel });
    if (root.roots !== undefined) {
        root.roots.forEach(function(r) { addRoot(g, r, root.id) });
    }

}

function addDesc(g, desc, parent) {
    var descLabel = makeLabel(desc);
    g.setNode(desc.id, { id: desc.id, labelType:'html', label: descLabel, class: 'word' });
    var edgeLabel = makeEdgeLabel(parent, desc.id);
    g.setEdge(parent, desc.id, { lineInterpolate: "bundle", labelType:'html', label: edgeLabel });
    if (desc.descs !== undefined) {
        desc.descs.forEach(function(d) { addDesc(g, d, desc.id) });
    }
}

function makeGraph(roots, descs, form) {
    var origin = roots;

    // convert roots and descs into a single dagre graph
    var g = new dagreD3.graphlib.Graph()
        .setGraph({
            nodesep: 70,
            ranksep: 50,
            rankdir: "LR",
            marginx: 20,
            marginy: 20
        })
        .setDefaultEdgeLabel(function() { return {}; });;

    g.setNode(origin.id, { id: origin.id, labelType:'html', label: makeLabel(origin),  class: 'origin word' });

    roots.roots.forEach(function(r) { addRoot(g, r, origin.id) });
    descs.descs.forEach(function(d) { addDesc(g, d, origin.id) });

    if (loggedIn) {
        g.setNode('add_root', { id: 'add_root', labelType: 'html', label: '+ Add Root', class: 'add add-root' });
        g.setEdge('add_root', origin.id, { lineInterpolate: "bundle", class: 'add-edge' });

        g.setNode('add_desc', { id: 'add_desc', labelType: 'html', label: '+ Add Descendant', class: 'add add-desc' });
        g.setEdge(origin.id, 'add_desc', { lineInterpolate: "bundle", class: 'add-edge' });
    }
    // Draw the graph
    // Create the renderer
    var render = new dagreD3.render();

    // Set up an SVG group so that we can translate the final graph.
    var svg = d3.select("svg"),
        svgGroup = svg.append("g");

    // Run the renderer. This is what draws the final graph.
    render(d3.select("svg g"), g);

    $("g.word").click(function() {
        if ($('.selected').length !== 0) {
            $(".selected").attr("class", $(".selected").attr("class").replace('selected', ''));
        }
        $( this ).attr("class", "selected " + $(this).attr("class"));
        // Get data from the graph node
        var id = $( this ).attr("id");
        var orig_form = $("div#"+ id +".data").attr("data-orig_form");
        var eng_form = $("div#"+ id +".data").attr("data-eng_form");
        var lang_name = $("div#"+ id +".data").attr("data-lang_name");
        var ipa_form = $("div#"+ id +".data").attr("data-ipa_form");
        var definition = $("div#"+id+".data").attr("data-definition");
        // Construct the html to go inside the info sidebar
        var info = "<h2>" + orig_form + '</h2>';
        if (eng_form !== undefined){
            info += "<p> English Transliteration: " + eng_form + '</p>';
        }
        if (ipa_form !== undefined){
            info += "<p> Pronounciation: " + ipa_form + '</p>';
        }
        if (lang_name !== undefined){
            info += "<p> Language: "+ lang_name + '</p>';
        }
        if (definition !== undefined){
            info += "<p> Definition: "+ definition + '</p>';
        }
        info += '<a href="/flag/' + id + '">Flag this as incorrect?</a>';
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

    // Resize the top div container for this graph
    var gtag, gh, vw, pad;
    gtag = $('g');
    gh = gtag[0].getBBox().height;
    gw = gtag[0].getBBox().width;
    pad = 30; //gh and gw are actually less than what is reported in developer tools so we pad them.
    gh += pad;
    gw += pad;
    $('.flex-content').height(gh);
    $('.flex-content').width(gw);
}
