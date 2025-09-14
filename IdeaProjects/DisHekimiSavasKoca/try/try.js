
const sliderHandle = document.querySelector('.slider-handle');
const imageOverlay = document.querySelector('.image-overlay');
const sliderWrapper = document.querySelector('.slider-wrapper');
const afterImg = document.querySelector('.image-container > img');
const beforeImg = document.querySelector('.image-overlay img');

let isDragging = false;

function setSlider(percentage) {
    sliderHandle.style.left = `${percentage}%`;
    // Sürüklenen tarafa opaklık 0, diğerine 1
    if (percentage <= 0) {
        beforeImg.style.opacity = 1;
        afterImg.style.opacity = 0;
    } else if (percentage >= 100) {
        beforeImg.style.opacity = 0;
        afterImg.style.opacity = 1;
    } else if (percentage < 50) {
        beforeImg.style.opacity = 1;
        afterImg.style.opacity = 0;
    } else {
        beforeImg.style.opacity = 0;
        afterImg.style.opacity = 1;
    }
}

sliderHandle.addEventListener('mousedown', (e) => {
    isDragging = true;
    e.preventDefault();
});

window.addEventListener('mouseup', () => {
    isDragging = false;
});

window.addEventListener('mousemove', (event) => {
    if (!isDragging) return;
    const rect = sliderWrapper.getBoundingClientRect();
    let offsetX = event.clientX - rect.left;
    if (offsetX < 0) offsetX = 0;
    if (offsetX > rect.width) offsetX = rect.width;
    const percentage = (offsetX / rect.width) * 100;
    setSlider(percentage);
});

// Touch support for mobile
sliderHandle.addEventListener('touchstart', (e) => {
    isDragging = true;
    e.preventDefault();
});
window.addEventListener('touchend', () => {
    isDragging = false;
});
window.addEventListener('touchmove', (event) => {
    if (!isDragging) return;
    const touch = event.touches[0];
    const rect = sliderWrapper.getBoundingClientRect();
    let offsetX = touch.clientX - rect.left;
    if (offsetX < 0) offsetX = 0;
    if (offsetX > rect.width) offsetX = rect.width;
    const percentage = (offsetX / rect.width) * 100;
    setSlider(percentage);
});

// Initialize at 50%
setSlider(50);