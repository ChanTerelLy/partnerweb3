// get color of calendar
function getColorSchedule(ticket_id) {
    $.ajax({
            url: `./get_schedule_color?ticket_id=${ticket_id}&house_id=0`,
            dataType: 'json',
            success: function (data) {
                $.each(data[0]['days'], function (key, i) {
                    document.querySelectorAll(`[data-date="${i.day}"][data-month="${data[0].month}"][data-year="${data[0].year}"]`)[0].style.background = i.status
                })

            }
        }
    );
}

//datetimepicker
let getCalendar = () => {
    $.datetimepicker.setLocale('ru');
    $('#id_datetime').datetimepicker({
        format: 'd.m.Y H:i',
        dayOfWeekStart: 1,
    });
    $(function () {
        $('#datetimepicker12').datetimepicker(
            {
                format: 'd.m.Y H:i',
                dayOfWeekStart: 1,
                inline: true,
                sideBySide: true,
                allowTimes: ['00:00'],
                todayButton: true,
                timepickerScrollbar: false,
                onSelectDate: function (value) {
                    let globalDate = [];
                    $.ajax({
                        url: `./schedule/${value.getFullYear()}/${value.getMonth() + 1}/${value.getDate()}`,
                        dataType: "json",
                        success: function (result) {
                            getColorSchedule();
                            $.each(result, function (key, value) {
                                globalDate.push(key);
                            });
                            if (globalDate.length < 1) {
                                globalDate = ['00:00']
                            }
                            $('#datetimepicker12').datetimepicker('setOptions', {allowTimes: globalDate});
                            console.log(globalDate);
                            document.getElementById('load').style.visibility = 'hidden'
                        },
                        beforeSend: function () {
                            document.getElementById('load').style.visibility = 'visible'
                        },
                        error: function () {
                            alert('Произошка ошибка, попробуйте снова');
                            document.getElementById('load').style.visibility = 'hidden'
                        }
                    });
                }
            });
    });
};

//
function getPersonalInfo() {
    phone = document.getElementById('phone').value;
    $.ajax({
        url: `/personal_info/?phone=${phone}&city=69`,
        dataType: "json",
        success: function (result) {
            console.log(result);
            document.getElementById('personal_info').innerHTML = `
<p><b>Баланс:</b> ${result.data.balance}</p>
<p><b>ФИО:</b> ${result.data.ensemble_personal_data.clientRepName}</p>
<p><b>Тариф:</b> ${result.data.ensemble_personal_data.soc_description}</p>
<p><b>Прописка:</b> ${result.data.ensemble_personal_data.clientRepAddress}</p>
<p><b>Основной номер:</b>${result.data.ensemble_personal_data.phoneHome}</p>
<p><b>Логин ДИ:</b>${result.data.ensemble_data.ctn_validation.existing_login.value}</p>`;
            document.getElementById('load_person').style.visibility = 'hidden'
        },
        beforeSend: function () {
            document.getElementById('load_person').style.visibility = 'visible'
        },
        error: function () {
            alert('Произошка ошибка, попробуйте снова');
            document.getElementById('load_person').style.visibility = 'hidden'
        }
    })
}

function checkFraud() {
    let flat = document.getElementById('id_flat').value;
    $.ajax({
            url: `./${flat}`,
            success: function (data) { alert(data.result)}
            }
    );
}

function getTicketInfo(id) {
    let tariff = document.getElementById(`t_${id}`);
    $.ajax({
            url: `/ticket_info/${id}/`,
            success: function (data) { tariff.innerText = `${data.services.IS_INAC_PRESET_name} ${data.services.IS_PRESET_name}`}
            }
    );
}

function getHouseID() {
    let url = window.location.pathname;
    return url.split('/');
}

function setMobilePresets(city_id, house_id) {
    let tariff = document.getElementById('id_basket');
    $.ajax({
        url: `/get_mobile_presets?city_id=${city_id}&house_id=${house_id}&`,
        success: function (data) {
            for (let property of data) {
                let option = document.createElement('option');
                option.innerText = property.name;
                option.setAttribute('bundel_id', property.id);
                option.setAttribute('service_type', property.service_type);
                option.setAttribute('vpdn', property.VPDN);
                option.value = `${property.id};${property.service_type};${property.VPDN}`;
                tariff.add(option);
            }
        }
    });
}

function setPresets(city_id, house_id) {
    let tariff = document.getElementById('id_basket');
    $.ajax({
        url: `/get_presets?city_id=${city_id}&house_id=${house_id}&`,
        success: function (data) {
            for (let property of data) {
                if (!property.name) continue;
                let option = document.createElement('option');
                option.innerText = property.name;
                option.setAttribute('bundel_id', property.id);
                option.setAttribute('service_type', property.service_type);
                option.setAttribute('VPDN', property.VPDN);
                option.value = `${property.id};${property.service_type};${property.VPDN}`;
                tariff.add(option);
            }
        }
    });
}