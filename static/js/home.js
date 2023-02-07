// Functions
function displayWeather(data) {
    $("#high").text(data['high'] + "\u2109");
    $("#low").text(data['low'] + "\u2109");
    $("#temp").text(data['temp'] + "\u2109");
    $("#forecast").text(data['forecast']);
    $("#rain").text(data['rain'] + "%");
    $("#humidity").text(data['humidity'] + "%");
    $("#forecast_icon").attr('src', '/static/resources/weather_icons/'+data['icon']+'.svg');
}

function displayWord(data) {
    $("#title").text(data['title']);
    $("#pronunciation").text(data['pronunciation']);
    $("#type").text(data['type']);
    //Definitions
    $("#definitions").empty()
    $.each(data["definitions"], function(index, value) {
        $("#definitions").append("<p>"+value +"</p><br>");
        return false;
    });
    // Examples
    $("#examples").empty()
    $.each(data["examples"], function(index, value) {
        $("#examples").append("<p>"+value +"</p><br>");
        return false;
        //$('#examples').slick('slickAdd','<div>' + value + '</div>');
    });
}

function displayPrayer(data) {
    $("#prayer").text(data['prayer']);
    $("#verse").text(data['verse']);
}

function displayWeatherWeek(data) {
    // empty weather week container to make room for data
    $("#weather_week_table").empty();
    //iterate through the data getting one value type at a time
    // e.g. Get all the forecast, then all the dates, etc..
    $.each(data[0], function(day_index, day_value) {
        //console.log("--"+day_index+"--");
        var $row = $("<tr>");
        $.each(data, function(index, value) {
            //console.log(value[day_index]);
            if (day_index == 'icon') {
                src = '/static/resources/weather_icons/'+value[day_index]+'.svg'
                $row.append("<td id='img'><img src='"+src+"'></td>");
            } else {
                $row.append("<td id='"+day_index+"''>"+value[day_index]+"</td>");
            };
        });
        $row.append("</tr>");
        //console.log($row);
        $("#weather_week_table").append($row);
    });
}

function displayRecipe(data) {
    //Fade recipe card out
    $("#recipe_card .card-body").fadeOut("fast");
    //define current time to attach to img src so it can update
    time = Date.now();
    $("#name.recipe").text(data['name']);
    $("#summary.recipe").text(data['summary']);
    $("#author.recipe").text(data['author']);
    $("#image.recipe").attr('src', data['image']+"?t="+time);
    // Star Review
    recipe_review.starRating('setRating', data['review']);
    // second star rating plugin
    //$('.rating').star_rating('rating', data['review']);
    //$('.rating').star_rating('reload');
    //myRating.setRating(data['review']);
    //QR CODE
    recipe_qrcode.clear();
    recipe_qrcode.makeCode(data['link']);
    //Fade recipe card back in
    $("#recipe_card .card-body").fadeIn("slow");
}

