/**
 * @file Reveals page elements as they enter the visitor viewport.
 */
(function(){
  function onReady(callback){
    if(document.readyState !== 'loading') return callback();
    document.addEventListener('DOMContentLoaded', callback);
  }

  onReady(function(){
    const revealElements = document.querySelectorAll('.reveal');
    if(!revealElements.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2, rootMargin: '0px 0px -10% 0px' });

    revealElements.forEach(element => {
      // Respect existing inline transition delays or utility classes
      observer.observe(element);
    });
  });
})();
