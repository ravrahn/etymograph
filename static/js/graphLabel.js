function makeLabel(word) {
    return '<div class="node-container"><span class="node-lang-name">' + word.lang_name + '</span><span class="node-label">' + word.orig_form + '</span><div style="clear: none;"></div></div>';
}

function makeLinkLabel(word) {
	return '<a href="/' + word.id + '"><div class="node-container"><span class="node-lang-name">' + word.lang_name + '</span><span class="node-label">' + word.orig_form + '</span><div style="clear: none;"></div></div></a>';
}
