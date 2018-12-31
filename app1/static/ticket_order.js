function ticket_order(){
    $("#log").html("<li>正在订票...</li>");
    $("#submit").attr('disabled',true);
    let username = $("#username").val();
    let password = $("#password").val();
    let passenger_name = $("#passengerName").val();
    let seat_type = $("#seat_type").val();
    let inform_phone = $("#informPhone").val();
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
         xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
            }
        });
    $.ajax("order_action_ajax/",{
        data:{username: username, password: password, passenger_name: passenger_name, seat_type: seat_type, inform_phone:inform_phone},
        dataType: 'json',
        method: 'post'
    }).done(function (data) {
        if(data.status==="error"){
             $("#log").html("<li>" + data.message + "</li>");
        }else{
            $("#log").html(
            "<li>订单号码：" + data.订单号码 +"</li>" +
            "<li>出发日期：" + data.出发日期 +"</li>" +
            "<li>车厢号：" + data.车厢号 +"</li>" +
            "<li>座位号：" + data.座位号 +"</li>" +
            "<li>座位类别：" + data.座位类别 +"</li>" +
            "<li>车票类别：" + data.车票类别 +"</li>" +
            "<li>订票时间：" + data.订票时间 +"</li>" +
            "<li>最迟付款：" + data.最迟付款 +"</li>" +
            "<li>票价：" + data.票价 +"</li>");
        }
        $("#submit").attr('disabled',false);
    });
    return false;
}

function scramble_ticket(){
    $("#log").html("<li>正在初始化抢票...</li>");
    let username = $("#username").val();
    let password = $("#password").val();
    let passenger_name = $("#passengerName").val();
    let seat_type = $("#seat_type").val();
    let inform_phone = $("#informPhone").val();
    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
         xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
            }
        });
    $.ajax("scramble_ticket_ajax/",{
        data:{username: username, password: password, passenger_name: passenger_name, seat_type: seat_type, inform_phone:inform_phone},
        dataType: 'json',
        method: 'post'
    }).done(function (data) {
         $("#log").html("<li>" + data.message + "</li>");
    });
}