console.log('load.js loaded');

// when the page is loaded, hide the loading circles also works for backarrow
window.addEventListener( "pageshow", function ( event ) {
    document.querySelector('.loading-circles').style.display = 'none';
    document.querySelector('.loading-overlay').style.display = 'none';
    document.body.classList.remove('no-scroll');
});

//show loading circles when load-show is clicked
document.querySelectorAll('.load-show').forEach(function(element) {
    element.addEventListener('click', function(event) {
        document.querySelector('.loading-circles').style.display = 'block';
        document.querySelector('.loading-overlay').style.display = 'block';
        document.body.classList.add('no-scroll');
    });
});