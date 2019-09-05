$(document).ready(function() {
 
  $("#owl-btc-example").owlCarousel({

  	loop:false,
    margin:10,
    responsiveClass:true,
    nav    : true,
    navText : ["<i class='fa fa-chevron-left' style='color: #fff;'> </i>","<i class='fa fa-chevron-right' style='color: #fff;'></i>"],
    // navText : ["Previous","Next"],
    autoplay:true,
    autoplayTimeout:3000,
    autoplayHoverPause:true,
    responsive: {
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

    $("#owl-btc-example2").owlCarousel({

        loop: true,
        margin: 10,
        responsiveClass: true,
        nav: true,
        navText: ["<i class='fa fa-chevron-left pink pink-left' style='color: #fff;'> </i>", "<i class='fa fa-chevron-right pink' style='color: #fff;'></i>"],
        responsive: {
            0: {

                items: 1,
                loop: true,
            },
            600: {

                items: 3,
                loop: true,
            },
            1000: {

                items: 5,
                loop: true,
            }
        }
    });

    $("#owl-btc-example3").owlCarousel({

        loop: true,
        margin: 10,
        responsiveClass: true,
        nav: true,
        navText: ["<i class='fa fa-chevron-left pink pink-left'> </i>", "<i class='fa fa-chevron-right pink'></i>"],
        responsive: {
            0: {

                items: 1,
                loop: true,
            },
            600: {

                items: 3,
                loop: true,
            },
            1000: {

                items: 5,
                loop: true,
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
    console.log(typeof jsonData)
    var str = jsonData;
    var res = str.replace(/"/g, "");
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
        // data: jsonVal,
        data: res,
        success: function(result){
            // console.log(result)                
            var json_data = JSON.parse(result);
            console.log(json_data);
            // $("#myModal").;
            showDialog(json_data);
        },
        failure: function (response) {
            console.log(response);
        }
    });
}

function showDialog(result){
    console.log(result)
    
    var movieDialog = document.getElementById('movieDialog');
    var closeBtn = document.getElementById('closeBtn');
    var movieTitle = document.getElementById('movieTitle');
    movieTitle.innerHTML = result.title;    
    movieDialog.showModal();
    closeBtn.addEventListener('click', function() {
        movieDialog.close('animalNotChosen');
    });
}