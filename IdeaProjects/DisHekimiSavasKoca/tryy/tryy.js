const islemData = {
  implant: {
    title: 'İmplant',
    photos: [
      'implant-before.jpg',
      'implant-after.jpg',
      'implant-step1.jpg',
      'implant-step2.jpg'
    ],
    details: `
      <h3>Sık Sorulan Sorular</h3>
      <p>İmplant işlemi acıtır mı? Hayır, lokal anestezi ile ağrısızdır.</p>
      <h3>Dikkat Edilmesi Gerekenler</h3>
      <ul>
        <li>İlk 24 saat sıcak yiyecek/içecekten kaçının.</li>
        <li>Düzenli ağız bakımı yapın.</li>
      </ul>
    `
  },
  zirkonyum: {
    title: 'Zirkonyum',
    photos: [
      'zirkonyum-before.jpg',
      'zirkonyum-after.jpg',
      'zirkonyum-step1.jpg'
    ],
    details: `
      <h3>Sık Sorulan Sorular</h3>
      <p>Zirkonyum kaplama dayanıklı mıdır? Evet, uzun ömürlüdür.</p>
      <h3>Dikkat Edilmesi Gerekenler</h3>
      <ul>
        <li>Sert gıdalardan kaçının.</li>
        <li>Düzenli diş kontrolü yaptırın.</li>
      </ul>
    `
  }
};

const modal = document.getElementById('islem-modal');
const modalBody = document.getElementById('modal-body');
const closeBtn = document.querySelector('.close-btn');

document.querySelectorAll('.islem-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    const islem = btn.dataset.islem;
    const data = islemData[islem];
    if (!data) return;
    let html = `<h2>${data.title}</h2>`;
    html += '<div class="photo-group">';
    data.photos.forEach(src => {
      html += `<img src="${src}" alt="${data.title}">`;
    });
    html += '</div>';
    html += `<div class="details">${data.details}</div>`;
    modalBody.innerHTML = html;
    modal.style.display = 'flex';
  });
});

closeBtn.addEventListener('click', function() {
  modal.style.display = 'none';
});

window.addEventListener('click', function(e) {
  if (e.target === modal) {
    modal.style.display = 'none';
  }
});
