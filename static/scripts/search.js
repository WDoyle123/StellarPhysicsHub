$(document).ready(function() {
    $('#search-bar').on('input', function() {
        var query = $(this).val();
        $.ajax({
            url: '/autocomplete',
            data: { 'q': query },
            success: function(data) {
                $('#suggestions-box').empty();
                data.matching_results.forEach(function(item) {
                    $('#suggestions-box').append($('<div>').text(item));
                });
            }
        });
    });
});

