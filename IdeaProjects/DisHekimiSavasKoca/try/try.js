document.getElementById('show-before').addEventListener('click', function() {
  document.getElementById('ba-img').src = 'before.JPG';
});

document.getElementById('show-after').addEventListener('click', function() {
  document.getElementById('ba-img').src = 'after.JPG';
});

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