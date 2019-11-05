document.getElementById('input-search').addEventListener('keydown', function (value) {
    $.getJSON(`./street_search/?streetPattern=${document.getElementById('input-search').value}`,
        function (result) {
            document.getElementById('result').innerHTML = '';
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
            $.each(result, function (key, value) {
                document.getElementById('result').innerHTML += `<div id="${value.s_id}">${value.city} : ${value.street_name}<\div>`;
                $.getJSON(`/get_homes_by_street?house_id=${value.s_id}`, function (houses) {
                    $.each(houses, function (key, house) {
                        console.log(house.h_segment);
                        let color_house = '';
                        switch (house.h_segment) {
                            case -1:
                                color_house = 'bg-second';
                                break;
                            case 1:
                                color_house = 'bg-dangerous';
                                break;
                            case  2:
                                color_house = 'bg-warning';
                                break;
                            case  3:
                                color_house = 'bg-success';
                                break;
                        }
                        document.getElementById(value.s_id).insertAdjacentHTML('beforeend', `<a target="_blank" href="./house_info/${house.h_id}" style="border: solid black" class=${color_house}>${house.name}</a>`);
                    });
                });
            })
        });
});