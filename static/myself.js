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
    $.ajax('/search_ajax/',{
        data:{
            from_station: from_station,
            to_station: to_station,
            date: date
        },
        dataType: "json",
        method: "post"
    }).done(function(data){
                if(data.code===0 || data.code==='0'){
                    $("#queryLeftTable").html(data.html);
                    $("#notice").html('<strong>'+from_station+'</strong> -->'+'<strong>'+to_station+'</strong> ('+date+') 共计'+data.quantity+'车次');
                }else if(data.code===1 || data.code==='1'){
                    $("#queryLeftTable").html('');
                    $("#notice").html('<p style="color:red;float:left;">未查到相关信息！ 请检查<strong>城市名称</strong>是否正确！</p>');
                }else if(data.code===2 || data.code==='2'){
                    $("#queryLeftTable").html('');
                    $("#notice").html('<p style="color:red;float:left;">未查到相关信息！ 请检查<strong>日期</strong>是否正确！</p>');
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
    $.ajax('/ticket_order_ajax/',{
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
            window.location.href = "../ticket_order/";
        }
    });
}
