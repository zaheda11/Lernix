// LERNIX CurrHub Pro Shared UI Script

document.addEventListener('DOMContentLoaded', () => {
    // Add custom hover transitions or log elements
    console.log("LERNIX CurrHub Pro initialized successfully.");

    // Simple header drop shadow on scroll
    const header = document.querySelector('.app-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.4)';
                header.style.backgroundColor = 'rgba(9, 13, 22, 0.95)';
            } else {
                header.style.boxShadow = '0 1px 0px rgba(255, 255, 255, 0.07)';
                header.style.backgroundColor = 'rgba(9, 13, 22, 0.8)';
            }
        });
    }
});
