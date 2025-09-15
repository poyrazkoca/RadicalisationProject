

const baImg = document.getElementById('ba-img');
const baBtn = document.getElementById('ba-btn');
let showingBefore = true;

baBtn.addEventListener('click', () => {
  if (showingBefore) {
    baImg.src = 'after.JPG';
    baImg.alt = 'After';
    baBtn.textContent = 'Show Before';
  } else {
    baImg.src = 'before.JPG';
    baImg.alt = 'Before';
    baBtn.textContent = 'Show After';
  }
  showingBefore = !showingBefore;
});
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
// ...existing code...

// Initialize at 50%
setSlider(50);