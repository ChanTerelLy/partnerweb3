// get color of calendar
function getColorSchedule(ticket_id) {
    let url = house_id ? `./get_schedule_color?house_id=${house_id}&ticket_id=0` : `./get_schedule_color?ticket_id=${ticket_id}&house_id=0`;
    $.ajax({
            url: url,
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
function call_timer() {
    $('#id_datetime').datetimepicker({
        format: 'd.m.Y H:i',
        allowTimes: ['00:00','10:00', '11:00', '12:00','13:00', '14:00','15:00',
            '16:00','17:00', '18:00','19:00', '20:00','21:00', '22:00'],
        dayOfWeekStart: 1,
    });
}


let getSchedule = (id, inline, load_el, house_id=false) => {
    $.datetimepicker.setLocale('ru');
    $(function () {
        $(id).datetimepicker(
            {
                format: 'd.m.Y H:i',
                dayOfWeekStart: 1,
                inline: inline,
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
                            getColorSchedule(ticket_id);
                            $.each(result, function (key, value) {
                                globalDate.push(key);
                            });
                            if (globalDate.length < 1) {
                                globalDate = ['00:00']
                            }
                            $(id).datetimepicker('setOptions', {allowTimes: globalDate});
                            console.log(globalDate);
                            document.getElementById(load_el).style.visibility = 'hidden'
                        },
                        beforeSend: function () {
                            document.getElementById(load_el).style.visibility = 'visible'
                        },
                        error: function () {
                            alert('Произошка ошибка, попробуйте снова');
                            document.getElementById(load_el).style.visibility = 'hidden'
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
                option.value = `${property.id};${property.service_type};${property.VPDN};${property.name}`;
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
                option.value = `${property.id};${property.service_type};${property.VPDN};${property.service_name}`;
                tariff.add(option);
            }
        }
    });
}

function sendEmail(csrfmiddlewaretoken) {
    let number = document.getElementById('ticket_number').innerText;
    let agent = document.getElementById('agent').innerText;
    let client_name = document.getElementById('client_name').innerText;
    let address = document.getElementById('address').innerText;
    let phone1 = document.getElementById('phone1').innerText;
    let time = document.getElementById('installerscheduleform').value;
    let tariff = document.getElementById('tariff_form').value;
    let mail_to = document.getElementById('mail_to').selectedOptions;
    let comment = document.getElementById('comment_form').value;
    let mails = [];
    for (let i of mail_to) mails.push(i.value);

    payload = {'number': number, 'agent' : agent, 'client_name' : client_name, 'address' : address, 'phone1': phone1,
    'time': time, 'tariff': tariff, 'mail_to': mails, 'comment': comment, 'csrfmiddlewaretoken': csrfmiddlewaretoken
    };
    $.ajax({
        url: '/send_mail/',
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrfmiddlewaretoken);
        },
        data: JSON.stringify(payload),
        dataType: 'text',
        success: function (result) {
            alert(result);
        }
    });
}

get_assigned_tickets = () => {
        return $.ajax({
            url: `/assigned_tickets/`,
            success: data => {return data},
            error: error => console.log(error)
            }
    );
};
get_call_today_tickets = () => {
        return $.ajax({
            url: `/call_today_tickets/`,
            success: data => {return data},
            error: error => console.log(error)
            }
    );
};
get_switched_tickets = () => {
        return $.ajax({
            url: `/switched_tickets/`,
            success: data => {return data},
            error: error => console.log(error)
            }
    );
};
get_count_created_today = () => {
        return $.ajax({
            url: `/count_created_today/`,
            success: data => {return data},
            error: error => console.log(error)
            }
    );
};

addTicketsToTable = (tickets, table_id) => {
    tickets = JSON.parse(tickets);
    for (let ticket of tickets) {
        let table = document.getElementById(table_id);
        let row = table.insertRow(1);
        row.insertCell(0).innerHTML = ticket.number;
        row.insertCell(1).innerHTML = ticket.address;
        row.insertCell(2).innerHTML = ticket.phone1;
        row.insertCell(3).innerHTML = ticket.status;
        row.insertCell(4).innerHTML = ticket.call_time;
        row.insertCell(5).innerHTML = ticket.operator;
    }

};

forbidChanges = (status) => {
    if(status === 'Назначено в график' ||  status === 'Подключен' ||  status === 'Закрыта') {
        document.getElementById('id_datetime').disabled = true;
        document.getElementById('id_status').disabled = true;
        document.getElementById('id_comments').disabled = true;
    }
};

additionalTicketInfo = (positive) => {
    let number = document.getElementById('extra_ticket').value;
    let operator = document.getElementById('agent').innerText;
    return {"number": number, "positive": positive, "operator":operator}
};

addAdditionalTicket = (positive, csrfmiddlewaretoken) => {
    let payload = additionalTicketInfo(positive);
    $.ajax({
        url: '/add_additional_ticket/',
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrfmiddlewaretoken);
        },
        data: JSON.stringify(payload),
        dataType: 'text',
        success: function (result) {
            alert(result);
        }
    })
};

sendSourceTicket = (self, ticket_id, source, csrfmiddlewaretoken) => {
    let operator = self.parentElement.parentElement.parentElement;
    let payload = {'source' : source.value, 'ticket_id': ticket_id, 'operator': operator.dataset.operator};
    $.ajax({
        url: `/ticket_source/?add=${ticket_id}/`,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrfmiddlewaretoken);
        },
        data: JSON.stringify(payload),
        dataType: 'text',
        success: function (result) {
            let data = JSON.parse(result);
            alert(data.status);
        }
    })
};

showSourceTicket = (ticket_id) => {
    $.ajax({
        url: `/ticket_source/?show=${ticket_id}`,
        type: 'GET',
        success: function (result) {
            document.getElementById(`source_${ticket_id}`).value = result.source;
        }
    })
};