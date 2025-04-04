document.addEventListener('DOMContentLoaded', () => {
    const likeButtons = document.querySelectorAll('.like-button');

    likeButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission for animation
            button.classList.add('like-animation');
            setTimeout(() => {
                button.classList.remove('like-animation');
                button.closest('form').submit(); // Submit the form after animation
            }, 500); // Animation duration
        });
    });
});
