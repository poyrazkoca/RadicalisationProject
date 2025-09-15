

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
// ...existing code...
// ...existing code...