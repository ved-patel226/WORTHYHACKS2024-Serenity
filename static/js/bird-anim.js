document.addEventListener('DOMContentLoaded', function () {
    var animationContainers = document.getElementsByClassName('bird');

    for (var i = 0; i < animationContainers.length; i++) {
        var animation = lottie.loadAnimation({
            container: animationContainers[i],
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: 'static/json/bird.json' 
        });
    }
});
