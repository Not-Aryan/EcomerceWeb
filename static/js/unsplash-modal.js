var usButton = document.querySelector(".unsplash");
var close = document.querySelector(".modal-close");
var m = document.querySelector(".modal");

usButton.addEventListener("click", function() {
    m.classList.toggle("active");
});

close.addEventListener("click", function() {
    m.classList.toggle("active");
});

m.addEventListener("click", function() {
    if(event.currentTarget === event.target) {
        m.classList.toggle("active");
    }
});

function Search() {

    var clientId = "eH01h4Z5h0r0GxxVtN5TG9Rv0P6h-dxVSB0CTu3XKY4";
    var query = document.querySelector(".search").value;
    var url = "https://api.unsplash.com/search/photos/?client_id="+clientId+"&query="+query+"&orientation=portrait";
    var i = 0;
    document.querySelector(".results").innerHTML = "";
    fetch(url)
        .then(function (data) {
            return data.json();
    })
        .then(function(data) {
            data.results.forEach(photo => {
                if (i < 9) {
                    let link = `<img class="uns-img" name='${i}' onclick="choseimg(${i});" src="${photo.urls.regular}">`;
                    $(".results").append(link);
                    i++;
                }
            });
        });
}



function choseimg(i){
    var imgs = document.querySelector(".results").getElementsByTagName('img');
    var input = document.getElementById("img-input");
    var par = document.getElementById("img-url");
    for (var j=0; j<imgs.length; j++){
        var curImg = imgs[j];
        if (curImg.name == i){
            input.value=curImg.src;
            m.classList.toggle("active");
            par.classList.add("focus");
        }
    }
}
