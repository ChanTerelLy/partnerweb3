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
        allowTimes: ['00:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
            '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00'],
        dayOfWeekStart: 1,
    });
}

let assign_data = []
let choosed_assign_data = {}
let getSchedule = (id, inline, load_el, house_id = false) => {
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
                            assign_data = result;
                            getColorSchedule(ticket_id);
                            $.each(result, function (key, value) {
                                globalDate.push(value['convenient_time']);
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
                },
                onSelectTime: function (ct,$i){
                    let time = $i.val().split(' ')[1];
                    $.each(assign_data, function (key, value){
                        if(value['convenient_time'] == time){
                            choosed_assign_data = value;
                        }
                    })
                    //set data for all send form
                    $('#installerscheduleform').val($i.val());
                    $('#assign-myself').val($i.val());
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
            success: function (data) {
                alert(data.result)
            }
        }
    );
}

function getTicketInfo(id) {
    let tariff = document.getElementById(`t_${id}`);
    $.ajax({
            url: `/ticket_info/${id}/`,
            success: function (data) {
                tariff.innerText = `${data.services.IS_INAC_PRESET_name} ${data.services.IS_PRESET_name}`
            }
        }
    );
}

function getHouseID() {
    let url = window.location.pathname;
    return url.split('/');
}

let tariffs = []
function setMobilePresets(city_id, house_id) {
    let tariff = document.getElementById('id_basket');
    $.ajax({
        url: `/get_mobile_presets?city_id=${city_id}&house_id=${house_id}&`,
        success: function (data) {
            tariffs = tariffs.concat(data)
            for (let property of data) {
                let option = document.createElement('option');
                option.innerText = `${property.name} - ${property.min_cost_total_price}р.`;
                option.setAttribute('bundel_id', property.id);
                option.setAttribute('service_type', property.service_type);
                option.setAttribute('vpdn', property.min_cost.VPDN.S_ID);
                option.value = `${property.id};${property.service_type};${property.min_cost.VPDN.S_ID};${property.name}`;
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
            tariffs = tariffs.concat(data)
            for (let property of data) {
                if (!property.name) continue;
                let option = document.createElement('option');
                option.innerText = `${property.name} - ${property.min_cost_total_price}р.` ;
                option.setAttribute('bundel_id', property.id);
                option.setAttribute('service_type', property.service_type);
                option.setAttribute('VPDN', property.min_cost.VPDN.S_ID);
                option.value = `${property.id};${property.service_type};${property.min_cost.VPDN.S_ID};${property.service_name}`;
                tariff.add(option);
            }
        }
    });
}

function getTariffInfo(){
    let id = $('#id_basket').children("option:selected").attr('bundel_id');
    let info_box = $('#tariff_info')
    $.each(tariffs, function (key, value){
        if(value['id'] == id){
            if(value['service_type'] == 'IS_PRESET'){
                info_box.show()
                info_box.html(
                    `<p><b>Стоимость</b>: ${value['min_cost_total_price']}</p>
                     <p><b>Минут</b>: ${value['minutes']}</p>
                     <p><b>Смс</b>: ${value['sms']}</p>
                     <p><b>Гигабайт</b>: ${value['traffic']}</p>
                     <p><b>Интернет</b>: ${value?.min_cost?.VPDN?.DATA?.traffic_classes?.inet[1]?.speed_in / 1000}</p>
                     <p><b>ТВ приставка в комплекте</b>: ${value?.min_cost?.TVE_RENT ? 'да' : 'нет'}</p>
                     <p><b>Колличество каналов</b>: ${value?.min_cost?.TVE?.DATA?.count_chanals}</p>
                     <p><b>Роутер</b>: ${value?.min_cost?.W_NONSTOP_NR?.DATA?.name}</p>
`
                )
            }
            else if(value['service_type'] == 'IS_INAC_PRESET'){
                info_box.show()
                info_box.html(
                    `<p><b>Стоимость</b>: ${value['min_cost_total_price']}</p>
                     <p><b>Интернет</b>: ${value?.min_cost?.VPDN?.DATA?.traffic_classes?.inet[1]?.speed_in / 1000}</p>
                     <p><b>ТВ приставка в комплекте</b>: ${value?.min_cost?.TVE_RENT ? 'да' : 'нет'}</p>
                     <p><b>Колличество каналов</b>: ${value?.min_cost?.TVE?.DATA?.count_chanals}</p>
                     <p><b>Роутер</b>: ${value?.min_cost?.W_STOPPABLE_RENT_NR?.DATA?.name}</p>
`
                )
            }
        }
    })
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
    tariff_options = document.getElementById('tariff_checkbox').querySelectorAll('input');
    let tarrif_menu = [];
    for (let i of tariff_options) {
        if (i.checked === true) tarrif_menu.push(i.labels[0].innerText)
    }
    let entrance = document.getElementById('entrance').value;
    let floor = document.getElementById('floor').value;
    payload = {
        'number': number, 'agent': agent, 'client_name': client_name, 'address': address, 'phone1': phone1,
        'time': time, 'tariff': tariff, 'mail_to': mails, 'comment': comment,
        'csrfmiddlewaretoken': csrfmiddlewaretoken, 'tariff_menu': tarrif_menu, 'entrance': entrance, 'floor': floor
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
            success: data => {
                return data
            },
            error: error => console.log(error)
        }
    );
};
get_call_today_tickets = () => {
    return $.ajax({
            url: `/call_today_tickets/`,
            success: data => {
                return data
            },
            error: error => console.log(error)
        }
    );
};
get_switched_tickets = () => {
    return $.ajax({
            url: `/switched_tickets/`,
            success: data => {
                return data
            },
            error: error => console.log(error)
        }
    );
};
get_count_created_today = () => {
    return $.ajax({
            url: `/count_created_today/`,
            success: data => {
                return data
            },
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
    if (status === 'Назначено в график' || status === 'Подключен' || status === 'Закрыта') {
        document.getElementById('id_datetime').disabled = true;
        document.getElementById('id_datetime').style.backgroundColor = '#e9ecef';
        document.getElementById('id_status').disabled = true;
        document.getElementById('id_comments').disabled = true;
        document.getElementById('img_change_phones').disabled = true;
        $('#submit-button').prop('disabled', true).addClass('disable')
        $('#submit-supervisor').prop('disabled', true).addClass('disable')
        $('#submit-myself').prop('disabled', true).addClass('disable')
        $('#id_status').val('')
    }
};

additionalTicketInfo = (positive) => {
    let number = document.getElementById('extra_ticket').value;
    let operator = document.getElementById('agent').innerText;
    return {"number": number, "positive": positive, "operator": operator}
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

sendSourceTicket = (operator, ticket_id, source, csrfmiddlewaretoken) => {
    let payload = {'source': source.value, 'ticket_id': ticket_id, 'operator': operator};
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
        }
    })
};

