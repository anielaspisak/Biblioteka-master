document.addEventListener('DOMContentLoaded', () => {
  // Znajdź wszystkie linki wypożyczania książek
  const borrowLinks = document.querySelectorAll('a[href*="borrow"]');

  borrowLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      //e.preventDefault(); // zatrzymujemy normalne działanie linka (możesz to usunąć, jeśli chcesz)
      alert('Kliknąłeś przycisk wypożyczania książki. Zaraz to przetworzymy!');
      // Tutaj można dodać AJAX, albo po prostu pozwolić na normalne przejście
      // np. window.location.href = link.href;
    });
  });
});