function displayPlanting(data) {
    //Fade planting card out
    $("#planting_card .card-body").fadeOut("fast");
    //define current time to attach to img src so it can update
    time = Date.now();
    $("#classification.planting").text(data['classification']);
    $("#name.planting").text(data['name']);
    $("#sow.planting").text(data['sow']);
    $("#spring_indoor_sow.planting").text(data['spring_indoor_sow']);
    $("#summer_transplant.planting").text(data['summer_transplant']);
    $("#spring_summer_transplant.planting").text(data['spring_summer_transplant']);
    $("#fall_indoor_sow.planting").text(data['fall_indoor_sow']);
    $("#fall_transplant.planting").text(data['fall_transplant']);
    $("#fall_direct_sow.planting").text(data['fall_direct_sow']);
    $("#succession.planting").text(data['succession']);
    $("#image.planting").attr('src', data['image']+"?t="+time);
    //Fade planting card back in
    $("#planting_card .card-body").fadeIn("slow");
}
// Inject the time in the UI
function renderDatetime() {
    var datetime = new Date();
    var time = document.querySelector('#time');
    var date = document.querySelector('#date');
    var day = document.querySelector('#day');
    date.textContent = datetime.toLocaleString('en-US', {year: 'numeric', month: 'long', day: 'numeric'});
    time.textContent = datetime.toLocaleString('en-US', {hour: 'numeric', minute: 'numeric', hour12: true});
    day.textContent = datetime.toLocaleString('en-US', {weekday: 'long'});
    //update clock
    setClock()
    // Set Light or Dark mode depending on time
    // 7am < now < 7pm = Light
    now = new Date().getHours()
    if (now >= 7 && now < 19) {return swapLightMode()};
    return swapDarkMode()
    

};
// Page update on socket request
function updatePage(data,on_connect=false) {
    //iterate through data and run required functions
    $.each(data, function(index, value) {
        //alert( index + ": " + value );
        //Run only if the data is ready to update

        if (data[index] != null) {
            if (data[index]['ready'] == true || on_connect == true) {
                if (index == "weather") displayWeather(data['weather']);
                if (index == "word") displayWord(data['word']);
                if (index == "prayer") displayPrayer(data['prayer']);
                if (index == "weather_week") displayWeatherWeek(data['weather_week']['data']);
                if (index == "recipe") displayRecipe(data['recipe']);
                if (index == "planting") displayPlanting(data['planting']);
            }
        }
    });
}
// Update Page to Dark Mode
function swapDarkMode() {
    let root = document.documentElement;
    // Text Color
    root.style.setProperty('--primary-text-color', '#F4F4F4');
    root.style.setProperty('--secondary-text-color', '#8c8c8c');
    root.style.setProperty('--tertiary-text-color', '#C9AAE7');
    // Main Colors
    root.style.setProperty('--primary-color', '#121212');
    root.style.setProperty('--secondary-color', '#161616');
    // Background Color
    root.style.setProperty('--background-color', '#000000');
    //Card Background Color
    root.style.setProperty('--card-background-color', '#121212');
}
// Update Page to Light Mode
function swapLightMode() {
    let root = document.documentElement;
    // Text Color
    root.style.setProperty('--primary-text-color', '#191919');
    root.style.setProperty('--secondary-text-color', '#3d3d3d');
    root.style.setProperty('--tertiary-text-color', '#3499ff');
    // Main Colors
    root.style.setProperty('--primary-color', '#ededed');
    root.style.setProperty('--secondary-color', '#e8e8e8');
    // Background Color
    root.style.setProperty('--background-color', '#fafafa');
    //Card Background Color
    root.style.setProperty('--card-background-color', '#ededed');
}

function setClock() {
    var time = new Date();
    var hd = 360.0 * time.getHours() / 12 + 30.0 * time.getMinutes() / 60;
    var md = 360.0 * time.getMinutes() / 60 + 6.0 * time.getSeconds() / 60;
    var sd = 360.0 * time.getSeconds() / 60 + 6.0 * time.getMilliseconds() / 1000;
    document.getElementById("div-hour").style.transform = "rotate(" + hd + "deg)";
    document.getElementById("div-minute").style.transform = "rotate(" + md + "deg)";
    document.getElementById("div-second").style.transform = "rotate(" + sd + "deg)";
}

// Document Ready
$(document).ready(function(){
    console.log("starting...");
    //Define QR Codes
    recipe_qrcode = new QRCode("recipe_qrcode", {
        text: 'https://www.allrecipes.com/',
        width: 128,
        height: 128,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });

    recipe_review = $(".recipe#review").starRating({
        readOnly: true,
        starSize: 5,
        disableAfterRate: false
    });
    recipe_review.starRating('resize', 24)
    // Start up the SocketIO connection to the server
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    // Update Display Socket Update
    socket.on('update_display', function(msg) {
        updatePage(msg)
    })
    // Force display update on initial connection
    socket.on('update_display_on_connect', function(msg) {
        updatePage(msg,on_connect=true)
    })
    // Every minute request update from server (run routines)
    setInterval(function(){
        socket.emit('update_me'); 
     }, 60000);
    // Update time and date every second
    setInterval(renderDatetime, 1000);
    swapDarkMode()

    //define div button to enable/disable light/dark mode temp maybe
    $( "#dark" ).click(function() {
        swapLightMode()
    });
    $( "#light" ).click(function() {
        swapDarkMode()
    });
});