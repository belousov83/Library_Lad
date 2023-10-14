const ratingButtons = document.querySelectorAll('.rating-buttons');

ratingButtons.forEach(button => {
    button.addEventListener('click', event => {
        // Получаем значение рейтинга из data-атрибута кнопки
        const rate = parseInt(event.target.dataset.rate)
        const bookId = parseInt(event.target.dataset.book)
        const ratingSum = button.querySelector('.rating-sum');
        // Создаем объект FormData для отправки данных на сервер
        const formData = new FormData();
        // Добавляем id книги, значение кнопки
        formData.append('book_id', bookId);
        formData.append('rate', rate);
        // Отправляем AJAX-Запрос на сервер
        fetch("/books/rating/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData
        }).then(response => response.json())
        .then(data => {
            // Обновляем значение на кнопке
            ratingSum.textContent = data.rating_sum;
        })
        .catch(error => console.error(error));
    });
});