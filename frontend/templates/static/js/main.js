// ========================================
// MAIN JAVASCRIPT FILE
// Attendance System - Client-side Logic
// 
// TODO: Migrate to TypeScript for better type safety
// TODO: Add unit tests for utility functions
// ========================================

// Theme Toggle
// Saves preference to localStorage so it persists across sessions
function toggleTheme() {
  const body = document.body;
  const icon = document.querySelector('.theme-toggle i');

  body.classList.toggle('dark-mode');

  if (body.classList.contains('dark-mode')) {
    icon.classList.remove('fa-moon');
    icon.classList.add('fa-sun');
    localStorage.setItem('theme', 'dark');
  } else {
    icon.classList.remove('fa-sun');
    icon.classList.add('fa-moon');
    localStorage.setItem('theme', 'light');
  }
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme');
  const icon = document.querySelector('.theme-toggle i');

  if (savedTheme === 'dark') {
    document.body.classList.add('dark-mode');
    if (icon) {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
    }
  }

  // Navbar scroll effect - adds shadow when scrolling
  window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
});

// ========================================
// NOTIFICATION SYSTEM
// Reusable toast notifications
// ========================================

function showNotification(message, type = 'info', duration = 3000) {
  // Remove existing notification to avoid stacking
  const existing = document.querySelector('.notification-toast');
  if (existing) existing.remove();

  const icons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle'
  };

  const toastHTML = `
    <div class="position-fixed bottom-0 end-0 p-3 notification-toast" style="z-index: 9999;">
      <div class="toast align-items-center text-white border-0 shadow-lg" role="alert">
        <div class="d-flex">
          <div class="toast-body d-flex align-items-center">
            <i class="fas ${icons[type]} me-2 fa-lg"></i>
            <span>${message}</span>
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', toastHTML);
  
  const toastEl = document.querySelector('.notification-toast .toast');
  const toast = new bootstrap.Toast(toastEl, { delay: duration });
  toast.show();

  setTimeout(() => {
    const notif = document.querySelector('.notification-toast');
    if (notif) notif.remove();
  }, duration + 500);
}

// ========================================
// LOADING OVERLAY
// ========================================

function showLoading(message = 'Loading...') {
  const overlay = document.createElement('div');
  overlay.className = 'spinner-overlay';
  overlay.id = 'loading-overlay';
  overlay.innerHTML = `
    <div class="text-center">
      <div class="spinner-border text-light mb-3" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-white fw-bold">${message}</p>
    </div>
  `;
  document.body.appendChild(overlay);
}

function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.remove();
}

// ========================================
// CAMERA UTILITIES
// ========================================

async function setupCamera(videoElement) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'user'
      } 
    });
    videoElement.srcObject = stream;
    return true;
  } catch (err) {
    console.error('Camera error:', err);
    showNotification('Camera access denied. Please allow camera permission.', 'error');
    return false;
  }
}

function stopCamera(videoElement) {
  if (videoElement && videoElement.srcObject) {
    const tracks = videoElement.srcObject.getTracks();
    tracks.forEach(track => track.stop());
    videoElement.srcObject = null;
  }
}

function captureFrame(videoElement, canvas) {
  const ctx = canvas.getContext('2d');
  canvas.width = videoElement.videoWidth || 640;
  canvas.height = videoElement.videoHeight || 480;
  ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg', 0.9);
}

// ========================================
// API HELPERS
// ========================================

async function apiRequest(url, method = 'GET', data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    }
  };
  
  if (data) {
    options.body = JSON.stringify(data);
  }
  
  try {
    const response = await fetch(url, options);
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// ========================================
// UTILITIES
// ========================================

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function formatTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit'
  });
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ========================================
// CONFETTI EFFECT (for success)
// ========================================

function triggerConfetti(element) {
  const colors = ['#667eea', '#764ba2', '#11998e', '#38ef7d', '#00c6ff', '#f5576c'];
  
  for (let i = 0; i < 50; i++) {
    const confetti = document.createElement('div');
    confetti.style.position = 'fixed';
    confetti.style.width = '10px';
    confetti.style.height = '10px';
    confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    confetti.style.left = Math.random() * 100 + 'vw';
    confetti.style.top = '-10px';
    confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
    confetti.style.zIndex = '10000';
    confetti.style.transition = 'all 2s ease-out';
    
    document.body.appendChild(confetti);
    
    setTimeout(() => {
      confetti.style.transform = `translate(${Math.random() * 200 - 100}px, ${window.innerHeight + 100}px) rotate(${Math.random() * 720}deg)`;
      confetti.style.opacity = '0';
    }, 10);
    
    setTimeout(() => confetti.remove(), 2000);
  }
}
