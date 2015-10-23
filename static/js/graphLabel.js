function makeLabel(word) {
    return hiddenInfo(word)+'<div class="node-container"><span class="node-lang-name">' + word.lang_name + '</span><span class="node-flags">' + word.flag_count + ' flag' + (word.flag_count === 1 ? '' : 's') + '</span><a class="node-label" href="/'+word.id+'">' + word.orig_form + '</a><div style="clear: none;"></div></div>';
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