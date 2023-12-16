function updateLogs() {
    $.ajax({
        url: '/updateStatusSection',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            var statusList =  $('.statusList');
            statusList.empty();
            data.forEach(function(status) {
                if (status.status === 'OK') {
                    statusList.append('<li class="statusOK">' + status.name + ' -> ' + status.status + ': ' + status.message + '</li>');
                } else {
                    statusList.append('<li class="statusERROR">' + status.name + ' -> ' + status.status + ': ' + status.message + '</li>');
                }
            });
        },
        error: function(error) {
            console.log('ERROR', error);
        }
    });
}

setInterval(updateLogs, 3000);  