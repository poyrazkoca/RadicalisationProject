

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