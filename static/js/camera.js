// client-side camera helper for capture.html
async function initCamera(roll) {
  const video = document.getElementById('video');
  const snapBtn = document.getElementById('snap');
  const captures = document.getElementById('captures');
  const counter = document.getElementById('capture-counter');
  let captureCount = 0;

  // --- Initialize Camera ---
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    showNotification('Camera connected successfully!', 'success');
  } catch (err) {
    console.error('Camera initialization failed:', err);
    showNotification('Camera access blocked. Please allow permission or use HTTPS/localhost.', 'error');
    return;
  }

  // --- Capture and Upload ---
  snapBtn.onclick = async () => {
    snapBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Capturing...';
    snapBtn.disabled = true;

    try {
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const dataUrl = canvas.toDataURL('image/jpeg');

      // Show preview
      const img = document.createElement('img');
      img.src = dataUrl;
      Object.assign(img.style, {
        width: '120px',
        height: '120px',
        objectFit: 'cover',
        border: '2px solid var(--bs-success)',
        borderRadius: '8px',
        opacity: '0',
        transition: 'opacity 0.3s'
      });
      captures.appendChild(img);
      setTimeout(() => (img.style.opacity = '1'), 50);

      // Upload to backend
      const response = await fetch('/api/upload_face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roll, image: dataUrl })
      });

      if (response.ok) {
        const result = await response.json();
        showNotification(`✅ Image saved as ${result.saved}`, 'success');
        captureCount++;
        counter.textContent = captureCount;
      } else {
        showNotification('❌ Error uploading image to server', 'error');
      }
    } catch (err) {
      console.error('Upload failed:', err);
      showNotification('Upload failed. Please try again.', 'error');
    } finally {
      snapBtn.innerHTML = '<i class="fas fa-camera me-2"></i>Capture & Upload';
      snapBtn.disabled = false;
    }
  };
}

// --- Toast Notification Helper ---
function showNotification(message, type = 'info') {
  const existing = document.querySelector('.notification-toast');
  if (existing) existing.remove();

  const alertClass = {
    success: 'bg-success',
    error: 'bg-danger',
    info: 'bg-info',
    warning: 'bg-warning'
  }[type] || 'bg-info';

  const icon = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle'
  }[type];

  const toastHTML = `
    <div class="position-fixed bottom-0 end-0 p-3 notification-toast" style="z-index: 2000;">
      <div class="toast align-items-center text-white ${alertClass}" role="alert">
        <div class="d-flex">
          <div class="toast-body">
            <i class="fas ${icon} me-2"></i>${message}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', toastHTML);
  const toastEl = document.querySelector('.notification-toast .toast');
  const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
  toast.show();

  setTimeout(() => {
    const notif = document.querySelector('.notification-toast');
    if (notif) notif.remove();
  }, 3500);
}
