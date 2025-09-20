const baImg = document.getElementById('ba-img');
const beforeBtn = document.getElementById('before-btn');
const afterBtn = document.getElementById('after-btn');

function showBefore() {
  baImg.src = 'before.JPG';
  baImg.alt = 'Öncesi';
  beforeBtn.style.display = 'none';
  afterBtn.style.display = 'inline-block';
}

function showAfter() {
  baImg.src = 'after.JPG';
  baImg.alt = 'Sonrası';
  beforeBtn.style.display = 'inline-block';
  afterBtn.style.display = 'none';
}

beforeBtn.addEventListener('click', showBefore);
afterBtn.addEventListener('click', showAfter);

// Initial state: show only 'Sonrasını Göster' button
showBefore();