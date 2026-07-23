(() => {
  const sidebar = document.querySelector('[data-sidebar]');
  const backdrop = document.querySelector('[data-sidebar-backdrop]');
  const openButton = document.querySelector('[data-sidebar-open]');
  const closeButton = document.querySelector('[data-sidebar-close]');

  const closeSidebar = () => {
    sidebar?.classList.remove('open');
    backdrop?.classList.remove('show');
    document.body.classList.remove('menu-open');
  };
  const openSidebar = () => {
    sidebar?.classList.add('open');
    backdrop?.classList.add('show');
    document.body.classList.add('menu-open');
  };

  openButton?.addEventListener('click', openSidebar);
  closeButton?.addEventListener('click', closeSidebar);
  backdrop?.addEventListener('click', closeSidebar);
  document.querySelectorAll('.sidebar-nav a').forEach((link) => link.addEventListener('click', closeSidebar));
})();
