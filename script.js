// HyperClean Studio v2.0 - Formal Corporate Website Script
document.addEventListener('DOMContentLoaded', () => {

  // Toast Notification System
  window.showToast = function(message, icon = 'fa-circle-check') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.2s ease';
      setTimeout(() => toast.remove(), 250);
    }, 3000);
  };

  // Download Handlers - Ensure immediate downloading feedback for all download buttons
  const downloadBtns = document.querySelectorAll('.download-exe-trigger, .download-zip-trigger, [download], a[href$=".zip"], a[href$=".exe"], a[href$=".py"], a[href$=".txt"]');
  
  downloadBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const href = btn.getAttribute('href');
      const filename = btn.getAttribute('download') || (href ? href.split('/').pop() : '');

      if (btn.classList.contains('download-exe-trigger')) {
        showToast('Downloading HyperCleanStudio-v2.0.zip (37.8 MB)...', 'fa-file-arrow-down');
      } else if (btn.classList.contains('download-zip-trigger')) {
        showToast('Downloading hyperclean-studio-v2.0-source.zip...', 'fa-file-zipper');
      } else if (filename) {
        showToast(`Downloading ${filename}...`, 'fa-file-arrow-down');
      }
    });
  });

  // Copy Code Functionality
  window.copyCode = function(text, buttonElement) {
    navigator.clipboard.writeText(text).then(() => {
      const originalText = buttonElement.innerHTML;
      buttonElement.innerHTML = `<i class="fa-solid fa-check"></i> Copied`;
      buttonElement.style.color = '#34d399';
      showToast('Command copied to clipboard!');

      setTimeout(() => {
        buttonElement.innerHTML = originalText;
        buttonElement.style.color = '';
      }, 2000);
    }).catch(() => {
      showToast('Failed to copy text', 'fa-circle-exclamation');
    });
  };

  // Simulation Scan Inspector
  const startDemoBtn = document.getElementById('start-demo-btn');
  const demoTerminal = document.getElementById('demo-terminal');
  const demoProgressBar = document.getElementById('demo-progress-fill');

  if (startDemoBtn && demoTerminal) {
    let isRunning = false;

    const scanSteps = [
      { text: "[INIT] Initializing HyperClean Studio v2.0 Detector Engine...", delay: 200 },
      { text: "[AUDIT] Launching Safety Confirmation Modal & File Target Audit...", delay: 400 },
      { text: "[CHECK] Verifying file target list, caution item badges, and safety confirmation checkbox...", delay: 650 },
      { text: "[MEM] Invoking Win32 EmptyWorkingSet API across 42 active background processes...", delay: 950 },
      { text: "[OK]  RAM Working Set Flushed. Reclaimed 2.4 GB unallocated physical memory.", delay: 1250 },
      { text: "[GPU] Scanning graphics shader pipelines (NVIDIA DXCache, AMD DxCache, DirectX D3DSCache)...", delay: 1550 },
      { text: "[OK]  Purged 8.7 GB compiled graphics shader cache files.", delay: 1850 },
      { text: "[NET] Purging Windows DNS Resolver Cache (ipconfig /flushdns)...", delay: 2150 },
      { text: "[OK]  Windows DNS Resolver Cache successfully flushed.", delay: 2400 },
      { text: "[DEV] Scanning developer repositories (NPM, Yarn, Pip, UV, Poetry, Cargo, Gradle)...", delay: 2700 },
      { text: "[OK]  Purged NPM cache (.npm/_cacache): 12.3 GB reclaimed.", delay: 3000 },
      { text: "[OK]  Purged Pip Wheel & PyPI HTTP downloads: 4.8 GB reclaimed.", delay: 3300 },
      { text: "[OK]  Purged Cargo registry & Go build cache: 6.2 GB reclaimed.", delay: 3600 },
      { text: "[REG] Cross-matching Windows Registry against %AppData% leftover directories...", delay: 3900 },
      { text: "[OK]  Removed 3 uninstalled application orphan directories (1.5 GB).", delay: 4200 },
      { text: "[DONE] Execution Complete. Reclaimed 33.5 GB Disk Space | RAM Freed: 2.4 GB", delay: 4500 }
    ];

    startDemoBtn.addEventListener('click', () => {
      if (isRunning) return;
      isRunning = true;
      startDemoBtn.disabled = true;
      startDemoBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Executing Engine...`;
      demoTerminal.innerHTML = '';
      demoProgressBar.style.width = '0%';

      scanSteps.forEach((step, index) => {
        setTimeout(() => {
          const line = document.createElement('div');
          line.className = 'cli-line-item';
          if (step.text.includes('[OK]') || step.text.includes('[DONE]')) {
            line.style.color = '#34d399';
            line.style.fontWeight = '600';
          } else if (step.text.includes('[INIT]') || step.text.includes('[MEM]')) {
            line.style.color = '#38bdf8';
          } else {
            line.style.color = '#94a3b8';
          }
          line.textContent = step.text;
          demoTerminal.appendChild(line);
          demoTerminal.scrollTop = demoTerminal.scrollHeight;

          const progressPercent = Math.min(100, Math.round(((index + 1) / scanSteps.length) * 100));
          demoProgressBar.style.width = `${progressPercent}%`;

          if (index === scanSteps.length - 1) {
            isRunning = false;
            startDemoBtn.disabled = false;
            startDemoBtn.innerHTML = `<i class="fa-solid fa-rotate"></i> Re-execute Simulation`;
            showToast('Simulation complete. 33.5 GB reclaimed!', 'fa-circle-check');
          }
        }, step.delay);
      });
    });
  }

});
