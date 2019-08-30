$(document).ready(function() {
 
  $("#owl-example").owlCarousel({

  	loop:false,
    margin:10,
    responsiveClass:true,
    nav    : true,
    navText : ["<i class='fa fa-chevron-left'> </i>","<i class='fa fa-chevron-right'></i>"],
    // navText : ["Previous","Next"],
    autoplay:true,
    autoplayTimeout:3000,
    autoplayHoverPause:true,
    responsive:{
        0:{

            items:1,
            // loop:true,
        },
        600:{

            items:3,
            // loop:true,
        },
        1000:{

            items:5,
            // loop:true,
        }
    }

  });

});

function myFunction(obj) {
    console.log(obj);
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

  
function sendMovieObject(jsonData){

    // var tags = JSON.parse(document.getElementById('tags-data').textContent);
    
    var str = jsonData;
    var res = str.replace(/False/g, "false");
    var jsonVal = res.replace(/None/g, 0);
    // console.log(jsonData);
    // console.log(jsonVal);
    var final_json = JSON.stringify(jsonVal);
    console.log(final_json);
    var objVal = "Hello from sendMovieObject()";
    // console.log("Hello from sendMovieObject()");
    $.ajax({
      type: "POST",
      url: "moviedetail",
      headers: {"X-CSRFToken": csrftoken},
      data: jsonVal,
      success: function(result){
        // alert("Success");
        console.log(result);
      },
      failure: function (response) {
        console.log(response);
      }
    });
}