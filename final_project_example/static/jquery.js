// declare variables
var goData = $('#my-data').data();
  $.each (function(val, i) {
      $('thumbnails').append("<img src=" + val + "/>");
    })


// Specify the Flickr Settings

// const maxThumbs = 60; // max number of images to display in grid
//
// // declare variables
// const thumbContainer = document.getElementById('thumbnails');
// const overlay = document.getElementById("overlay");
// const nextBtn = document.getElementById("nextBtn");
// const prevBtn = document.getElementById("prevBtn");
// const modalImg = document.getElementById("image");
// let nextImgID;
// let currentImgID;
//
//
// // create image thumbnails
// const createThumb = (num, url, title) => {
//     let thumb = document.createElement('li');
//     thumb.id = num + 1;
//     thumb.classList.add("thumbnail");
//     thumb.innerHTML = '<img src="' + url + '" title="'+ title +'"/>';
//     thumbContainer.appendChild(thumb);
// }
//
//
// // load flickr JSON
// const loadJSON = (callback) => {
//     var xmlhttp = new XMLHttpRequest();
//     xmlhttp.overrideMimeType("application/json");
//     xmlhttp.open("GET", 'https://api.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=' + '80d72794b84477bdecafea98c3d43c7b' + '&photoset_id=' + '72157706205050634' + '&format=json&nojsoncallback=1son&nojsoncallback=1', true);
//
//     xmlhttp.onreadystatechange = () => {
//         if (xmlhttp.readyState === 4 && xmlhttp.status == "200") {
//             callback(xmlhttp.responseText);
//         }
//     }
//     xmlhttp.send(null);
// }
//
// // parse flickr JSON and populate data
// loadJSON((text) => {
//     const data = JSON.parse(text);
//     photo = data.photoset.photo;
//
//     for (let i = 0; i < maxThumbs; i++) {
//         const farmID = photo[i].farm;
//         const serverID = photo[i].server;
//         const id = photo[i].id;
//         const secret = photo[i].secret;
//         const title = photo[i].title;
//         const imgURL = 'https://farm' + farmID + '.staticflickr.com/' + serverID + '/' + id + '_' + secret + '.jpg';
//
//        createThumb(i, imgURL);
//
//     }
// });
//
//
//
// // Thumbnails click
// thumbContainer.addEventListener("click", (e) => {
//
//     // set modal image and title that of thumb clicked
//     modalImg.src = e.target.getAttribute("src");
//
//     // show overlay
//     overlay.style.display = "block";
//     setTimeout(function() {
//         overlay.classList.add("show");
//     }, 2);
//
//
//     // set currentImgID var to thumbnail clicked
//     currentImgID = e.target.parentNode.id;
//
//     // hide prev / next button if on first or last image
//     if (currentImgID >= maxThumbs) {
//         nextBtn.style.display = "none";
//     } else if (currentImgID <= 1) {
//         prevBtn.style.display = "none";
//     }
// });
//
//
// // Lightbox - get and load next image
// const nextImage = (direction) => {
//     if (direction == "prev") {
//         nextImgID = Number(currentImgID) - 1;
//     } else if (direction == "next") {
//         nextImgID = Number(currentImgID) + 1;
//     }
//
//     // set modal image and title to that of next thumbnail image
//     modalImg.src = document.getElementById(nextImgID).firstChild.getAttribute("src");
//
//     // set currentImgID to the current image
//     currentImgID = nextImgID;
//
//     // show / hide nextBtn
//     if (currentImgID >= maxThumbs) {
//         nextBtn.style.display = "none";
//     } else {
//         nextBtn.style.display = "block";
//     }
//
//     // show / hide prevBtn
//     if (currentImgID <= 1) {
//         prevBtn.style.display = "none";
//     } else {
//         prevBtn.style.display = "block";
//     }
// }
//
//
// // close lightbox
// const closeBtn = document.getElementById("closeBtn");
//
// closeBtn.onclick = () => {
//     overlay.style.display = "none";
//     overlay.classList.remove("show");
//
//     currentImgID = "";
//     nextBtn.style.display = "block";
//     prevBtn.style.display = "block";
// }
