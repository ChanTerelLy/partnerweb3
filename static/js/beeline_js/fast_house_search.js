document.getElementById('input-search').addEventListener('keydown', function (value) {
    $.getJSON(`./street_search/?streetPattern=${document.getElementById('input-search').value}`,
        function (result) {
            document.getElementById('result').innerHTML = '';
            console.log(result);
            $.each(result, function (key, value) {
                document.getElementById('result').innerHTML += `<p id="${value.s_id}">${value.city} : ${value.street_name}<\p>`;
            });
        },
    );
});
document.getElementById('input-button').addEventListener('click', function (value) {
    $.getJSON(`./street_search/?streetPattern=${document.getElementById('input-search').value}`,
        function (result) {
            document.getElementById('result').innerHTML = '';
            console.log(result);
            $.each(result, function (key, value) {
                document.getElementById('result').innerHTML += `<p id="${value.s_id}">${value.city} : ${value.street_name}<\p>`;
                $.getJSON(`/get_homes_by_street?house_id=${value.s_id}`, function (houses) {
                    $.each(houses, function (key, house)
                    {
                        document.getElementById(value.s_id).insertAdjacentHTML('beforeend', `<span class="badge-success">${house}</span>`);
                    });
            });
        })
    });
});