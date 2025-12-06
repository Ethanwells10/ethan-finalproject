/**
 * Toast Notification System
 * Simple, elegant notifications for user feedback
 */

class Toast {
  static show(message, type = 'info', duration = 4000) {
    const container = this.getContainer();
    const toast = this.createToast(message, type);

    container.appendChild(toast);

    // Trigger reflow for animation
    toast.offsetHeight;
    toast.classList.add('show');

    // Auto-dismiss
    setTimeout(() => {
      this.hide(toast);
    }, duration);

    return toast;
  }

  static success(message, duration) {
    return this.show(message, 'success', duration);
  }

  static error(message, duration) {
    return this.show(message, 'error', duration);
  }

  static warning(message, duration) {
    return this.show(message, 'warning', duration);
  }

  static info(message, duration) {
    return this.show(message, 'info', duration);
  }

  static getContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  static createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    const icons = {
      success: 'fa-check-circle',
      error: 'fa-times-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };

    const titles = {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info'
    };

    toast.innerHTML = `
      <div class="toast-header">
        <i class="fas ${icons[type]} me-2"></i>
        <strong class="me-auto">${titles[type]}</strong>
        <button type="button" class="btn-close btn-close-sm" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    `;

    // Close button handler
    const closeBtn = toast.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => {
      this.hide(toast);
    });

    return toast;
  }

  static hide(toast) {
    toast.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }
}

// Make Toast globally available
window.Toast = Toast;

// Helper function for Flask flash messages
document.addEventListener('DOMContentLoaded', function() {
  // Convert Flask flash messages to toasts
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach(msg => {
    const type = msg.dataset.category || 'info';
    const message = msg.textContent.trim();

    // Map Flask categories to toast types
    const typeMap = {
      'success': 'success',
      'error': 'error',
      'danger': 'error',
      'warning': 'warning',
      'info': 'info'
    };

    Toast.show(message, typeMap[type] || 'info');
    msg.remove(); // Remove the original flash message element
  });
});