showSourceTicket = (ticket_id) => {
    $.ajax({
        url: `/ticket_source/?show=${ticket_id}`,
        type: 'GET',
        success: function (result) {
            let elem = document.getElementById(`source_${ticket_id}`)
            elem.value = result.source;
            if(elem.value != 'Не определено'){
                $(`#source_${ticket_id}`).css('background', 'transparent')
            }

        }
    })
};

function switchCounter() {
    $(document).ready(function () {
        $('switched_count').html(($('#switch_table tr').length - 1));
    });
    setInterval(function () {
        $('result_call').html(($('#call_table tr').filter(':visible').length - 1));
        $('result_switch').html(($('#switch_table tr').filter(':visible').length - 1));
        $('result_assign').html(($('#assign_table tr').filter(':visible').length - 1));
    }, 500);
}

function assignCounter() {
    $(document).ready(function () {
        var str = 'Назначенных заявок: ';
        $('assigned_count').html(str + ($('#assign_table tr').length - 1));
    });
}

function searchLine() {
    $(document).ready(function () {
        $("#myInput").on("keyup", function () {
            var value = $(this).val().toLowerCase();
            $("#myTable tr").filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
            });
        });
    });
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
}

function getCTNinfo() {
    ctn = document.getElementById('ctn').value;
    $.ajax({
        url: `/get_ctn_info/?ctn=${ctn}`,
        dataType: "json",
        success: function (data) {
            console.log(data);
            document.getElementById('personal_info').innerHTML = `
<p><b>ФИО:</b> ${data.data.name}</p>
<p><b>Адресс:</b> ${data.data.city} , ${data.data.street}, ${data.data.house}</p>`;
            document.getElementById('load_person').style.visibility = 'hidden'
        },
        beforeSend: function () {
            document.getElementById('load_person').style.visibility = 'visible'
        },
        error: function (err) {
            alert('Произошка ошибка, попробуйте снова');
            console.log(err);
            document.getElementById('load_person').style.visibility = 'hidden'
        }
    })
}

