//模态框
$('#myModal').on('shown.bs.modal', function () {
  $('#myInput').focus()
})

//查询相应函数
function search_form() {
    $("#notice").html('正在查询......')
    let from_station = $('#fromStationText').val();
    let to_station = $('#toStationText').val();
    let date = $('#dateText').val();
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
             xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
                }
            });
    $.ajax('search_ajax/',{
        data:{
            from_station: from_station,
            to_station: to_station,
            date: date
        },
        dataType: "json",
        method: "post"
    }).done(function(data){
                if(data.status===true || data.status==='true'){
                    $("#queryLeftTable").html(data.html);
                    $("#notice").html('<strong>'+from_station+'</strong> -->'+'<strong>'+to_station+'</strong> ('+date+') 共计'+data.quantity+'车次');
                }else{
                    $("#notice").html('<p style="color:red;float:left;">' + data.html + '</p>')
                }
           }
    );
    return false;
}

//预定相应
function order(date, from_station, to_station, train_no) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
             xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
                }
            });
    $.ajax('ticket_order_ajax/',{
        data:{
            from_station: from_station,
            to_station: to_station,
            date: date,
            train_no: train_no
        },
        dataType: "json",
        method: "post"
    }).done(function(data){
        if (data.status_code === "0" || data.status_code === 0){
            window.location.href = "ticket_order/";
        }
    });
}
