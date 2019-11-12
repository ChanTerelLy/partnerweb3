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
                    document.getElementById(value.s_id).insertAdjacentHTML('beforeend', parse_table(houses));
                });
            })
        });
});
function parse_table(data){
  var perrow = 5, // 5 items per row
      html = "<table class='table table-hover table-bordered'><tr>";

  // Loop through array and add table cells
  for (var i=0; i<data.length; i++) {
      let color_house = '';
      switch (data[i].h_segment) {
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

    html += `<td class='${color_house}'><a href='/house_info/${data[i].h_id}/' target="_blank">${data[i].name}</a></td>`;
    // Break into next row
    var next = i+1;
    if (next%perrow==0 && next!=data.length) {
      html += "</tr><tr>";
    }
  }
  html += "</tr></table>";

  // ATTACH HTML TO CONTAINER
  return html;
}