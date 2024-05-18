let timeout;

function debouncedSearch(e) {
    clearTimeout(timeout);

    // timeout = setTimeout(() => {
    const inputValue = e.target.textContent;
    const temp_input = e.target.getAttribute('data-value');

    const intValue = isStringInt(inputValue.trim()); // Try to parse the input as an integer

    if (intValue) {
        main_function(e);
    } else {
        e.target.textContent = temp_input;
    }
    // }, 4000);

}

function isStringInt(inputString) {
    return /^\d+$/.test(inputString);
}


function main_function(e) {
    const a = check_value(e);
    if (a === 1) {
        console.log('Hit Api');
        send_request(e);
    }

}

function check_value(e) {
    const sec_2 = parseInt($('#sec_2_' + e.target.getAttribute('data-id')).val(), 10);
    const sec_1 = parseInt($('#sec_1_' + e.target.getAttribute('data-id')).val(), 10);
    const temp_value = parseInt((e.target.textContent).trim(), 10);
    const sec_name = e.target.getAttribute('data-field');

    let a;
    if (sec_name === 'section_1') {
        if (temp_value === sec_1) {
            a = 0;
        } else {
            $('#sec_1_' + e.target.getAttribute('data-id')).val(temp_value);
            if (sec_2) {
                document.querySelector('td[id=total_' + e.target.getAttribute('data-id') + ']').textContent = temp_value + sec_2;
            }
            else{
                document.querySelector('td[id=total_' + e.target.getAttribute('data-id') + ']').textContent = temp_value;
            }
            a = 1;
        }
    } else {
        if (temp_value === sec_2) {
            a = 0;
        } else {
            $('#sec_2_' + e.target.getAttribute('data-id')).val(temp_value);
            if (sec_1) {
                document.querySelector('td[id=total_' + e.target.getAttribute('data-id') + ']').textContent = temp_value + sec_1;
            }
            else{
                document.querySelector('td[id=total_' + e.target.getAttribute('data-id') + ']').textContent = temp_value;
            }            a = 1;
        }
    }
    return a;
}


$('#download').click(function() {
    var csv_name = $('#csv_name').val();
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        type: 'POST',
        headers: {'X-CSRFToken': csrfToken},
        url: '/download-csv/',
        success: function(response) {
            var blob = new Blob([response]);
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = csv_name;
            link.click();
        }
    });

});


const tds = document.querySelectorAll('td[contenteditable="true"]');
tds.forEach(td => {
  td.addEventListener('blur', debouncedSearch);
})