// components.js - small UX helpers: show file name and disable submit while uploading
document.addEventListener('DOMContentLoaded', function() {
  // file inputs with class .cv-file
  document.querySelectorAll('.cv-file').forEach(function(inp) {
    const label = inp.closest('.file-input-wrap')?.querySelector('.file-name');
    inp.addEventListener('change', function() {
      if (!label) return;
      const f = inp.files && inp.files[0];
      label.textContent = f ? `${f.name} (${Math.round(f.size/1024)} KB)` : 'Fayl seçilməyib';
    });
  });

  // disable submit on click and show spinner
  document.querySelectorAll('form.async-submit').forEach(function(form){
    form.addEventListener('submit', function(e){
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        const original = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Göndərilir...';
        // allow form to submit normally; re-enable won't happen here (server redirect)
      }
    });
  });
});


document.addEventListener("DOMContentLoaded", function () {
    // Dropdown-ları yalnız kliklə aç
    const dropdownToggles = document.querySelectorAll('.navbar-nav .dropdown-toggle');

    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            e.preventDefault(); // linkin default açılmasını dayandır
            const parentDropdown = this.parentElement;

            // Əgər klik etdiyimiz dropdown artıq açıqdırsa bağla
            if (parentDropdown.classList.contains('show')) {
                parentDropdown.classList.remove('show');
                parentDropdown.querySelector('.dropdown-menu').classList.remove('show');
            } else {
                // Əvvəl bütün açıq dropdown-ları bağla
                document.querySelectorAll('.navbar-nav .dropdown.show').forEach(d => {
                    d.classList.remove('show');
                    d.querySelector('.dropdown-menu').classList.remove('show');
                });
                // Sonra kliklənən dropdown-u aç
                parentDropdown.classList.add('show');
                parentDropdown.querySelector('.dropdown-menu').classList.add('show');
            }
        });
    });

    // Ekranın başqa yerinə klikləyəndə dropdownları bağla
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar-nav')) {
            document.querySelectorAll('.navbar-nav .dropdown.show').forEach(d => {
                d.classList.remove('show');
                d.querySelector('.dropdown-menu').classList.remove('show');
            });
        }
    });
});