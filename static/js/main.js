// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive features
    initializeButtons();
    initializeTableResponsiveness();
    initializeChartResponsiveness();
    initializeSmoothScrolling();
});

//navbar
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navbarLinks = document.querySelector('.navbar-links');
    const navbarUser = document.querySelector('.navbar-user');

    mobileMenuButton.addEventListener('click', function() {
        navbarLinks.classList.toggle('active');
        navbarUser.classList.toggle('active');
        this.classList.toggle('active');
    });
});

// Button interactions
function initializeButtons() {
    const buttons = document.querySelectorAll('button, .button');
    
    buttons.forEach(button => {
        // Add ripple effect on click
        button.addEventListener('click', function(e) {
            // Only add effect if button isn't disabled
            if (!this.disabled) {
                const ripple = document.createElement('span');
                ripple.classList.add('ripple');
                this.appendChild(ripple);
                
                // Position the ripple
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                ripple.style.width = ripple.style.height = `${size}px`;
                ripple.style.left = `${e.clientX - rect.left - size/2}px`;
                ripple.style.top = `${e.clientY - rect.top - size/2}px`;
                
                // Remove ripple after animation
                ripple.addEventListener('animationend', () => {
                    ripple.remove();
                });
            }
        });

        // Add loading state handling
        button.addEventListener('click', function() {
            if (this.dataset.loading === 'true') {
                const originalText = this.textContent;
                this.textContent = 'Loading...';
                this.disabled = true;

                // Reset after 1 second (adjust as needed)
                setTimeout(() => {
                    this.textContent = originalText;
                    this.disabled = false;
                }, 1000);
            }
        });
    });
}

// Smooth scrolling implementation
function initializeSmoothScrolling() {
    // Add smooth scroll to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return; // Ignore empty anchors
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                // Add scroll indicator
                const indicator = createScrollIndicator();
                
                // Smooth scroll to target
                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
                const startPosition = window.pageYOffset;
                const distance = targetPosition - startPosition;
                const duration = 1000; // Adjust duration as needed
                let start = null;
                
                function animation(currentTime) {
                    if (start === null) start = currentTime;
                    const timeElapsed = currentTime - start;
                    const progress = Math.min(timeElapsed / duration, 1);
                    
                    window.scrollTo(0, startPosition + distance * easeInOutCubic(progress));
                    
                    if (timeElapsed < duration) {
                        requestAnimationFrame(animation);
                    } else {
                        indicator.remove(); // Remove indicator when done
                        // Add focus outline to target
                        targetElement.classList.add('scroll-focus');
                        setTimeout(() => {
                            targetElement.classList.remove('scroll-focus');
                        }, 1000);
                    }
                }
                
                requestAnimationFrame(animation);
            }
        });
    });
    
    // Add scroll to top button
    const scrollButton = createScrollToTopButton();
    document.body.appendChild(scrollButton);
    
    // Show/hide scroll button based on scroll position
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollButton.classList.add('visible');
        } else {
            scrollButton.classList.remove('visible');
        }
    });
}

// Utility function for smooth easing
function easeInOutCubic(t) {
    return t < 0.5 
        ? 4 * t * t * t 
        : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// Create scroll indicator
function createScrollIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    document.body.appendChild(indicator);
    return indicator;
}

// Create scroll to top button
function createScrollToTopButton() {
    const button = document.createElement('button');
    button.className = 'scroll-top';
    button.innerHTML = '↑';
    button.title = 'Scroll to top';
    
    button.addEventListener('click', () => {
        const duration = 1000;
        const start = window.pageYOffset;
        let startTime = null;
        
        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const progress = Math.min(timeElapsed / duration, 1);
            
            window.scrollTo(0, start * (1 - easeInOutCubic(progress)));
            
            if (timeElapsed < duration) {
                requestAnimationFrame(animation);
            }
        }
        
        requestAnimationFrame(animation);
    });
    
    return button;
}

// Table responsiveness
function initializeTableResponsiveness() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        // Add smooth hover effect on table rows
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.transition = 'background-color 0.3s ease';
                this.style.backgroundColor = '#f5f5f5';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });

        // Make table scrollable on small screens
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        wrapper.style.overflowX = 'auto';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

// Chart responsiveness
function initializeChartResponsiveness() {
    const charts = document.querySelectorAll('.chart');
    
    function updateChartSizes() {
        charts.forEach(chart => {
            const parent = chart.parentElement;
            const width = parent.clientWidth;
            chart.style.width = '100%';
            chart.style.height = `${width * 0.6}px`;
        });
    }

    updateChartSizes();

    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(updateChartSizes, 250);
    });
}

// Add CSS styles
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }

    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .table-responsive {
        margin: 1em 0;
        box-shadow: var(--box-shadow);
        border-radius: var(--border-radius);
    }

    .scroll-indicator {
        position: fixed;
        top: 50%;
        right: 20px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--accent-color);
        animation: pulse 1s infinite;
        z-index: 1000;
    }

    .scroll-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--accent-color);
        color: white;
        border: none;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s ease, transform 0.3s ease;
        transform: translateY(20px);
        z-index: 1000;
    }

    .scroll-top.visible {
        opacity: 1;
        transform: translateY(0);
    }

    .scroll-top:hover {
        transform: translateY(-5px);
    }

    .scroll-focus {
        animation: highlight 1s ease;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.5); opacity: 0.5; }
        100% { transform: scale(1); opacity: 1; }
    }

    @keyframes highlight {
        0% { background-color: transparent; }
        50% { background-color: rgba(52, 152, 219, 0.1); }
        100% { background-color: transparent; }
    }

    @media (max-width: 768px) {
        .table-responsive {
            margin: 0.5em -15px;
            padding: 0 15px;
        }
    }

    .chart {
        transition: width 0.3s ease, height 0.3s ease;
    }
`;

document.head.appendChild(style);