word = '';
document.getElementById('input-search').addEventListener('keydown', function (value) {
    console.log(value.key);
    if (value.key == 'Backspace') {
        word = word.slice(0, -1);
    } else if (value.key == 'Control' || value.key == 'Alt' || value.key == 'Enter'
        || value.key == 'Shift' || value.key == 'Delete') {
    } else {
        word = word + value.key;
    }
    console.log(word);
    $.getJSON(`./street_search/?streetPattern=${word}`,
        function (result) {
            document.getElementById('result').innerHTML = '';
            console.log(result);
            $.each(result, function (key, value) {
                document.getElementById('result').innerHTML += `<p>${value.city} : ${value.street_name}<\p>`;
            });
        },
    );
});