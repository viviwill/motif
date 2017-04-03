// start of article_read.html
function goBack() {
    window.history.back()
}

$(function(){
    //deleting article
    $(document).on("click", "#article-thumb-delete", function(e) {
        e.preventDefault();
        var href = $(this).attr('href')
        bootbox.confirm({
            message: "You sure?",
            buttons: {
                confirm: {label: 'Delete', className: 'btn-danger'},
                cancel: {label: 'Cancel', className: 'btn'}
            },
            callback: function (result) {
                console.log('This was logged in the callback: ' + result);
                if (result == true) {
                    console.log(href)
                    $.ajax({
                        type: 'POST',
                        url: href,
                        data: {
                            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                        },
                        success: function (response) {
                            console.log('article deleted');
                        }
                    });
                }
            }
        });
    });


    //add article through url
    $(document).on("click", "#base-add-url-submit", function(e) {
        var private = $('#base-add-url-private-check').is(":checked")
        var article_url = $('#base-add-url-value').val()
        console.log("SUBMIT - Ppublic:", private, "| url: ", article_url)
        $.ajax({
            type: 'POST',
            url: "/article_add/",
            data: {
                article_url: article_url,
                private: private,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function(response) {
                console.log('Article added');
                setTimeout(function(){
                    location.reload(); // then reload the page.(2)
                }, 100);  // wait for x secs. (1)
            }
        });
    });

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
            // $(".menu-toggle").effect("shake", {times:1},750);
        });

    // $(".menu-toggle").click(function (e) {
    //     e.preventDefault();
    //     $("#wrapper").toggleClass("toggled");
    //     $("#article-main").toggleClass("col-md-8");
    //     $("#article-main-margin-1").toggleClass("col-md-2");
    //     $("#article-main-margin-2").toggleClass("col-md-2");
    // });


    // toggle button here
    $("#sidebar-wrapper").hide()
    $(".menu-toggle").click(function (e) {
        e.preventDefault();
        var sidebar = $("#sidebar-wrapper")
        var article = $("#article-wrapper")
        var margin = $('.article-main-margin')
        var main = $('.article-main')
        if (sidebar.val() == "show") {
            sidebar.val("hide")
            sidebar.hide()
            console.log("side bar button click", sidebar.val())
            article.toggleClass("col-md-12 col-md-7 col-sm-12")
            margin.toggleClass("col-lg-2 col-lg-1")
            main.toggleClass("col-lg-10 col-md-12")
        }
        else {
            sidebar.val("show")
            sidebar.show()
            console.log("side bar button click", sidebar.val())
            article.toggleClass("col-md-12 col-md-7 col-sm-12")
            margin.toggleClass("col-lg-2 col-lg-1")
            main.toggleClass("col-lg-10 col-md-12")
        }

        //
        // $("#sidebar-wrapper").val("show")
        // console.log("side bar button click", $("#sidebar-wrapper").val())
        // $("#article-wrapper").toggleClass("col-md-7");
        // $("#sidebar-wrapper").toggleClass("col-sm-12 col-md-5");
        // $("#article-main-margin-1").toggle();
        // $("#article-main-margin-2").toggle();
        // $("#sidebar-wrapper").toggle();
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

    // rating
    $(document).on('submit', '#rating-form', function(e) {
        e.preventDefault();
        var score = $(".creative-star:checked").val();
        $.ajax({
            type: 'POST',
            url: "rating_edit/",
            data: {
                creative_star: score,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function(response) {
                console.log("rating submit:", score)
                $('#rating-form-close').trigger('click');
                $("#article-read-rating").replaceWith(response);
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
    $(".font-minus").click(function (e) {
        e.preventDefault();
        console.log('font+')
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
    $(".font-plus").click(function (e) {
        e.preventDefault();
        console.log('font-')
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


    // feedback submit
    $('#feedback-submit').click(function(e) {
        e.preventDefault();
        var test = $('#feedback-message').val()
        console.log(test)
        $.ajax({
            type: 'POST',
            url: "/feedback_submit/",
            data: {
                feedback_url: $('#feedback-url').val(),
                feedback_message: $('#feedback-message').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (response) {
                console.log("submit")
            }
        });
    });


    //summernote setup
    $(document).ready(function() {
        $('#summernote').summernote({
            placeholder: 'Write summary here...',
            height: 200,
            toolbar: [
                ['font', ['bold', 'italic', 'clear']],
                ['para', ['ul', 'ol']],
            ]
        });
        $(".note-popover").hide()
        $(".popover-content").hide()
        $('.note-editable').css('font-size','1.2rem');
        $('.note-editable').css('background-color','var(--main-theme-color-3)');
    });


    //upvote
    $('.upvote-button').on("click", '.btn', function(e) {
        e.preventDefault();
        var element = $(this)
        var storage_id = element.attr('value');
        var vote_count = parseInt(element.children(' span').html());
        console.log('vote_count',vote_count);
        $.ajax({
            type: 'POST',
            url: "/upvote_summary/",
            data: {
                storage_id: storage_id,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (response) {
                console.log("upvote summary on:", storage_id)
                var voted = response['voted']
                // console.log("Voted: ", response['voted'])
                if (voted == 1 ) {
                    element.toggleClass("btn-secondary btn-motif-1");
                    element.children(' span').html(vote_count+1);
                }
                else {
                    element.toggleClass("btn-motif-1 btn-secondary");
                    element.children(' span').html(vote_count-1);
                }
            }
        });
    });


//end
});
