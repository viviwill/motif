// start of article_read.html
function goBack() {
    window.history.back()
}

$(function(){
    $(document).ready(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });

//rating form
    $('a[rel=popover]').popover({
        html: 'true',
        placement: 'top'
    })

// toggle button here
        $(".toggle-button").hover(function (e) {
            console.log("show effect")
            $(".menu-toggle").effect("shake", {times:1},750);
        });

    $(".menu-toggle").click(function (e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
        $("#article-main").toggleClass("col-md-8");
        $("#article-main-margin-1").toggleClass("col-md-2");
        $("#article-main-margin-2").toggleClass("col-md-2");
    });

//show/hide summary form
    $('#summarize-form').hide();
    $(document).ready(function () {
        $("#summarize-button").click(function () {
            console.log("click sum button!!!!");
            $('#summarize-form').show();
            $("#summarize-button").hide();
        });
    });

// summary form close button
    $(document).ready(function () {
        $("#summarize-close-button").click(function () {
            $('#user-summary').show();
            $("#summarize-button").show();
            $('#summarize-form').hide();
            $('#summary-edit-footer').show();
        });
    });

// summary edit button
    $(document).ready(function () {
        $("#summarize-edit-button").click(function () {
            $('#summarize-form').show();
            $('#user-summary').hide();
            $('#summary-edit-footer').hide();
        });
    });

//summary form submission
    $(document).on('submit', '#summarize-form', function (e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: "summary_edit/",
            data: {
                summary: $('#summary').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (response) {
                var update_summary;
                console.log("hahah")
                $('#summarize-form').hide();
                $('#user-summary').show();
                $('#summary-edit-footer').show();
                $('#user-summary').html(response['update_summary']);
            }
        });
    });

    // article-read.html - edit article storage settings
    $("#edit-article-storage").click(function (e)  {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: "article_storage_edit/",
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (response) {
                console.log(response['storage_status'])
                $("#edit-article-storage").html(response['storage_status'])
            }
        });
    });

    // article-read.html - change font+
    $("#font-minus").click(function (e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: "theme_edit/",
            data: {
                'font_size': 'minus',
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (response) {
                $(".article-content").css("font-size", response['font_size']);
            }
        });
    });

    // article-read.html - change font-
    $("#font-plus").click(function (e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: "theme_edit/",
            data: {
                'font_size': 'plus',
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (response) {
                $(".article-content").css("font-size", response['font_size']);
            }
        });
    });

    // index.html - article public setting edit
    $(".article-public-edit").click(function(e){
        e.preventDefault();
        var href = $(this).attr('href')
        var class_name = '.' + $(this).attr('class').split(' ')[1]
        $.ajax({
            type: 'POST',
            url: href,
            data: {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),},
            success: function (response) {
                console.log(class_name)
                var privacy_icon
                if (response['public'] == true) {
                    var privacy_icon = "<i class=\"fa fa-eye\" aria-hidden=\"true\"></i>";
                } else {
                    var privacy_icon = "<i class=\"fa fa-eye-slash\" aria-hidden=\"true\"></i>";
                }

                $(class_name).html(privacy_icon)
            }
        });
    });



//end
});
