
function vw(percent) {
    var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    return (percent * w) / 100;
}

function getRandomYPosition(excludeY) {
    let newY;
    do {
        newY = Math.floor(Math.random() * (window.innerHeight - 100)) + 50;
    } while (Math.abs(newY - excludeY) < 50); // Ensure the new Y is different from the excludeY
    return newY;
}

function moveBird(bird, onMoveComplete) {
    const startY = bird.getBoundingClientRect().top;
    const endY = getRandomYPosition(startY);
    const maxDistance = vw(99); // 100vmax in pixels
    const halfway = vw(50); // 50vmax in pixels

    bird.style.transition = `left ${Math.random() * 3 + 3}s linear, top ${Math.random() * 3 + 3}s linear`; // Variance in speed
    bird.style.left = `${window.innerWidth}px`;
    bird.style.top = `${endY}px`;

    const checkPosition = () => {
        const birdRect = bird.getBoundingClientRect();
        if (birdRect.left > halfway) { // If bird crosses 50vw
            if (onMoveComplete) onMoveComplete(); // Notify completion
        }
        if (birdRect.left > maxDistance) { // If bird crosses 100vw
            bird.style.transition = 'none'; // Disable transition
            bird.style.left = `-${bird.offsetWidth}px`; // Move instantly to the left
            bird.style.top = `${getRandomYPosition(endY)}px`; // Set new Y position
            requestAnimationFrame(() => moveBird(bird)); // Start moving again
        } else {
            requestAnimationFrame(checkPosition); // Check position again
        }
    };

    requestAnimationFrame(checkPosition);
}

function startMovingBirds() {
    const birds = document.querySelectorAll('.bird');
    const birdCount = birds.length;
    let startedNextBatch = false;

    birds.forEach((bird, index) => {
        const initialY = getRandomYPosition(null);
        bird.style.left = `-${bird.offsetWidth}px`;
        bird.style.top = `${initialY}px`;

        if (index < 3) {
            // Start the first three birds immediately
            moveBird(bird, () => {
                if (index === 2 && !startedNextBatch) {
                    // Once the first three birds cross 50vw, start the next three
                    startedNextBatch = true;
                    for (let j = 3; j < birdCount; j++) {
                        const nextBird = birds[j];
                        const nextInitialY = getRandomYPosition(null);
                        nextBird.style.left = `-${nextBird.offsetWidth}px`;
                        nextBird.style.top = `${nextInitialY}px`;
                        moveBird(nextBird);
                    }
                }
            });
        } else {
            // Delay the start of the next three birds
            bird.style.left = `-${bird.offsetWidth}px`;
            bird.style.top = `${initialY}px`;
        }
    });
}

startMovingBirds();