function setChangePhones() {
    for (let i = 1; i < 4; i++) {
        try {
            document.getElementById(`changePhone${i}`).value
                = document.getElementById(`phone${i}`).innerText;
        } catch (e) {
            document.getElementById(`changePhone${i}`).value = ''
        }
        try {
            document.getElementById(`changePhoneComment${i}`).value
                = document.getElementById(`phoneComment${i}`).innerText;
        } catch (e) {
            document.getElementById(`changePhoneComment${i}`).value = ''
        }
    }
}

function sendChangePhones(csrfmiddlewaretoken) {
        let time = document.querySelector("#cur_call_time").innerText;
        let phones_info = {"status_id":21,"call_time":time,
            "phones":[]};
        for (let i = 1; i < 4; i++) {
            let phone = '';
            let comment = '';
            try {
                phone = document.getElementById(`changePhone${i}`).value
            } catch (e) {
                phone = document.getElementById(`changePhone${i}`).value = ''
            }
            try {
                comment  = document.getElementById(`changePhoneComment${i}`).value;
            } catch (e) {
                comment  = document.getElementById(`changePhoneComment${i}`).value = ''
            }
            if (phone !== ''){
                phones_info.phones.push({'phone': phone, "comment" : comment})
            }

    }
        $.ajax({
            url: `/change_phone_number/?ticket_id=${ticket_id}`,
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrfmiddlewaretoken);
            },
            data: JSON.stringify(phones_info),
            dataType: 'text',
            success: function (data) {
                location.reload();
            }
        })
}

// getTariffOptions = (id) => {
//     let group = document.getElementById(id);
//     group.forEach(a => {
//         console.log(a);
//     })
// };


autoUpdateInstallerComments = (id, csrf_token) => {
    function setComments(result) {
        getCountAssigned();
        let comment_id = document.getElementById(`installer_comments_${id}`);
        comment_id.innerText = '';
        for (let property of result) {
            document.getElementById(`installer_comments_${id}`).insertAdjacentHTML('beforeend', property.text)
        }
    }

    function get_comments() {
        $.ajax({
            url: `/info/${id}/?json=1`,
            type: 'GET',
            dataType: 'json',
            success: function (result) {
                let j = JSON.parse(result);
                let comments = [j.comments[0]];
                document.getElementById(`assign_date_${id}`).innerHTML = j.assigned_date;
                setComments(comments);
                dump_assigned_ticket(id, result, csrf_token);
            }
        })
    }
    get_comments();

    setInterval(function (){get_comments()}, 180000);
};

function getCountAssigned() {
    let dates = document.querySelectorAll('#assign_table abbr');
    let d_now = moment().format('DD.MM.YYYY');
    let counter = 0;
    for(let d of dates){
        let as_d = d.innerText.split(' ')[0];
        if( as_d === d_now){
            counter++;
        }

    }
    console.log(counter);
    document.getElementById('assigned_today_counter').innerText = counter;
}

function dump_assigned_ticket(id, result, csrf_token) {
    $.ajax({
        url: `/info/${id}/?insert_assigned=1`,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        },
        data: JSON.stringify(result),
        dataType: 'text',
        success: function (data) {
            console.log(`${id} dumped`)
        }
    })
}

function getAupEmail() {
    $.ajax({
        url: `/get_aup_email`,
        type: 'GET',
        dataType: 'json',
        success: function (result) {
            result = JSON.parse(result);
            let mail_to = document.getElementById('mail_to');
            for (let human of result){
                let option = document.createElement("option");
                option.text = human.fields.name;
                option.value = human.fields.email;
                mail_to.add(option);
            }
        }
    })
}

function assignTicket(csrfmiddlewaretoken) {
    let payload =  Object.assign(choosed_assign_data,
        {
        'ticket_id': ticket_id,
        'entrance' : $('#entrance-myself').val(),
        'floor' : $('#floor-myself').val(),
        })
    $.ajax({
        url: `/assign_ticket/`,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrfmiddlewaretoken);
        },
        data: JSON.stringify(payload),
        dataType: 'text',
        success: function (data) {
            alert(data);
        }
    })
}