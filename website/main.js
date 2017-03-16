$(function(){
    $.ajax({
        type: "GET",
        dataType: "jsonp",
        url: 'http://localhost:5000/all',
        success: function (data) {
            blogposts_render(data);
            }
    });

});


$(function() {
    $('form#filter').on('submit', function() {
        var _that = $(this);
        $.ajax({
            type: "GET",
            data: _that.serialize(),
            dataType: "jsonp",
            url: _that.attr('action'),
            success: function (data) {
                console.log(data);
                blogposts_render(data);
                }
        });

        return false;
    });
});

function blogposts_render (data) {
    $('#blogposts').empty();
    $.each(data, function (i, item) {
        var template = "<p><lead>{{author}}'s post in category {{category}}</lead> <br><br>{{text}}</p>";
        var html = Mustache.render(template, item);
        $("#blogposts").append(html);
        console.log(i, item);
});
}

 $("form#filter: author").tooltip({
      position: "center right",
      offset: [-2, 10],
      effect: "fade",
      opacity: 0.7

      });

 $("form#filter: category").tooltip({
      position: "center right",
      offset: [-2, 10],
      effect: "fade",
      opacity: 0.7

      });