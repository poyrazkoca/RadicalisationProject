const baImg = document.getElementById('ba-img');
const beforeBtn = document.getElementById('before-btn');
const afterBtn = document.getElementById('after-btn');

beforeBtn.addEventListener('click', () => {
  baImg.src = 'before.JPG';
  baImg.alt = 'Öncesi';
});

afterBtn.addEventListener('click', () => {
  baImg.src = 'after.JPG';
  baImg.alt = 'Sonrası';
});