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

    $("#owl-btc-example4").owlCarousel({

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

    $("#owl-btc-example5").owlCarousel({

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

    $("#owl-btc-simMovie").owlCarousel({

        loop: false,
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



var csrftoken = getCookie('csrftoken');

function showLoginModal(){
    
        // Get the modal
    var modal = document.getElementById("loginModal");

    modal.style.display = "block";
    modal.style.zIndex = "9";
    // Get the button that opens the modal

    var btnLogin = document.getElementById("modalLoginBtn");

    // Get the <span> element that closes the modal
    // var span = document.getElementsByClassName("modalCancelBtn")[0];

    var btnCancel = document.getElementById("modalCancelBtn");

    btnCancel.addEventListener('click', function() {
        modal.style.display = "none";
    });
    var username = document.getElementById("username");
    
    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    btnLogin.addEventListener('click', function() {
        console.log(username.value);
        var id = username.value;
        var res = {"login": id};
        $.ajax({
            type: "POST",
            url: "authentic/login",
            headers: {"X-CSRFToken": csrftoken},
            // data: jsonVal,
            data: res,
            success: function(result){
                console.log(result);
                modal.style.display = "none";
                // $.redirect("/topmovies", {'arg1': 'value1', 'arg2': 'value2'});
                window.location.href = "/recommended";                
                // var json_data = JSON.parse(result);
                // console.log(json_data);
                // // $("#myModal").;
                // showDialog(json_data);
            },
            failure: function (response) {
                console.log(response);
            }
        });
    });

}




/*
    ****************** ********* ********* ********* ********* ********* ********* *********  
                        
                        Not using currently 

    ****************** ********* ********* ********* ********* ********* ********* ********* 

*/


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


$(".rateBtn").click(function(){
    movieid = $(this).attr('movieid');
    $("#rateThisMovieId").val(movieid)
    $("#rateModal").modal();
});

$("#modalRateBtn").click(function(){
    $.ajax({
        type: "POST",
        url: "authentic/login",
        headers: {"X-CSRFToken": csrftoken},
        // data: jsonVal,
        data: res,
        success: function(result){
            console.log(result);
            modal.style.display = "none";
            // $.redirect("/topmovies", {'arg1': 'value1', 'arg2': 'value2'});
            window.location.href = "/recommended";                
            // var json_data = JSON.parse(result);
            // console.log(json_data);
            // // $("#myModal").;
            // showDialog(json_data);
        },
        failure: function (response) {
            console.log(response);
        }
    });
});
