(function() {
  const overlay = document.getElementById('ba-overlay');
  const slider = document.getElementById('ba-slider');
  const wrapper = slider.parentElement;
  let dragging = false;

  function setSlider(x) {
    const rect = wrapper.getBoundingClientRect();
    let percent = (x - rect.left) / rect.width;
    percent = Math.max(0, Math.min(1, percent));
    overlay.style.width = (percent * 100) + '%';
    slider.style.left = `calc(${percent * 100}% - 12px)`;
  }

  slider.addEventListener('mousedown', function(e) {
    dragging = true;
    document.body.style.cursor = 'ew-resize';
  });

  window.addEventListener('mousemove', function(e) {
    if (!dragging) return;
    setSlider(e.clientX);
  });

  window.addEventListener('mouseup', function() {
    dragging = false;
    document.body.style.cursor = '';
  });

  // Touch support
  slider.addEventListener('touchstart', function(e) {
    dragging = true;
    document.body.style.cursor = 'ew-resize';
  });
  window.addEventListener('touchmove', function(e) {
    if (!dragging) return;
    setSlider(e.touches[0].clientX);
  });
  window.addEventListener('touchend', function() {
    dragging = false;
    document.body.style.cursor = '';
  });

  // Initialize to center
  setSlider(wrapper.getBoundingClientRect().left + wrapper.getBoundingClientRect().width / 2);
})();

const baImg = document.getElementById('ba-img');
const baBtn = document.getElementById('ba-btn');
let showingBefore = true;

baBtn.addEventListener('click', () => {
  if (showingBefore) {
    baImg.src = 'after.JPG';
    baImg.alt = 'After';
    baBtn.textContent = '🡸 Öncesini Göster';
  } else {
    baImg.src = 'before.JPG';
    baImg.alt = 'Before';
    baBtn.textContent = 'Sonrasını Göster 🡺';
  }
  showingBefore = !showingBefore;
});